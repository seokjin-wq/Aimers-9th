"""exp_024 -- trend-extrapolated pitcher-level Trackman physical features.

Motivation (user hypothesis): `trackman_pitcher_features.py`'s season-2025
sentinel is a flat all-history mean (2019-2024) of each pitcher's
rel_speed/spin_rate/induced_vert_break/horz_break/extension, carried
forward unchanged into every 2025 row. If a pitcher's true physical
profile is drifting season over season (e.g. velocity decline with age,
or the opposite for a young pitcher still developing), a flat historical
mean is a biased estimate of the *next* season's value -- the same
season-drift argument that motivated exp_022/023's label-side
prior-shift recalibration, just applied to the trackman feature values
themselves instead of the base rate.

This module builds an alternative sentinel: per pitcher, fit a linear
trend across that pitcher's own SEASON-LEVEL means (not ym-level) for
all seasons strictly before `target_season`, extrapolate one step to
`target_season`, and clip to that column's [1st, 99th] percentile range
(guards against wild extrapolation from a short/noisy trend). Falls back
to the flat cumulative mean (identical to
`trackman_pitcher_features.py`'s existing behavior) whenever a pitcher
has fewer than `min_seasons_for_trend` distinct prior seasons with data
-- a 1-2 point "trend" is not a trend, it's noise.

Fairness note for backtesting (important, see
`train_exp024_trend_trackman.py`): real 2025 inference will have ZERO
Trackman rows for 2025 itself, so the sentinel is the ONLY signal 2025
rows get. But `trackman_clean.csv` DOES contain real season-2024 rows,
so a naive local validation on season 2024 (train on 2019-2023, validate
on 2024) would let 2024 validation rows resolve to genuine within-season
2024 Trackman history via the interior cumulative-before-ym table
(`trackman_pitcher_features.build_pitcher_physical_asof_tables`'s
`cum_table`) instead of ever touching the sentinel at all -- that is NOT
representative of what 2025 inference will actually see, and silently
overstates how good ANY sentinel method (flat or trend) looks locally.
This module's caller is responsible for excluding the target season's
own rows from `trackman_clean` before calling here, so the sentinel is
actually exercised in the backtest exactly as it will be in production.
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
TRACKMAN_PITCHER_ASOF_COLS = [f"trackman_{c}_asof" for c in PHYSICAL_COLS]


def _linear_extrapolate(seasons, values, target_season):
    x = np.asarray(seasons, dtype=float)
    y = np.asarray(values, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    return slope * target_season + intercept


def build_pitcher_physical_asof_tables_trend(
    trackman_clean, target_season, min_seasons_for_trend=3, clip_quantiles=(0.01, 0.99)
):
    """Same return shape as
    `trackman_pitcher_features.build_pitcher_physical_asof_tables`
    ({col: {"table": DataFrame, "league_fallback": float}}), except the
    single terminal sentinel row per pitcher (ym = target_season*100+1)
    is a trend extrapolation instead of a flat all-history mean.

    `trackman_clean` should already be restricted by the caller to rows
    with `season < target_season` for a fair backtest (see module
    docstring); this function does not filter by season itself so it can
    also be called with the FULL 2019-2024 history at real submission
    time (target_season=2025), where every real row is already < 2025.
    """
    tm = trackman_clean.loc[~trackman_clean["is_illegal_count"]].copy()
    tm["ym"] = tm["season"] * 100 + tm["game_month"]

    tables = {}
    n_trend, n_fallback = 0, 0
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

        league_fallback = float(frame[col].mean())
        lo, hi = frame[col].quantile(list(clip_quantiles))

        season_stats = frame.groupby(["pitcher_trackman_id", "season"])[col].mean().reset_index()
        flat_totals = frame.groupby("pitcher_trackman_id")[col].agg(n="size", mean="mean")

        totals_rows = []
        for tmid, sub in season_stats.groupby("pitcher_trackman_id"):
            total_n = int(flat_totals.loc[tmid, "n"])
            flat_mean = float(flat_totals.loc[tmid, "mean"])
            n_seasons = sub["season"].nunique()
            if n_seasons >= min_seasons_for_trend:
                pred = _linear_extrapolate(sub["season"].to_numpy(), sub[col].to_numpy(), target_season)
                pred = float(np.clip(pred, lo, hi))
                n_trend += 1
            else:
                pred = flat_mean
                n_fallback += 1
            totals_rows.append((tmid, target_season * 100 + 1, total_n, pred))
        totals = pd.DataFrame(totals_rows, columns=["pitcher_trackman_id", "ym", "cum_n", "asof_mean"])

        full_table = (
            pd.concat([cum_table, totals], ignore_index=True)
            .sort_values(["pitcher_trackman_id", "ym"])
            .reset_index(drop=True)
        )
        tables[col] = {"table": full_table, "league_fallback": league_fallback}

    print(
        f"[trend sentinel] target_season={target_season}: "
        f"{n_trend // len(PHYSICAL_COLS)} pitchers trend-extrapolated "
        f"(>= {min_seasons_for_trend} prior seasons), "
        f"{n_fallback // len(PHYSICAL_COLS)} pitchers fell back to flat mean"
    )
    return tables
