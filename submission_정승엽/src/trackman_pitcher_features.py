"""Phase 3-A — pitcher-level as-of Trackman physical-intensity features.

Uses the Phase 2 row-level identity mapping
(`reports/trackman_id_mapping/tables/pitcher_mapping.csv`, v3: 778/792
train pitchers at high/medium confidence, 99.67% independently-validated
precision) to attach each pitcher's own cumulative Trackman pitch
"intensity" (release speed, spin rate, movement, extension) as of before
each row -- the angle exp_005 explicitly flagged as untried ("비율이
아니라 강도(intensity)는 여전히 미검증 각도다",
`reports/eda_trackman/README.md` §9-4), as opposed to exp_005's rejected
league-wide season+month pitch-mix *rates* (`src/trackman_features.py`).

Leak safety: for each (pitcher_trackman_id, ym) bucket (ym = season*100 +
game_month), only Trackman rows strictly *before* that bucket are
averaged -- same cumulative-cutoff design as
`trackman_features._asof_table`, generalized with `pandas.merge_asof`
(backward) instead of an exact ym-equality merge, so a pitcher's gap
months (no Trackman rows that particular month) don't wrongly collapse
straight to the global fallback -- merge_asof correctly carries forward
their latest actual cumulative bucket instead.

season 2025 (the real hidden test season, with zero Trackman rows) is
handled by appending one synthetic "as of season start" sentinel row per
pitcher at ym=202501 holding their TRUE full 2019-2024 total (not a
"cumulative-before" partial). Since every real Trackman ym is <= 202412 <
202501, and every test row's ym is >= 202501, `merge_asof(..., by=pitcher,
direction="backward")` always resolves 2025 rows to this sentinel --
i.e. exactly "full pre-2025 history", automatically, no special-casing
needed. This mirrors the same convenient property already documented and
relied on in `trackman_features.py`.

Regularization (exp_005's other next-hypothesis: shrink rather than feed
raw values): `shrunk = (n*raw + k*league_fallback) / (n+k)`, same
empirical-Bayes formula as `features.apply_shrinkage`, but the fallback
here is a fixed unconditional 2019-2024 Trackman mean, not
target-derived, so (unlike `features.SHRINKAGE_SPECS`) it never
references `control_success` and needs no train-only refit per split --
matches `trackman_features.py`'s existing precedent for why a single
fallback table built once is safe to reuse across validation and the
final full retrain.
"""

import numpy as np
import pandas as pd

PHYSICAL_COLS = [
    "rel_speed",
    "spin_rate",
    "induced_vert_break",
    "horz_break",
    "extension",
]
# exp_008 tried adding rel_height/rel_side/zone_speed here (8 cols
# total) and it scored *below* exp_007's original 5 (724.19/702.65 vs
# 740.86 at k=50/100 -- see experiments/exp_008_trackman_extended_physical.md).
# Reverted; kept at exp_007's 5 columns.

TRACKMAN_PITCHER_ASOF_COLS = [f"trackman_{c}_asof" for c in PHYSICAL_COLS]

SEASON_2025_SENTINEL_YM = 202501


def load_pitcher_mapping(path="reports/trackman_id_mapping/tables/pitcher_mapping.csv", confidences=("high", "medium")):
    pm = pd.read_csv(path, encoding="utf-8-sig")
    return pm[pm["confidence"].isin(confidences)][["pitcher_id", "matched_pitcher_trackman_id"]]


def build_pitcher_physical_asof_tables(trackman_clean):
    """One as-of table per PHYSICAL_COLS entry. Returns
    {col: {"table": DataFrame(pitcher_trackman_id, ym, cum_n, asof_mean),
           "league_fallback": float}}.
    `trackman_clean` must have `is_illegal_count` (Phase 1) -- those ~97
    rows are excluded here (no train counterpart was ever found for them
    in Phase 2, so they shouldn't pollute a pitcher's physical profile).
    """
    tm = trackman_clean.loc[~trackman_clean["is_illegal_count"]].copy()
    tm["ym"] = tm["season"] * 100 + tm["game_month"]

    tables = {}
    for col in PHYSICAL_COLS:
        frame = tm.dropna(subset=[col])
        g = (
            frame.groupby(["pitcher_trackman_id", "ym"])[col]
            .agg(n="size", s="sum")
            .reset_index()
            .sort_values(["pitcher_trackman_id", "ym"])
        )
        g["cum_n"] = g.groupby("pitcher_trackman_id")["n"].cumsum() - g["n"]
        g["cum_s"] = g.groupby("pitcher_trackman_id")["s"].cumsum() - g["s"]
        g["asof_mean"] = g["cum_s"] / g["cum_n"]
        cum_table = g[["pitcher_trackman_id", "ym", "cum_n", "asof_mean"]]

        totals = frame.groupby("pitcher_trackman_id")[col].agg(n="size", asof_mean="mean").reset_index()
        totals = totals.rename(columns={"n": "cum_n"})
        totals["ym"] = SEASON_2025_SENTINEL_YM

        full_table = pd.concat([cum_table, totals[["pitcher_trackman_id", "ym", "cum_n", "asof_mean"]]], ignore_index=True)
        full_table = full_table.sort_values(["pitcher_trackman_id", "ym"]).reset_index(drop=True)

        tables[col] = {"table": full_table, "league_fallback": float(frame[col].mean())}
    return tables


