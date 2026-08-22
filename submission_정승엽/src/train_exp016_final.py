"""exp_016 final -- retrain the free 5-way weighted seed blend's winning
subset (seed42=0.39, seed1=0.58, seed7=0.03, from exp016_run_log.txt;
the other two seeds got weight 0 and are dropped) on the FULL 2019-2024
train.csv. Iteration counts reused directly (deterministic, same seed/
data/params): seed42->696, seed1->632 (exp010_run_log.txt), seed7->635
(exp010_run_log.txt's original 5-seed comparison also logged best_iter
for seed7=634).

Saves model_type="catboost_seedbag" with the new "seed_weights" field
(submission/script.py already supports weighted averaging there when
present, falling back to uniform mean when absent -- exp_010's archive
is untouched by this).
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
SEED_ITERS = {42: 696, 1: 632, 7: 635}
SEED_WEIGHTS = {42: 0.39, 1: 0.58, 7: 0.03}

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    print(f"SEED_WEIGHTS={SEED_WEIGHTS}")
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

    train_pool = cb.Pool(train_final[ALL_FEATURES], train_final[TARGET], cat_features=CAT_COLS)

    print()
    print("=" * 80)
    print("2. 시드별 전체 재학습")
    print("=" * 80)
    os.makedirs(MODEL_DIR, exist_ok=True)
    seed_model_files = []
    seed_weights_ordered = []
    for seed, iters in SEED_ITERS.items():
        cb_params = dict(
            iterations=iters, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=seed, thread_count=-1, verbose=200,
        )
        clf = cb.CatBoostClassifier(**cb_params)
        t = time.time()
        clf.fit(train_pool)
        print(f"[seed={seed}] 완료 :: {time.time() - t:.1f}s")
        fname = f"catboost_model_seed{seed}.cbm"
        clf.save_model(os.path.join(MODEL_DIR, fname))
        seed_model_files.append(fname)
        seed_weights_ordered.append(SEED_WEIGHTS[seed])

    print()
    print("=" * 80)
    print("3. 저장")
    print("=" * 80)
    lookup, league_fallback = build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({lookup.shape})")

    for stale in ["catboost_model.cbm", "lgbm_booster.txt"]:
        p = os.path.join(MODEL_DIR, stale)
        if os.path.exists(p):
            os.remove(p)
            print(f"제거: {p} (이전 실험 아티팩트 정리)")

    joblib.dump(
        {
            "model_type": "catboost_seedbag",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "trackman_cols": TRACKMAN_PITCHER_ASOF_COLS,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
            "trackman_league_fallback": league_fallback,
            "trackman_shrink_k": TRACKMAN_SHRINK_K,
            "seed_model_files": seed_model_files,
            "seed_weights": seed_weights_ordered,
            "exp_id": "exp_016_weighted_seedblend",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: model_meta.pkl (seed_model_files={seed_model_files}, seed_weights={seed_weights_ordered})")
    print("\n완료.")


if __name__ == "__main__":
    main()
