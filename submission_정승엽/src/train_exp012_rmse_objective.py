"""exp_012 -- train CatBoost with an RMSE (squared-error) objective
instead of Logloss, on the exp_007 champion 89-feature set (exp_003's 84
+ 5 trackman pitcher-level as-of physical features, shrink_k=50).

Rationale: every prior experiment (exp_007/008/009/010) trained with
`loss_function="Logloss"`, which is a proper scoring rule but is NOT the
same objective as the competition metric. The official score is a
monotonic transform of plain squared-error (Brier score = mean((pred -
y)**2)) -- exactly what RMSE minimizes. Logloss penalizes confident wrong
predictions near 0/1 much more harshly than squared error does, so a
model tuned to minimize Logloss is not guaranteed to minimize Brier;
training directly against RMSE aligns the training objective with the
actual leaderboard metric. This is a large, structural, previously-untried
lever (as opposed to exp_009's hyperparameter micro-tuning within
Logloss, which was fully rejected).

CatBoostRegressor's RMSE objective is unbounded (not a probability), so
predictions must be clipped to [0, 1] before scoring -- this clipping
itself changes the effective loss surface right at the boundaries, which
is fine (it's exactly what submission/script.py already does with
np.clip for every model type).
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
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
SEED = 42

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축 (exp_007 89피처 챔피언, k=50)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    is_val = train["season"] == 2024
    train_only = train.loc[~is_val]
    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, val_priors_recent)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    X_train = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET]
    print(f"train={X_train.shape}, val={X_val.shape}, features={len(TRACKMAN_FEATURE_SET)}")

    print()
    print("=" * 80)
    print("1. baseline 재현: Logloss (exp_007과 동일)")
    print("=" * 80)
    cls_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=SEED, thread_count=-1, verbose=False,
    )
    train_pool_cls = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool_cls = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
    t = time.time()
    clf = cb.CatBoostClassifier(**cls_params)
    clf.fit(train_pool_cls, eval_set=val_pool_cls, early_stopping_rounds=100)
    pred_logloss = clf.predict_proba(X_val)[:, 1]
    brier_ll, score_ll = official_score(pred_logloss, y_val)
    print(f"[Logloss] Brier={brier_ll:.6f} | score={score_ll:.2f} | best_iter={clf.get_best_iteration()} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("2. RMSE 목적함수 (제곱오차 -- Brier score와 직접 정렬)")
    print("=" * 80)
    reg_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="RMSE", eval_metric="RMSE",
        random_seed=SEED, thread_count=-1, verbose=False,
    )
    train_pool_reg = cb.Pool(X_train, y_train.astype(float), cat_features=CAT_COLS)
    val_pool_reg = cb.Pool(X_val, y_val.astype(float), cat_features=CAT_COLS)
    t = time.time()
    reg = cb.CatBoostRegressor(**reg_params)
    reg.fit(train_pool_reg, eval_set=val_pool_reg, early_stopping_rounds=100)
    pred_rmse_raw = reg.predict(X_val)
    pred_rmse = np.clip(pred_rmse_raw, 0.0, 1.0)
    brier_rmse, score_rmse = official_score(pred_rmse, y_val)
    n_clipped = int(((pred_rmse_raw < 0) | (pred_rmse_raw > 1)).sum())
    print(f"[RMSE] Brier={brier_rmse:.6f} | score={score_rmse:.2f} | best_iter={reg.get_best_iteration()} | {time.time()-t:.1f}s | clipped={n_clipped}/{len(pred_rmse_raw)}")

    print()
    print("=" * 80)
    print("3. 두 목적함수 예측 평균 (다른 손실함수 = 다양성, 앙상블 시도)")
    print("=" * 80)
    pred_blend = (pred_logloss + pred_rmse) / 2
    brier_blend, score_blend = official_score(pred_blend, y_val)
    print(f"[Logloss+RMSE 평균] Brier={brier_blend:.6f} | score={score_blend:.2f}")

    print()
    print("=" * 80)
    print("요약")
    print("=" * 80)
    print(f"Logloss (exp_007 재현): score={score_ll:.2f}")
    print(f"RMSE:                  score={score_rmse:.2f} | Δ vs Logloss={score_rmse-score_ll:+.2f}")
    print(f"Logloss+RMSE 평균:      score={score_blend:.2f} | Δ vs Logloss={score_blend-score_ll:+.2f}")
    best_label, best_score = max(
        [("Logloss", score_ll), ("RMSE", score_rmse), ("blend", score_blend)],
        key=lambda t: t[1],
    )
    print(f"\n최선: {best_label} (score={best_score:.2f})")
    print("\n완료.")


if __name__ == "__main__":
    main()
