"""exp_013 -- genuine cross-architecture stacking/blending on top of the
exp_007 champion 89-feature set (exp_003's 84 + 5 trackman pitcher-level
as-of physical features, shrink_k=50).

exp_006 already tried blending CatBoost with RandomForest/ExtraTrees/
LogisticRegression and found the optimal weight always collapsed to
CatBoost=1.0 -- those models are both much weaker AND make similar
mistakes (all are just "worse trees/linear on the same tabular
features"), so there was no error-cancellation benefit. This experiment
tries LightGBM and XGBoost instead: both are boosted-tree families
roughly as strong as CatBoost on tabular data (unlike RF/ET/LR), but
with genuinely different tree-growth/regularization mechanics (leaf-wise
vs. CatBoost's symmetric/oblivious trees, different split-finding and
categorical handling), so their errors may correlate less than same-
architecture seed-bagging (exp_010) or weak-model blending (exp_006)
did. Weights are chosen via `src/ensemble.coarse_fine_blend_search` on
the SAME validation split used everywhere else in this project (never
via leaderboard probing, per `dacon-leaderboard-probing-risk` memory).
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import lightgbm as lgb
import xgboost as xgb
# catboost는 반드시 lightgbm보다 나중에 import한다 -- 이 환경(Windows,
# lightgbm 4.7.0)에서 catboost를 먼저 import하면 이후 모든
# lgb.Dataset(...) 생성이 데이터 내용과 무관하게(순수 랜덤 배열로도
# 재현됨) set_label 단계에서 access violation으로 크래시하는 DLL
# 로드순서 충돌이 실제로 확인됨(2026-08-21 진단, exp_013). numpy/pandas
# import 순서는 영향 없음 -- catboost -> lightgbm 순서 자체가 원인.
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


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


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

    X_train_cb = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val_cb = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET]
    print(f"train={X_train_cb.shape}, val={X_val_cb.shape}, features={len(TRACKMAN_FEATURE_SET)}")

    # LightGBM/XGBoost는 범주형을 정수 인코딩해서 넘긴다 (train_lgbm.py와
    # 동일한 이유 -- category dtype을 LightGBM에 직접 넘기면 이 환경에서
    # 네이티브 크래시가 재현됨). 인코더는 train split에서만 fit.
    cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    train_enc = train_shrunk.copy()
    train_enc[CAT_COLS] = cat_encoder.fit_transform(train_enc[CAT_COLS]).astype(int)
    X_train_enc = train_enc.loc[~is_val, TRACKMAN_FEATURE_SET]
    X_val_enc = train_enc.loc[is_val, TRACKMAN_FEATURE_SET]

    print()
    print("=" * 80)
    print("1. CatBoost (챔피언 재현)")
    print("=" * 80)
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
    print(f"[CatBoost] Brier={brier_cb:.6f} | score={score_cb:.2f} | best_iter={clf_cb.get_best_iteration()} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("2. LightGBM")
    print("=" * 80)
    # sklearn 래퍼(LGBMClassifier.fit)가 이 환경(lightgbm 4.7.0)에서
    # eval_set 전달 시 access violation으로 크래시함 (신규 발견 --
    # CLAUDE.md에 기록된 기존 이슈는 "pickle 저장 후 다른 프로세스에서
    # 로드" 시나리오였는데, 이번엔 fit() 자체에서 재현됨). 네이티브
    # lgb.train()+lgb.Dataset API로 우회 (어차피 저장은 원래도 네이티브
    # 포맷을 씀 -- train_lgbm.py와 동일한 이유).
    lgb_params = dict(
        objective="binary", metric="binary_logloss",
        learning_rate=0.03, num_leaves=63,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
        min_child_samples=200, seed=SEED, num_threads=-1, verbosity=-1,
    )
    t = time.time()
    lgb_train_set = lgb.Dataset(X_train_enc, label=y_train.to_numpy(), categorical_feature=CAT_COLS)
    lgb_val_set = lgb.Dataset(X_val_enc, label=y_val.to_numpy(), categorical_feature=CAT_COLS, reference=lgb_train_set)
    booster_lgb = lgb.train(
        lgb_params, lgb_train_set, num_boost_round=2000, valid_sets=[lgb_val_set],
        callbacks=[lgb.early_stopping(100), lgb.log_evaluation(200)],
    )
    pred_lgb = booster_lgb.predict(X_val_enc, num_iteration=booster_lgb.best_iteration)
    brier_lgb, score_lgb = official_score(pred_lgb, y_val)
    print(f"[LightGBM] Brier={brier_lgb:.6f} | score={score_lgb:.2f} | best_iter={booster_lgb.best_iteration} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("3. XGBoost")
    print("=" * 80)
    xgb_params = dict(
        objective="binary:logistic", eval_metric="logloss",
        n_estimators=2000, learning_rate=0.03, max_depth=6,
        subsample=0.8, colsample_bytree=0.8, min_child_weight=10,
        reg_lambda=3.0, random_state=SEED, n_jobs=-1,
        early_stopping_rounds=100,
    )
    t = time.time()
    clf_xgb = xgb.XGBClassifier(**xgb_params)
    clf_xgb.fit(X_train_enc, y_train, eval_set=[(X_val_enc, y_val)], verbose=200)
    pred_xgb = clf_xgb.predict_proba(X_val_enc)[:, 1]
    brier_xgb, score_xgb = official_score(pred_xgb, y_val)
    print(f"[XGBoost] Brier={brier_xgb:.6f} | score={score_xgb:.2f} | best_iter={clf_xgb.best_iteration} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("4. 블렌딩 (coarse->fine 심플렉스 그리드서치, validation에서만)")
    print("=" * 80)
    pred_dict = {"catboost": pred_cb, "lightgbm": pred_lgb, "xgboost": pred_xgb}
    all_candidates = list(pred_dict.keys())
    best_w, best_brier, best_score = coarse_fine_blend_search(pred_dict, y_val.to_numpy(), all_candidates)
    print(f"[3-way 블렌드 최적] weights={ {k: round(v,3) for k,v in best_w.items()} } | Brier={best_brier:.6f} | score={best_score:.2f}")

    for pair in [("catboost", "lightgbm"), ("catboost", "xgboost"), ("lightgbm", "xgboost")]:
        w, brier, score = coarse_fine_blend_search(pred_dict, y_val.to_numpy(), list(pair))
        print(f"[{pair[0]}+{pair[1]} 블렌드] weights={ {k: round(v,3) for k,v in w.items()} } | Brier={brier:.6f} | score={score:.2f}")

    print()
    print("=" * 80)
    print("요약")
    print("=" * 80)
    print(f"CatBoost 단독:  score={score_cb:.2f}")
    print(f"LightGBM 단독:  score={score_lgb:.2f}")
    print(f"XGBoost 단독:   score={score_xgb:.2f}")
    print(f"3-way 최적 블렌드: score={best_score:.2f} | Δ vs CatBoost={best_score-score_cb:+.2f}")
    print("\n완료.")


if __name__ == "__main__":
    main()