def attach_pitcher_physical_features(df, tables, pitcher_mapping, shrink_k=100):
    """df must have `pitcher_id`, `season`, `game_month`. Returns a copy
    with `trackman_{col}_asof` added for each PHYSICAL_COLS entry.
    Unmapped pitchers (not in `pitcher_mapping`, i.e. the ~14/792 with no
    confident Phase-2 identity) fall through to the league-wide fallback
    via the shrinkage formula (n resolves to 0 for them), same as
    genuine cold-start."""
    df = df.copy()
    df["ym"] = df["season"] * 100 + df["game_month"]
    pid_to_tmid = pitcher_mapping.set_index("pitcher_id")["matched_pitcher_trackman_id"]
    df["_tmid"] = df["pitcher_id"].map(pid_to_tmid)

    df["_orig_order"] = np.arange(len(df))
    left = df[["_orig_order", "ym", "_tmid"]].copy()
    # int64 "by" key on both sides, NaN (unmapped pitcher) replaced with
    # a sentinel (-1) that never appears in any table's real
    # pitcher_trackman_id. merge_asof's cython "by" join is unreliable
    # with a float64 key in this pandas version (raises an "ambiguous
    # argument types" TypeError on the full dataset even when both sides
    # are float64) -- switching to a NaN-free int64 sentinel avoids that
    # entirely, and a sentinel that can't match anything produces the
    # same right-side-NaN result a genuine "no match" would, which is
    # exactly what should trigger the league-fallback collapse below.
    left["_tmid"] = left["_tmid"].fillna(-1).astype("int64")
    # merge_asof requires the "on" key sorted globally, "by" need not be.
    left_sorted = left.sort_values("ym")

    for col in PHYSICAL_COLS:
        table = tables[col]["table"].copy()
        table = table.rename(columns={"pitcher_trackman_id": "_tmid"}).sort_values("ym")
        league_fb = tables[col]["league_fallback"]

        merged = pd.merge_asof(
            left_sorted,
            table,
            on="ym",
            by="_tmid",
            direction="backward",
        )
        merged = merged.sort_values("_orig_order")

        n = merged["cum_n"].fillna(0.0).to_numpy()
        raw = merged["asof_mean"].fillna(0.0).to_numpy()
        shrunk = (n * raw + shrink_k * league_fb) / (n + shrink_k)
        df[f"trackman_{col}_asof"] = shrunk

    df = df.drop(columns=["ym", "_tmid", "_orig_order"])
    return df


def build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k):
    """Flat `pitcher_id -> trackman_*_asof` lookup for submission-time
    inference, where every row is season 2025 by construction. Every
    2025 row resolves to the SEASON_2025_SENTINEL_YM "full pre-2025
    history" bucket regardless of its actual game_month (no real
    Trackman ym is ever >= 202501), so a single probe row per mapped
    pitcher at (season=2025, game_month=1) is sufficient -- avoids
    shipping the full as-of table (14k+ rows per column) or the
    `merge_asof` machinery inside the submission zip; a small flat CSV
    plus the league-fallback constants (for pitcher_ids absent from the
    lookup entirely, e.g. any 2025 debutant not in the training data at
    all) is all `submission/script.py` needs at inference time.
    """
    probe = pitcher_mapping[["pitcher_id"]].copy()
    probe["season"] = 2025
    probe["game_month"] = 1
    lookup = attach_pitcher_physical_features(probe, tables, pitcher_mapping, shrink_k=shrink_k)
    lookup = lookup[["pitcher_id"] + TRACKMAN_PITCHER_ASOF_COLS].reset_index(drop=True)
    league_fallback = {f"trackman_{col}_asof": tables[col]["league_fallback"] for col in PHYSICAL_COLS}
    return lookup, league_fallback
