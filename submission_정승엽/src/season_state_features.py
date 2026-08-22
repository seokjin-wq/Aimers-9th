"""exp_027 -- current-season-only as-of pitcher/batter stats.

Ported from a teammate's independently-built pipeline
(github.com/seokjin-wq/Aimers-9th, experiment_workspace EXP_056), which
reported this as by far the single largest feature-engineering gain in
their 130-experiment search (Brier delta -0.000221, larger than every
other technique in their history combined -- see
experiments/exp_027_season_state_features.md for the full comparison).

The official `asof_*` columns are CAREER-cumulative (as of before this
pitch, since the pitcher's/batter's first ever tracked pitch). Since
control_success rate falls every season (established in this project's
own exp_022/023 calibration work), a flat career average is a stale
estimate of a pitcher's CURRENT form -- this module recovers
"this-season-only" stats as an explicit feature, letting the model
learn a per-pitcher recency signal directly instead of relying only on
one global post-hoc calibration shift.

Mechanism (row-local at apply time, no cross-row/test-row dependency --
CLAUDE.md rule 6): freeze a snapshot of each pitcher's/batter's
career-cumulative (n, rate) as of the LAST row of each of their seasons,
built ONCE from official train.csv only (`build_season_baselines`, MUST
be called on train-only data, same leak-safety contract as
`features.fit_shrinkage_priors`). For any row in season S, look up the
entity's snapshot from the most recent season strictly before S
(`merge_asof` backward, `allow_exact_matches=False` so season S never
matches itself; a debut season with no prior snapshot falls back to
baseline=0, i.e. season-to-date collapses exactly to the full career
value, correct since there IS no earlier history to subtract). Subtract
that baseline from the row's own (already-supplied) cumulative n/rate to
recover this-season-only counts, then shrink toward a train-only global
prior with the same empirical-Bayes formula as `features.apply_shrinkage`.
"""

import numpy as np
import pandas as pd

PITCHER_METRICS = ["success", "reverse", "middle", "ball", "strike"]
BATTER_METRICS = ["success", "middle"]

SEASON_STATE_SHRINK_K = 20


def _entity_config(entity):
    if entity == "pitcher":
        return "pitcher_id", PITCHER_METRICS
    if entity == "batter":
        return "batter_id", BATTER_METRICS
    raise ValueError(f"unknown entity: {entity}")


def season_state_cols(entity, shrink_k=SEASON_STATE_SHRINK_K):
    _, metrics = _entity_config(entity)
    cols = [f"{entity}_season_n"]
    for m in metrics:
        cols.append(f"{entity}_season_{m}_rate_k{shrink_k}")
        cols.append(f"{entity}_season_{m}_delta_career")
    return cols


def build_season_baselines(train_full, entity):
    """One row per (entity_id, season) holding the entity's career-cumulative
    asof_n / asof_{metric}_rate as of their LAST row in that season
    (still "before that last pitch" -- a small, consistently-applied
    underestimate that never leaks). `train_full` MUST be official train
    rows only (any season range is fine: 2019-2023 for validation, or
    the full 2019-2024 for the final refit), exactly like
    `features.fit_shrinkage_priors`.
    """
    id_col, metrics = _entity_config(entity)
    n_col = f"asof_{entity}_n"
    rate_cols = [f"asof_{entity}_{m}_rate" for m in metrics]
    cols = [id_col, "season", n_col] + rate_cols

    rename = {n_col: "_baseline_n"}
    rename.update({f"asof_{entity}_{m}_rate": f"_baseline_{m}_rate" for m in metrics})

    last = (
        train_full[cols]
        .sort_values([id_col, "season"], kind="stable")
        .groupby([id_col, "season"], observed=True, sort=False)
        .tail(1)
        .rename(columns=rename)
        .reset_index(drop=True)
    )
    return last


def latest_season_baselines(train_full, entity):
    """Submission-time variant of `build_season_baselines`: one row per
    entity_id holding ONLY their single most recent season's snapshot
    (built from the full train_full, e.g. all of 2019-2024) -- small
    enough to ship as a flat lookup CSV in the submission zip. Every
    real 2025 test row has season=2025, strictly after any entity's
    latest train season, so `attach_season_state_features`'s
    merge_asof(direction="backward", allow_exact_matches=False) resolves
    every row to this single snapshot automatically -- no 2025-specific
    sentinel handling needed (unlike trackman's SEASON_2025_SENTINEL,
    because here the row's OWN asof_{entity}_n/rate columns are real,
    genuinely-updated per-row values even for 2025 test rows -- verified
    directly against data/test.csv, e.g. TEST_000001 has
    asof_pitcher_n=3465, not a frozen/absent value like Trackman -- so
    season_n = row's own current n - this fixed baseline correctly
    tracks in-progress 2025-season pitch counts row by row)."""
    full = build_season_baselines(train_full, entity)
    id_col, _ = _entity_config(entity)
    return full.sort_values("season").groupby(id_col, observed=True, sort=False).tail(1).reset_index(drop=True)


