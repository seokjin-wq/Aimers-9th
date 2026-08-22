"""exp_021 -- shrinkage-k grid search. TRACKMAN_SHRINK_K=50 and the
pitcher/batter SHRINKAGE_SPECS k values (50/150) were set by analogy
early in the project (exp_002/exp_003/exp_007) and never independently
grid-searched the way CatBoost's own hyperparameters were in exp_009.
Quick single-model (no seed averaging, matches exp_008/009's style)
comparison on the standard 2019-2023/2024 split to see if there's cheap
room left in this axis. Baseline = exp_007/010's fixed TRACKMAN_SHRINK_K=50
with the champion's usual CatBoost config (single seed=42, no bagging,
matching exp_009's control).
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import pandas as pd

from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRINKAGE_SPECS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)
from metrics import official_score
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
SEED = 42
TRACKMAN_K_GRID = [20, 35, 50, 75, 100, 150]
PITCHER_K_GRID = [20, 35, 50, 75, 100]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
SHRUNK_COLS = [spec[3] for spec in SHRINKAGE_SPECS]
POST_SHRINKAGE_COLS = ["shrunk_pitcher_x_batter_success"]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS

CB_PARAMS = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=SEED, thread_count=-1, verbose=False,
)


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def run_one(train, tables, pitcher_mapping, trackman_k, pitcher_k, batter_k=150):
    is_val = train["season"] == 2024
    train_only = train.loc[~is_val]

    specs = [
        (col, ncol, (pitcher_k if "pitcher" in col else batter_k), out)
        for (col, ncol, _, out) in SHRINKAGE_SPECS
    ]
    priors = fit_shrinkage_priors(recent_seasons_df(train_only), specs=specs)
    train_shrunk = apply_shrinkage(train, priors, specs=specs)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=trackman_k)

    X_train = train_shrunk.loc[~is_val, ALL_FEATURES]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val = train_shrunk.loc[is_val, ALL_FEATURES]
    y_val = train_shrunk.loc[is_val, TARGET].to_numpy()

    train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
    clf = cb.CatBoostClassifier(**CB_PARAMS)
    clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    pred = clf.predict_proba(X_val)[:, 1]
    return official_score(pred, y_val)


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    print()
    print("=" * 80)
    print(f"1. TRACKMAN_SHRINK_K 그리드서치 (pitcher_k=50, batter_k=150 고정) -- {TRACKMAN_K_GRID}")
    print("=" * 80)
    best_trackman_k, best_trackman_score = None, -1
    for k in TRACKMAN_K_GRID:
        t = time.time()
        brier, score = run_one(train, tables, pitcher_mapping, trackman_k=k, pitcher_k=50)
        marker = ""
        if score > best_trackman_score:
            best_trackman_score, best_trackman_k = score, k
            marker = "  <- 현재 최선"
        print(f"[trackman_k={k}] Brier={brier:.6f} score={score:.2f} ({time.time()-t:.1f}s){marker}")
    print(f"\n선택된 trackman_k={best_trackman_k} (score={best_trackman_score:.2f})")

    print()
    print("=" * 80)
    print(f"2. pitcher SHRINKAGE k 그리드서치 (trackman_k={best_trackman_k} 고정, batter_k=150 고정) -- {PITCHER_K_GRID}")
    print("=" * 80)
    best_pitcher_k, best_pitcher_score = None, -1
    for k in PITCHER_K_GRID:
        t = time.time()
        brier, score = run_one(train, tables, pitcher_mapping, trackman_k=best_trackman_k, pitcher_k=k)
        marker = ""
        if score > best_pitcher_score:
            best_pitcher_score, best_pitcher_k = score, k
            marker = "  <- 현재 최선"
        print(f"[pitcher_k={k}] Brier={brier:.6f} score={score:.2f} ({time.time()-t:.1f}s){marker}")
    print(f"\n선택된 pitcher_k={best_pitcher_k} (score={best_pitcher_score:.2f})")

    print()
    print("=" * 80)
    print("요약 (기준: 현재 챔피언 설정 trackman_k=50, pitcher_k=50 -- exp_007/exp_010과 동일)")
    print("=" * 80)
    print(f"baseline(trackman_k=50, pitcher_k=50) 대비 최선 조합: trackman_k={best_trackman_k}, pitcher_k={best_pitcher_k}, score={best_pitcher_score:.2f}")

    print("\n완료.")


if __name__ == "__main__":
    main()
