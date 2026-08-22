"""exp_015 -- do the two independent wins from this session STACK?
exp_010 found 2-seed CatBoost averaging (seeds 42+1) beats single-seed
by +8.72 (variance reduction, same architecture). exp_013 found a small
CatBoost+LightGBM blend beats single-seed CatBoost by +2.02 (cross-
architecture diversity, but LightGBM is much weaker standalone so the
gain was modest). This experiment checks whether "2-seed CatBoost
average" + "a bit of LightGBM" combines additively (~+10-11 vs exp_007)
or whether the two variance-reduction mechanisms overlap/interfere.
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
CB_SEEDS = [42, 1]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


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

    X_train_cb = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val_cb = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET]

    cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    train_enc = train_shrunk.copy()
    train_enc[CAT_COLS] = cat_encoder.fit_transform(train_enc[CAT_COLS]).astype(int)
    X_train_enc = train_enc.loc[~is_val, TRACKMAN_FEATURE_SET]
    X_val_enc = train_enc.loc[is_val, TRACKMAN_FEATURE_SET]

    print()
    print("=" * 80)
    print(f"1. CatBoost {CB_SEEDS}개 시드")
    print("=" * 80)
    cb_preds = {}
    for seed in CB_SEEDS:
        cb_params = dict(
            iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=seed, thread_count=-1, verbose=False,
        )
        t = time.time()
        train_pool = cb.Pool(X_train_cb, y_train, cat_features=CAT_COLS)
        val_pool = cb.Pool(X_val_cb, y_val, cat_features=CAT_COLS)
        clf = cb.CatBoostClassifier(**cb_params)
        clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        pred = clf.predict_proba(X_val_cb)[:, 1]
        brier, score = official_score(pred, y_val)
        cb_preds[seed] = pred
        print(f"[CatBoost seed={seed}] Brier={brier:.6f} | score={score:.2f} | {time.time()-t:.1f}s")
    cb_avg = sum(cb_preds.values()) / len(CB_SEEDS)
    brier_cbavg, score_cbavg = official_score(cb_avg, y_val)
    print(f"[CatBoost {len(CB_SEEDS)}시드 평균] Brier={brier_cbavg:.6f} | score={score_cbavg:.2f} (exp_010 재현)")

    print()
    print("=" * 80)
    print("2. LightGBM (exp_013와 동일 설정)")
    print("=" * 80)
    lgb_params = dict(
        objective="binary", metric="binary_logloss",
        learning_rate=0.03, num_leaves=63,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
        min_child_samples=200, seed=42, num_threads=-1, verbosity=-1,
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
    print(f"[LightGBM] Brier={brier_lgb:.6f} | score={score_lgb:.2f} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("3. 블렌딩: (CatBoost 2시드 평균) + LightGBM, validation 그리드서치")
    print("=" * 80)
    pred_dict = {"catboost_2seed_avg": cb_avg, "lightgbm": pred_lgb}
    best_w, best_brier, best_score = coarse_fine_blend_search(pred_dict, y_val.to_numpy(), list(pred_dict.keys()))
    print(f"[블렌드 최적] weights={ {k: round(v,3) for k,v in best_w.items()} } | Brier={best_brier:.6f} | score={best_score:.2f}")

    print()
    print("=" * 80)
    print("요약 (기준: exp_007=740.86)")
    print("=" * 80)
    print(f"exp_010 (CatBoost 2시드 평균): score={score_cbavg:.2f} | Δ vs exp_007={score_cbavg-740.86:+.2f}")
    print(f"exp_013 스타일 단일CatBoost+LightGBM 블렌드 참고용 없음(이 실행은 2시드 평균 기준)")
    print(f"exp_015 (2시드평균 + LightGBM 블렌드): score={best_score:.2f} | Δ vs exp_007={best_score-740.86:+.2f} | Δ vs exp_010={best_score-score_cbavg:+.2f}")
    print("\n완료.")


if __name__ == "__main__":
    main()
