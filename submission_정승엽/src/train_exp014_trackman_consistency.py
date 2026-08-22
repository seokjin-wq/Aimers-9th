"""exp_014 -- add pitcher-level as-of trackman CONSISTENCY (std, not just
mean) for the champion 5 physical columns, on top of exp_007's as-of
means. exp_007 only used cumulative MEAN release speed/spin/movement/
extension ("how hard does this pitcher usually throw"); this experiment
adds cumulative STD of those same 5 columns ("how consistent is this
pitcher's stuff pitch-to-pitch") as an additional signal source --
control_success is about hitting a target location, and a pitcher whose
release/movement is more consistent plausibly has better command even at
the same average intensity. This is a genuinely new feature category
(dispersion, not central tendency), unlike exp_008 (more columns of the
SAME kind of feature -- mean of more physical quantities -- which was
rejected for adding noise).

Leak safety: same cumulative-before-this-bucket as-of design as
`trackman_pitcher_features.py` (Phase 3-A), computed independently here
(self-contained, does not modify the shared champion module) via
E[X^2] - E[X]^2 accumulated the same way the champion module accumulates
sum for the mean.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import numpy as np
import pandas as pd

from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRUNK_COLS,
    POST_SHRINKAGE_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)
from metrics import official_score
from trackman_pitcher_features import (
    PHYSICAL_COLS,
    TRACKMAN_PITCHER_ASOF_COLS,
    SEASON_2025_SENTINEL_YM,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
STD_SHRINK_K = 50
SEED = 42

STD_COLS = [f"trackman_{c}_std_asof" for c in PHYSICAL_COLS]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
CHAMPION_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS
EXTENDED_FEATURE_SET = CHAMPION_FEATURE_SET + STD_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def build_std_asof_tables(trackman_clean):
    """Same cumulative-before-bucket design as
    trackman_pitcher_features.build_pitcher_physical_asof_tables, but
    accumulates sum-of-squares too so std can be derived as-of each
    (pitcher, ym) bucket: var = E[X^2] - E[X]^2 (population, over all
    prior pitches)."""
    tm = trackman_clean.loc[~trackman_clean["is_illegal_count"]].copy()
    tm["ym"] = tm["season"] * 100 + tm["game_month"]

    tables = {}
    for col in PHYSICAL_COLS:
        frame = tm.dropna(subset=[col])
        g = (
            frame.assign(_sq=frame[col] ** 2)
            .groupby(["pitcher_trackman_id", "ym"])
            .agg(n=(col, "size"), s=(col, "sum"), sq=("_sq", "sum"))
            .reset_index()
            .sort_values(["pitcher_trackman_id", "ym"])
        )
        g["cum_n"] = g.groupby("pitcher_trackman_id")["n"].cumsum() - g["n"]
        g["cum_s"] = g.groupby("pitcher_trackman_id")["s"].cumsum() - g["s"]
        g["cum_sq"] = g.groupby("pitcher_trackman_id")["sq"].cumsum() - g["sq"]
        mean = g["cum_s"] / g["cum_n"]
        var = (g["cum_sq"] / g["cum_n"]) - mean**2
        g["asof_std"] = np.sqrt(np.clip(var, 0.0, None))
        cum_table = g[["pitcher_trackman_id", "ym", "cum_n", "asof_std"]]

        totals = frame.groupby("pitcher_trackman_id")[col].agg(n="size", asof_std="std").reset_index()
        totals = totals.rename(columns={"n": "cum_n"})
        totals["asof_std"] = totals["asof_std"].fillna(0.0)
        totals["ym"] = SEASON_2025_SENTINEL_YM

        full_table = pd.concat([cum_table, totals[["pitcher_trackman_id", "ym", "cum_n", "asof_std"]]], ignore_index=True)
        full_table = full_table.sort_values(["pitcher_trackman_id", "ym"]).reset_index(drop=True)

        tables[col] = {"table": full_table, "league_fallback": float(frame[col].std())}
    return tables


def attach_std_features(df, tables, pitcher_mapping, shrink_k=STD_SHRINK_K):
    df = df.copy()
    df["ym"] = df["season"] * 100 + df["game_month"]
    pid_to_tmid = pitcher_mapping.set_index("pitcher_id")["matched_pitcher_trackman_id"]
    df["_tmid"] = df["pitcher_id"].map(pid_to_tmid)
    df["_orig_order"] = np.arange(len(df))
    left = df[["_orig_order", "ym", "_tmid"]].copy()
    left["_tmid"] = left["_tmid"].fillna(-1).astype("int64")
    left_sorted = left.sort_values("ym")

    for col in PHYSICAL_COLS:
        table = tables[col]["table"].copy()
        table = table.rename(columns={"pitcher_trackman_id": "_tmid"}).sort_values("ym")
        league_fb = tables[col]["league_fallback"]

        merged = pd.merge_asof(left_sorted, table, on="ym", by="_tmid", direction="backward")
        merged = merged.sort_values("_orig_order")

        n = merged["cum_n"].fillna(0.0).to_numpy()
        raw = merged["asof_std"].fillna(0.0).to_numpy()
        shrunk = (n * raw + shrink_k * league_fb) / (n + shrink_k)
        df[f"trackman_{col}_std_asof"] = shrunk

    df = df.drop(columns=["ym", "_tmid", "_orig_order"])
    return df


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축 (exp_007 챔피언 + 신규 std 피처 5개)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables_mean = build_pitcher_physical_asof_tables(trackman_clean)
    tables_std = build_std_asof_tables(trackman_clean)

    is_val = train["season"] == 2024
    train_only = train.loc[~is_val]
    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, val_priors_recent)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables_mean, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    train_shrunk = attach_std_features(train_shrunk, tables_std, pitcher_mapping, shrink_k=STD_SHRINK_K)

    X_train_champ = train_shrunk.loc[~is_val, CHAMPION_FEATURE_SET]
    X_val_champ = train_shrunk.loc[is_val, CHAMPION_FEATURE_SET]
    X_train_ext = train_shrunk.loc[~is_val, EXTENDED_FEATURE_SET]
    X_val_ext = train_shrunk.loc[is_val, EXTENDED_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    y_val = train_shrunk.loc[is_val, TARGET]
    print(f"champion features={len(CHAMPION_FEATURE_SET)}, extended features={len(EXTENDED_FEATURE_SET)}")
    print(f"신규 std 피처 통계:\n{train_shrunk.loc[~is_val, STD_COLS].describe()}")

    cb_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=SEED, thread_count=-1, verbose=False,
    )

    print()
    print("=" * 80)
    print("1. 챔피언 재현 (mean asof 5개만, exp_007)")
    print("=" * 80)
    t = time.time()
    train_pool = cb.Pool(X_train_champ, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val_champ, y_val, cat_features=CAT_COLS)
    clf_champ = cb.CatBoostClassifier(**cb_params)
    clf_champ.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    pred_champ = clf_champ.predict_proba(X_val_champ)[:, 1]
    brier_champ, score_champ = official_score(pred_champ, y_val)
    print(f"[챔피언(mean만)] Brier={brier_champ:.6f} | score={score_champ:.2f} | best_iter={clf_champ.get_best_iteration()} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("2. mean + std asof 10개 (신규)")
    print("=" * 80)
    t = time.time()
    train_pool_ext = cb.Pool(X_train_ext, y_train, cat_features=CAT_COLS)
    val_pool_ext = cb.Pool(X_val_ext, y_val, cat_features=CAT_COLS)
    clf_ext = cb.CatBoostClassifier(**cb_params)
    clf_ext.fit(train_pool_ext, eval_set=val_pool_ext, early_stopping_rounds=100)
    pred_ext = clf_ext.predict_proba(X_val_ext)[:, 1]
    brier_ext, score_ext = official_score(pred_ext, y_val)
    print(f"[mean+std] Brier={brier_ext:.6f} | score={score_ext:.2f} | best_iter={clf_ext.get_best_iteration()} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("요약")
    print("=" * 80)
    print(f"챔피언(mean만): score={score_champ:.2f}")
    print(f"mean+std:      score={score_ext:.2f} | Δ={score_ext-score_champ:+.2f}")
    if score_ext > score_champ:
        importances = sorted(zip(EXTENDED_FEATURE_SET, clf_ext.get_feature_importance()), key=lambda x: -x[1])
        std_ranks = [(i + 1, name) for i, (name, _) in enumerate(importances) if name in STD_COLS]
        print(f"신규 std 피처 importance 순위(89개 중): {std_ranks}")
    print("\n완료.")


if __name__ == "__main__":
    main()
