"""exp_010 — seed-averaged CatBoost bagging on top of the champion
trackman feature set (exp_007's 5-col physical set, `TRACKMAN_FEATURE_SET`
below -- exp_008's 8-col extension was tried and rejected; change this
constant if exp_009's hyperparameter search picks a different champion).
Trains N_SEEDS independent CatBoost models with
identical data/features/hyperparameters but different `random_seed`
(which changes CatBoost's internal Bayesian-bootstrap row sampling and
feature-split tie-breaking), then averages their predicted
probabilities. This reduces prediction VARIANCE (not bias) -- exp_006
already showed blending CatBoost with structurally different, weaker
models (RF/ET/LR) doesn't help because they're both weaker AND their
errors don't cancel enough to offset the accuracy gap; seed-bagging the
SAME strong architecture instead targets pure variance reduction, which
should be strictly non-negative in expectation for Brier score (a
proper scoring rule) as long as the individual models are unbiased and
not pathologically correlated.
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
SEEDS = [42, 1, 7, 123, 2024]
TRACKMAN_SHRINK_K = 50

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
    print("0. 데이터 로드 + 피처 구축 (exp_007 5col trackman 챔피언, k=50)")
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
    print(f"1. {len(SEEDS)}개 시드로 독립 CatBoost 학습")
    print("=" * 80)
    val_preds = {}
    for seed in SEEDS:
        cb_params = dict(
            iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=seed, thread_count=-1, verbose=False,
        )
        train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
        val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
        t = time.time()
        clf = cb.CatBoostClassifier(**cb_params)
        clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        elapsed = time.time() - t
        pred = clf.predict_proba(X_val)[:, 1]
        brier, score = official_score(pred, y_val)
        val_preds[seed] = pred
        print(f"[seed={seed}] Brier={brier:.6f} | score={score:.2f} | best_iter={clf.get_best_iteration()} | {elapsed:.1f}s")

    print()
    print("=" * 80)
    print("2. 시드 평균 앙상블 (누적: 2개->N개 평균까지 순차적으로)")
    print("=" * 80)
    cum_pred = np.zeros(len(y_val))
    for i, seed in enumerate(SEEDS, start=1):
        cum_pred = cum_pred + val_preds[seed]
        avg_pred = cum_pred / i
        brier, score = official_score(avg_pred, y_val)
        print(f"[{i}개 시드 평균] Brier={brier:.6f} | score={score:.2f}")

    single_scores = {s: official_score(val_preds[s], y_val)[1] for s in SEEDS}
    best_single = max(single_scores, key=single_scores.get)
    full_avg_pred = sum(val_preds.values()) / len(SEEDS)
    _, full_avg_score = official_score(full_avg_pred, y_val)
    print(f"\n최고 단일 시드: seed={best_single}, score={single_scores[best_single]:.2f}")
    print(f"{len(SEEDS)}개 전체 평균: score={full_avg_score:.2f}, Δ vs 최고단일={full_avg_score-single_scores[best_single]:+.2f}")

    print("\n완료.")


if __name__ == "__main__":
    main()
