"""exp_012 final -- retrain the RMSE-objective CatBoostRegressor
(rejected locally, -17.77 vs exp_007, but archived per user policy
2026-08-21: archive every overnight experiment regardless of local
outcome) on the FULL 2019-2024 train.csv. iterations=477 reuses
exp012_run_log.txt's validation best_iteration(476)+1 directly (same
seed/data/params, deterministic) -- no re-validation needed.

Saves model_type="catboost_regressor"; submission/script.py predicts via
.predict() and clips to [0,1] for that type.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import joblib
import pandas as pd

from features import CAT_COLS, DERIVED_COLS, SHRUNK_COLS, POST_SHRINKAGE_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    build_test_time_pitcher_lookup,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
SEED = 42
FINAL_ITERATIONS = 477  # exp012_run_log.txt val best_iter(476)+1

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    print(f"FINAL_ITERATIONS={FINAL_ITERATIONS}")
    print("=" * 80)
    print("1. 전체 2019-2024 데이터 + 피처 구축")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    final_priors = fit_shrinkage_priors(recent_seasons_df(train))
    train_shrunk = apply_shrinkage(train, final_priors)
    train_final = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    print()
    print("=" * 80)
    print("2. RMSE 목적함수로 전체 재학습")
    print("=" * 80)
    reg_params = dict(
        iterations=FINAL_ITERATIONS, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="RMSE", eval_metric="RMSE",
        random_seed=SEED, thread_count=-1, verbose=200,
    )
    train_pool = cb.Pool(train_final[ALL_FEATURES], train_final[TARGET].astype(float), cat_features=CAT_COLS)
    reg = cb.CatBoostRegressor(**reg_params)
    t = time.time()
    reg.fit(train_pool)
    print(f"최종 재학습 완료 :: {time.time() - t:.1f}s")

    print()
    print("=" * 80)
    print("3. 저장")
    print("=" * 80)
    os.makedirs(MODEL_DIR, exist_ok=True)

    lookup, league_fallback = build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({lookup.shape})")

    for stale in ["catboost_model_seed42.cbm", "catboost_model_seed1.cbm", "catboost_model_seed7.cbm", "lgbm_booster.txt"]:
        p = os.path.join(MODEL_DIR, stale)
        if os.path.exists(p):
            os.remove(p)
            print(f"제거: {p} (이전 실험 아티팩트 정리)")

    reg.save_model(os.path.join(MODEL_DIR, "catboost_model.cbm"))
    joblib.dump(
        {
            "model_type": "catboost_regressor",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "trackman_cols": TRACKMAN_PITCHER_ASOF_COLS,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
            "trackman_league_fallback": league_fallback,
            "trackman_shrink_k": TRACKMAN_SHRINK_K,
            "exp_id": "exp_012_rmse",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: {MODEL_DIR}/catboost_model.cbm, {MODEL_DIR}/model_meta.pkl")
    print("\n완료.")


if __name__ == "__main__":
    main()