def fit_season_state_priors(train_only_df, entity):
    """Global mean of each season-rate metric's underlying asof_* column,
    computed on the training split only -- same leak-safety contract as
    `features.fit_shrinkage_priors`."""
    _, metrics = _entity_config(entity)
    return {m: float(train_only_df[f"asof_{entity}_{m}_rate"].mean()) for m in metrics}


def attach_season_state_features(df, baselines, priors, entity, shrink_k=SEASON_STATE_SHRINK_K):
    """Row-local: attach this-season-only n / shrunk-rate / delta-vs-career
    columns. `baselines` = `build_season_baselines(...)` output, `priors`
    = `fit_season_state_priors(...)` output. Safe to call on any split
    (train/val/test) once both are fit on the training split."""
    id_col, metrics = _entity_config(entity)
    n_col = f"asof_{entity}_n"

    df = df.copy()
    df["_orig_order"] = np.arange(len(df))
    left = df[["_orig_order", "season", id_col]].sort_values("season")
    baselines_sorted = baselines.sort_values("season")

    merged = pd.merge_asof(
        left, baselines_sorted, on="season", by=id_col,
        direction="backward", allow_exact_matches=False,
    ).sort_values("_orig_order")

    baseline_n = merged["_baseline_n"].fillna(0.0).to_numpy()
    current_n = df[n_col].fillna(0.0).to_numpy()
    season_n = np.clip(current_n - baseline_n, 0.0, None)
    df[f"{entity}_season_n"] = season_n

    for m in metrics:
        rate_col = f"asof_{entity}_{m}_rate"
        current_rate = df[rate_col].fillna(0.0).to_numpy()
        baseline_rate = merged[f"_baseline_{m}_rate"].fillna(0.0).to_numpy()
        current_count = current_n * current_rate
        baseline_count = baseline_n * baseline_rate
        delta_count = np.clip(current_count - baseline_count, 0.0, season_n)
        season_rate_shrunk = (delta_count + shrink_k * priors[m]) / (season_n + shrink_k)
        df[f"{entity}_season_{m}_rate_k{shrink_k}"] = season_rate_shrunk
        df[f"{entity}_season_{m}_delta_career"] = season_rate_shrunk - current_rate

    df = df.drop(columns=["_orig_order"])
    return df


def attach_season_state_features_flat(df, lookup, priors, entity, shrink_k=SEASON_STATE_SHRINK_K):
    """Submission-time variant of `attach_season_state_features`: same
    math, but `lookup` is a flat one-row-per-entity table (e.g.
    `latest_season_baselines(...)` output, shipped as a small CSV in the
    submission zip) merged with a plain `pd.merge` instead of
    `merge_asof` -- valid because every real inference row is season
    2025, strictly after any entity's latest official-train season, so
    there is only ever one applicable baseline row per entity regardless
    of the row's own season value. Avoids requiring the full
    `merge_asof`/sorted-by-season machinery inside `submission/script.py`."""
    id_col, metrics = _entity_config(entity)
    n_col = f"asof_{entity}_n"

    df = df.copy()
    merged = df[[id_col]].merge(lookup, on=id_col, how="left")

    baseline_n = merged["_baseline_n"].fillna(0.0).to_numpy()
    current_n = df[n_col].fillna(0.0).to_numpy()
    season_n = np.clip(current_n - baseline_n, 0.0, None)
    df[f"{entity}_season_n"] = season_n

    for m in metrics:
        rate_col = f"asof_{entity}_{m}_rate"
        current_rate = df[rate_col].fillna(0.0).to_numpy()
        baseline_rate = merged[f"_baseline_{m}_rate"].fillna(0.0).to_numpy()
        current_count = current_n * current_rate
        baseline_count = baseline_n * baseline_rate
        delta_count = np.clip(current_count - baseline_count, 0.0, season_n)
        season_rate_shrunk = (delta_count + shrink_k * priors[m]) / (season_n + shrink_k)
        df[f"{entity}_season_{m}_rate_k{shrink_k}"] = season_rate_shrunk
        df[f"{entity}_season_{m}_delta_career"] = season_rate_shrunk - current_rate

    return df
