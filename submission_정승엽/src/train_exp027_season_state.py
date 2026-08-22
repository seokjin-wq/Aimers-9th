"""exp_027 -- add current-season-only pitcher/batter state features
(ported from a teammate's pipeline, see season_state_features.py) on top
of the exp_007/010 champion feature set. Single seed=42, no bagging, to
match the exp_009/021-style ablation protocol for a first fast read
before committing to the full 2-seed champion retrain.
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
from season_state_features import (
    build_season_baselines,
    fit_season_state_priors,
    attach_season_state_features,
    season_state_cols,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
SEED = 42
VAL_SEASON = 2024

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS
SEASON_STATE_COLS = season_state_cols("pitcher") + season_state_cols("batter")
NEW_FEATURE_SET = TRACKMAN_FEATURE_SET + SEASON_STATE_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def fit_predict(feature_set, X_train, y_train, X_val, y_val, label):
    cb_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=SEED, thread_count=-1, verbose=False,
    )
    train_pool = cb.Pool(X_train[feature_set], y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val[feature_set], y_val, cat_features=CAT_COLS)
    t = time.time()
    clf = cb.CatBoostClassifier(**cb_params)
    clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    elapsed = time.time() - t
    pred = clf.predict_proba(X_val[feature_set])[:, 1]
    brier, score = official_score(pred, y_val)
    print(f"[{label}] Brier={brier:.6f} | score={score:.2f} | best_iter={clf.get_best_iteration()} | n_features={len(feature_set)} | {elapsed:.1f}s")
    return clf, pred, brier, score


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축 (기존 champion 피처 + 이번 시즌 상태 피처)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    is_val = train["season"] == VAL_SEASON
    train_only = train.loc[~is_val]

    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, val_priors_recent)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    pitcher_baselines = build_season_baselines(train_only, "pitcher")
    batter_baselines = build_season_baselines(train_only, "batter")
    pitcher_priors = fit_season_state_priors(train_only, "pitcher")
    batter_priors = fit_season_state_priors(train_only, "batter")
    train_full_feat = attach_season_state_features(train_shrunk, pitcher_baselines, pitcher_priors, "pitcher")
    train_full_feat = attach_season_state_features(train_full_feat, batter_baselines, batter_priors, "batter")

    X_train = train_full_feat.loc[~is_val]
    y_train = train_full_feat.loc[~is_val, TARGET]
    X_val = train_full_feat.loc[is_val]
    y_val = train_full_feat.loc[is_val, TARGET]
    print(f"train={X_train.shape}, val={X_val.shape}")
    print(f"새 피처 {len(SEASON_STATE_COLS)}개: {SEASON_STATE_COLS}")

    print()
    print("=" * 80)
    print("1. A/B 비교: 기존 챔피언 피처 vs +이번시즌 상태 피처")
    print("=" * 80)
    fit_predict(TRACKMAN_FEATURE_SET, X_train, y_train, X_val, y_val, "A: 챔피언(기존) 피처만")
    fit_predict(NEW_FEATURE_SET, X_train, y_train, X_val, y_val, "B: +이번시즌 상태 피처(exp_027)")

    print("\n완료.")


if __name__ == "__main__":
    main()
