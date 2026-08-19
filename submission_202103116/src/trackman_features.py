"""Trackman-derived as-of `(season, game_month)` cumulative features.

Background: `data/trackman_history.csv` has **no shared key** with
train/test (`pitcher_id`/`pitcher_trackman_id`, `pitcher_team_id`/
`pitcher_team` overlap 0 values — verified in
`reports/eda_trackman/README.md` §D). The only usable join axes are
columns that exist on *both* sides: `season`, `game_month`, and
row-local flags already computed by `features.build_features`
(`same_hand_matchup`, `three_ball`).

Leakage safety: every value attached to a train/test row must use only
`trackman_history.csv` rows strictly *before* that row's own
`(season, game_month)` — this is the as-of design from
`reports/eda_trackman/README.md` §E ("빼기 전에 검증부터" cousin: no
season-block carve-out, an actual monthly cumulative cutoff). Concretely,
for a row with `season=Y, game_month=M`, only trackman rows with
`season < Y` or (`season == Y and game_month < M`) are used.

Consequences of this design (see the README for the numbers):
- Season 2025 (the real hidden evaluation season, entirely absent from
  trackman_history.csv) always satisfies `season < Y` for every trackman
  row that exists, so it automatically resolves to the "full 2019-2024
  history" value — no special-casing needed for the evaluation season.
- The only cold-start bucket with near-zero cumulative sample size is
  2019-03 (the very first month in trackman_history.csv) — 0.908% of
  train rows. It's handled with a single fallback step: fill with the
  overall (all trackman rows) mean/rate for that group, which is what a
  "no history yet" prior should be.

Unlike `features.SHRINKAGE_SPECS` (which touches `control_success` and
therefore must be refit separately per train/validation split to avoid
target leakage), these features never reference `control_success` at
all — they're pure external physical-pitch data. The as-of cutoff alone
is sufficient leakage protection, so a single set of tables (built once
from the full trackman_history.csv) is reused unchanged for both the
held-out validation run and the final full retrain.

**Status: not currently used by any active training script.** exp_005
built the 4 features in TRACKMAN_DERIVED_COLS on top of exp_003 and
found every combination scored below exp_003's 723.17 (full bundle
703.21, either half tested alone -10 to -17 below baseline too — see
experiments/exp_005_trackman.md). The leak-safety mechanism itself
(the as-of cumulative join below) wasn't the problem — it's kept here
as tested, reusable infrastructure in case a future experiment wants to
build *different* trackman-derived features on the same join axes
(`season`+`game_month`, `same_hand_matchup`, `three_ball`).
"""

import numpy as np
import pandas as pd

TRACKMAN_DERIVED_COLS = [
    "trackman_same_hand_breaking_rate_asof",
    "trackman_three_ball_fastball_rate_asof",
    "trackman_three_ball_rel_speed_asof",
    "trackman_league_breaking_rate_asof",
]

# (output col, group_col or None, value expression name)
_SPECS = [
    ("trackman_same_hand_breaking_rate_asof", "same_hand_matchup", "is_breaking"),
    ("trackman_three_ball_fastball_rate_asof", "three_ball", "is_fastball"),
    ("trackman_three_ball_rel_speed_asof", "three_ball", "rel_speed"),
    ("trackman_league_breaking_rate_asof", None, "is_breaking"),
]


def _prep_trackman(trackman_df):
    """Row-local cleanup + the two join-key columns, mirroring
    features.build_features's naming so merges are a plain column match.

    reports/eda_trackman/README.md §A: drop the ~97 rows outside the
    legal balls/strikes/outs range (data-entry errors, 0.005% of rows).
    """
    tm = trackman_df.copy()
    legal = (
        tm["balls_before"].between(0, 3)
        & tm["strikes_before"].between(0, 2)
        & tm["outs_before"].between(0, 2)
    )
    tm = tm.loc[legal].copy()

    tm["ym"] = tm["season"] * 100 + tm["game_month"]
    tm["same_hand_matchup"] = (tm["pitcher_hand"] == tm["batter_hand"]).astype(int)
    tm["three_ball"] = (tm["balls_before"] == 3).astype(int)
    tm["is_breaking"] = (tm["pitch_type_group"] == "breaking").astype(int)
    tm["is_fastball"] = (tm["pitch_type_group"] == "fastball").astype(int)
    return tm


def _asof_table(tm, group_col, value_col):
    """Cumulative (as-of) mean of value_col, strictly before each
    (group_col?, ym) bucket's own month. group_col=None -> one global
    series per ym (league-wide, no further split)."""
    frame = tm.dropna(subset=[value_col])
    keys = ([group_col] if group_col else []) + ["ym"]
    g = frame.groupby(keys)[value_col].agg(n="size", s="sum").reset_index()
    g = g.sort_values(keys)

    cum_keys = [group_col] if group_col else None
    if cum_keys:
        g["cum_n"] = g.groupby(cum_keys)["n"].cumsum() - g["n"]
        g["cum_s"] = g.groupby(cum_keys)["s"].cumsum() - g["s"]
    else:
        g["cum_n"] = g["n"].cumsum() - g["n"]
        g["cum_s"] = g["s"].cumsum() - g["s"]
    g["asof_value"] = g["cum_s"] / g["cum_n"]

    if group_col:
        fallback = frame.groupby(group_col)[value_col].mean()
    else:
        fallback = frame[value_col].mean()
    return g[keys + ["asof_value"]], fallback


def build_trackman_asof_tables(trackman_df):
    """Build the lookup tables for all TRACKMAN_DERIVED_COLS.

    Returns a dict {output_col: (table_df, fallback)} to pass into
    `attach_trackman_features`. Build once from the full
    trackman_history.csv (2019-2024) — reused as-is for both the
    validation split and the final retrain (see module docstring for why
    that's safe here, unlike the target-derived shrinkage priors).
    """
    tm = _prep_trackman(trackman_df)
    tables = {}
    for out_col, group_col, value_col in _SPECS:
        tables[out_col] = _asof_table(tm, group_col, value_col)
    return tables


def attach_trackman_features(df, tables):
    """Merge the as-of trackman features onto df.

    df must already have `season`, `game_month`, `same_hand_matchup`,
    `three_ball` (i.e. call after features.build_features). Rows whose
    `(season, game_month)` isn't in the table (season >= 2025, or the
    2019-03 cold-start bucket where the cumulative window is empty) get
    the group's overall historical fallback value — see module docstring.
    """
    df = df.copy()
    df["ym"] = df["season"] * 100 + df["game_month"]

    for out_col, group_col, _value_col in _SPECS:
        table, fallback = tables[out_col]
        keys = ([group_col] if group_col else []) + ["ym"]
        merged = df.merge(table, on=keys, how="left")
        if group_col:
            fb = merged[group_col].map(fallback)
        else:
            fb = fallback
        df[out_col] = merged["asof_value"].fillna(fb).values

    df = df.drop(columns=["ym"])
    return df
