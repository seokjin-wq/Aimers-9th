"""exp_017 -- exp_013 blended CatBoost with a DEFAULT-hyperparameter
LightGBM and only got +2.02 (LightGBM was ~48 points weaker standalone,
too weak to blend well). LightGBM trains in ~15-30s here (vs CatBoost's
~200s), so a quick manual hyperparameter pass is cheap: try a handful of
configs (deeper leaves, lower learning rate + more rounds, stronger
regularization) and see whether a materially stronger standalone
LightGBM closes the gap enough to make the CatBoost+LightGBM blend beat
exp_010's 749.58 champion by more than exp_013/exp_015's ~+2 noise-level
margin.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import lightgbm as lgb
import catboost as cb
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from ensemble import coarse_fine_blend_search
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

LGB_CONFIGS = {
    "baseline(exp_013)": dict(num_leaves=63, learning_rate=0.03, min_child_samples=200, subsample=0.8, colsample_bytree=0.8, reg_lambda=0.0),
    "deeper_leaves": dict(num_leaves=255, learning_rate=0.03, min_child_samples=100, subsample=0.8, colsample_bytree=0.8, reg_lambda=0.0),
    "slow_lr": dict(num_leaves=63, learning_rate=0.01, min_child_samples=200, subsample=0.8, colsample_bytree=0.8, reg_lambda=0.0),
    "strong_reg": dict(num_leaves=63, learning_rate=0.03, min_child_samples=200, subsample=0.7, colsample_bytree=0.7, reg_lambda=5.0),
    "deep_slow": dict(num_leaves=255, learning_rate=0.01, min_child_samples=100, subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0),
}


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축")
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

    y_train = train_shrunk.loc[~is_val, TARGET]
    y_val = train_shrunk.loc[is_val, TARGET]

    cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    train_enc = train_shrunk.copy()
    train_enc[CAT_COLS] = cat_encoder.fit_transform(train_enc[CAT_COLS]).astype(int)
    X_train_enc = train_enc.loc[~is_val, TRACKMAN_FEATURE_SET]
    X_val_enc = train_enc.loc[is_val, TRACKMAN_FEATURE_SET]

    print()
    print("=" * 80)
    print(f"1. LightGBM {len(LGB_CONFIGS)}종 설정 비교")
    print("=" * 80)
    lgb_preds = {}
    lgb_scores = {}
    for name, overrides in LGB_CONFIGS.items():
        lgb_params = dict(
            objective="binary", metric="binary_logloss",
            seed=SEED, num_threads=-1, verbosity=-1,
        )
        lgb_params.update(overrides)
        t = time.time()
        lgb_train_set = lgb.Dataset(X_train_enc, label=y_train.to_numpy(), categorical_feature=CAT_COLS)
        lgb_val_set = lgb.Dataset(X_val_enc, label=y_val.to_numpy(), categorical_feature=CAT_COLS, reference=lgb_train_set)
        booster = lgb.train(
            lgb_params, lgb_train_set, num_boost_round=5000, valid_sets=[lgb_val_set],
            callbacks=[lgb.early_stopping(150, verbose=False), lgb.log_evaluation(0)],
        )
        pred = booster.predict(X_val_enc, num_iteration=booster.best_iteration)
        brier, score = official_score(pred, y_val)
        lgb_preds[name] = pred
        lgb_scores[name] = score
        print(f"[{name}] Brier={brier:.6f} | score={score:.2f} | best_iter={booster.best_iteration} | {time.time()-t:.1f}s")

    best_lgb_name = max(lgb_scores, key=lgb_scores.get)
    print(f"\n최선 LightGBM 설정: {best_lgb_name} (score={lgb_scores[best_lgb_name]:.2f})")

    print()
    print("=" * 80)
    print("2. CatBoost 챔피언 재현 (exp_007 파라미터)")
    print("=" * 80)
    X_train_cb = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    X_val_cb = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    cb_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=SEED, thread_count=-1, verbose=False,
    )
    t = time.time()
    train_pool = cb.Pool(X_train_cb, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val_cb, y_val, cat_features=CAT_COLS)
    clf_cb = cb.CatBoostClassifier(**cb_params)
    clf_cb.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    pred_cb = clf_cb.predict_proba(X_val_cb)[:, 1]
    brier_cb, score_cb = official_score(pred_cb, y_val)
    print(f"[CatBoost] Brier={brier_cb:.6f} | score={score_cb:.2f} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("3. CatBoost + 최선 LightGBM 블렌드")
    print("=" * 80)
    pred_dict = {"catboost": pred_cb, "lightgbm_tuned": lgb_preds[best_lgb_name]}
    best_w, best_brier, best_score = coarse_fine_blend_search(pred_dict, y_val.to_numpy(), list(pred_dict.keys()))
    print(f"[블렌드 최적] weights={ {k: round(v,3) for k,v in best_w.items()} } | Brier={best_brier:.6f} | score={best_score:.2f}")

    print()
    print("=" * 80)
    print("요약 (기준: exp_007=740.86, exp_010 챔피언=749.58)")
    print("=" * 80)
    for name, score in lgb_scores.items():
        print(f"LightGBM[{name}]: score={score:.2f}")
    print(f"CatBoost 단독: score={score_cb:.2f}")
    print(f"CatBoost+최선LightGBM 블렌드: score={best_score:.2f} | Δ vs exp_010챔피언(749.58)={best_score-749.58:+.2f}")
    print("\n완료.")


if __name__ == "__main__":
    main()
