"""exp_014 final -- retrain the 94-feature (89 champion + 5 trackman
as-of STD "consistency") CatBoost model on the FULL 2019-2024 train.csv.
Rejected locally (-15.83 vs exp_007) but archived per user policy
2026-08-21. iterations=589 reuses exp014_run_log.txt's val
best_iteration(588)+1 directly (deterministic, same seed/data/params).

model_type stays "catboost" -- the only difference from exp_007/010 is a
wider trackman_cols list (10 instead of 5) and a wider lookup CSV;
submission/script.py's existing attach_trackman_features loop already
handles an arbitrary trackman_cols list generically, so no script.py
change is needed for this one.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import joblib
import numpy as np
import pandas as pd

from features import CAT_COLS, DERIVED_COLS, SHRUNK_COLS, POST_SHRINKAGE_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from trackman_pitcher_features import (
    PHYSICAL_COLS,
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    build_test_time_pitcher_lookup,
    load_pitcher_mapping,
)
from train_exp014_trackman_consistency import (
    STD_COLS,
    STD_SHRINK_K,
    build_std_asof_tables,
    attach_std_features,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
SEED = 42
FINAL_ITERATIONS = 589  # exp014_run_log.txt val best_iter(588)+1

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS + STD_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def build_test_time_std_lookup(tables_std, pitcher_mapping, shrink_k):
    """Analogous to trackman_pitcher_features.build_test_time_pitcher_lookup
    but for the std tables -- a single season=2025/game_month=1 probe row
    per mapped pitcher resolves (via merge_asof backward) to the
    SEASON_2025_SENTINEL_YM "full 2019-2024 std" bucket, same trick."""
    probe = pitcher_mapping[["pitcher_id"]].copy()
    probe["season"] = 2025
    probe["game_month"] = 1
    lookup = attach_std_features(probe, tables_std, pitcher_mapping, shrink_k=shrink_k)
    lookup = lookup[["pitcher_id"] + STD_COLS].reset_index(drop=True)
    league_fallback = {f"trackman_{c}_std_asof": tables_std[c]["league_fallback"] for c in PHYSICAL_COLS}
    return lookup, league_fallback


def main():
    print(f"FINAL_ITERATIONS={FINAL_ITERATIONS}")
    print("=" * 80)
    print("1. 전체 2019-2024 데이터 + 피처 구축 (mean+std asof 10개, 94피처)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables_mean = build_pitcher_physical_asof_tables(trackman_clean)
    tables_std = build_std_asof_tables(trackman_clean)

    final_priors = fit_shrinkage_priors(recent_seasons_df(train))
    train_shrunk = apply_shrinkage(train, final_priors)
    train_final = attach_pitcher_physical_features(train_shrunk, tables_mean, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    train_final = attach_std_features(train_final, tables_std, pitcher_mapping, shrink_k=STD_SHRINK_K)

    print()
    print("=" * 80)
    print("2. CatBoost 전체 재학습")
    print("=" * 80)
    cb_params = dict(
        iterations=FINAL_ITERATIONS, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=SEED, thread_count=-1, verbose=200,
    )
    train_pool = cb.Pool(train_final[ALL_FEATURES], train_final[TARGET], cat_features=CAT_COLS)
    clf = cb.CatBoostClassifier(**cb_params)
    t = time.time()
    clf.fit(train_pool)
    print(f"최종 재학습 완료 :: {time.time() - t:.1f}s")

    print()
    print("=" * 80)
    print("3. 저장 (mean+std 결합 lookup)")
    print("=" * 80)
    os.makedirs(MODEL_DIR, exist_ok=True)

    mean_lookup, mean_fallback = build_test_time_pitcher_lookup(tables_mean, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    std_lookup, std_fallback = build_test_time_std_lookup(tables_std, pitcher_mapping, shrink_k=STD_SHRINK_K)
    combined_lookup = mean_lookup.merge(std_lookup, on="pitcher_id", how="outer")
    combined_fallback = {**mean_fallback, **std_fallback}
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    combined_lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({combined_lookup.shape}, 컬럼={list(combined_lookup.columns)})")

    for stale in ["catboost_model_seed42.cbm", "catboost_model_seed1.cbm", "catboost_model_seed7.cbm", "lgbm_booster.txt"]:
        p = os.path.join(MODEL_DIR, stale)
        if os.path.exists(p):
            os.remove(p)
            print(f"제거: {p} (이전 실험 아티팩트 정리)")

    clf.save_model(os.path.join(MODEL_DIR, "catboost_model.cbm"))
    joblib.dump(
        {
            "model_type": "catboost",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "trackman_cols": TRACKMAN_PITCHER_ASOF_COLS + STD_COLS,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
            "trackman_league_fallback": combined_fallback,
            "trackman_shrink_k": TRACKMAN_SHRINK_K,
            "exp_id": "exp_014_trackman_consistency",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: {MODEL_DIR}/catboost_model.cbm, {MODEL_DIR}/model_meta.pkl")
    print("\n완료.")


if __name__ == "__main__":
    main()
