"""exp_020 -- true OOF-based stacking meta-learner, as opposed to
exp_013/015/017's simple linear blend-weight search on the 2024 val set
directly. Previous blends found LightGBM only worth ~+2 points over pure
CatBoost (LightGBM is much weaker standalone), which suggested near-zero
extra diversity -- but a linear weight search on val predictions can
only ever find an affine combination; it can't discover any nonlinear
interaction between the base models' outputs (e.g. "trust LightGBM more
specifically when it and CatBoost disagree in a particular direction").

This trains a small LogisticRegression meta-learner on genuine 5-fold
cross-fit OOF predictions (2019-2023) from CatBoost seed=42 (reused
cache), CatBoost seed=1 (reused cache), and LightGBM "slow_lr" (exp_017's
best standalone LightGBM config -- new OOF, cheap since LightGBM trains
in ~20-30s). The meta-learner is then applied to the REAL 2024
predictions of all three fully-trained models (never touches 2024
during its own fit). Compared against: raw CatBoost 2-seed average,
exp_019's blended-OOF Platt (769.87, current best), and a plain
uniform 3-way average as a sanity baseline.
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
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.preprocessing import OrdinalEncoder

from calibration import fit_platt, apply_platt
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
KFOLD_SEED = 42
N_FOLDS = 5
OOF_CACHE_SEED42 = "./output/exp018_oof_cache.npz"
OOF_CACHE_SEED1 = "./output/exp019_oof_seed1_cache.npz"
OOF_CACHE_LGB = "./output/exp020_oof_lgb_cache.npz"
VAL_PRED_CACHE_SEED42 = "./output/exp018_champion_val_pred_cache.npy"
VAL_PRED_CACHE_SEED1 = "./output/exp019_champion_val_pred_seed1_cache.npy"
VAL_PRED_CACHE_LGB = "./output/exp020_champion_val_pred_lgb_cache.npy"

LGB_PARAMS = dict(
    objective="binary", metric="binary_logloss", seed=42, num_threads=-1, verbosity=-1,
    num_leaves=63, learning_rate=0.01, min_child_samples=200, subsample=0.8, colsample_bytree=0.8, reg_lambda=0.0,
)

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

    train_2319 = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET + [TARGET]].reset_index(drop=True)
    X_2319 = train_2319[TRACKMAN_FEATURE_SET]
    y_2319 = train_2319[TARGET].to_numpy()

    X_val = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET].to_numpy()

    cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    X_2319_enc = X_2319.copy()
    X_2319_enc[CAT_COLS] = cat_encoder.fit_transform(X_2319_enc[CAT_COLS]).astype(int)
    X_val_enc = X_val.copy()
    X_val_enc[CAT_COLS] = cat_encoder.transform(X_val_enc[CAT_COLS]).astype(int)

    print()
    print("=" * 80)
    print("1. OOF 확보 -- CatBoost seed42/seed1(캐시), LightGBM slow_lr(신규, 빠름)")
    print("=" * 80)
    npz42 = np.load(OOF_CACHE_SEED42)
    oof_cb42, oof_y = npz42["pred"], npz42["y"]
    npz1 = np.load(OOF_CACHE_SEED1)
    oof_cb1 = npz1["pred"]
    assert np.array_equal(oof_y, y_2319)
    print(f"CatBoost OOF 캐시 로드 완료 (n={len(oof_cb42)})")

    if os.path.exists(OOF_CACHE_LGB):
        oof_lgb = np.load(OOF_CACHE_LGB)["pred"]
        print(f"LightGBM OOF 캐시 로드: {OOF_CACHE_LGB}")
    else:
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=KFOLD_SEED)
        oof_lgb = np.zeros(len(train_2319))
        t0 = time.time()
        for fold, (tr_idx, ho_idx) in enumerate(kf.split(train_2319)):
            X_tr, y_tr = X_2319_enc.iloc[tr_idx], y_2319[tr_idx]
            X_ho = X_2319_enc.iloc[ho_idx]
            lgb_train_set = lgb.Dataset(X_tr, label=y_tr, categorical_feature=CAT_COLS)
            booster = lgb.train(LGB_PARAMS, lgb_train_set, num_boost_round=2000)
            oof_lgb[ho_idx] = booster.predict(X_ho)
            print(f"  fold {fold+1}/{N_FOLDS} 완료 ({time.time()-t0:.1f}s 누적)")
        os.makedirs("./output", exist_ok=True)
        np.savez(OOF_CACHE_LGB, pred=oof_lgb, y=y_2319)
        print(f"저장(캐시): {OOF_CACHE_LGB}")

    for name, p in [("cb42", oof_cb42), ("cb1", oof_cb1), ("lgb", oof_lgb)]:
        brier, score = official_score(p, oof_y)
        print(f"  [OOF {name} 단독] Brier={brier:.6f} score={score:.2f}")

    print()
    print("=" * 80)
    print("2. 메타학습기(LogisticRegression) 학습 -- OOF 3종을 피처로")
    print("=" * 80)
    meta_X_oof = np.column_stack([oof_cb42, oof_cb1, oof_lgb])
    meta = LogisticRegression(random_state=42)
    meta.fit(meta_X_oof, oof_y)
    print(f"메타 계수: {meta.coef_}, 절편: {meta.intercept_}")
    meta_oof_pred = meta.predict_proba(meta_X_oof)[:, 1]
    brier_m, score_m = official_score(meta_oof_pred, oof_y)
    print(f"메타 OOF 자체 성능(참고): Brier={brier_m:.6f} score={score_m:.2f}")

    print()
    print("=" * 80)
    print("3. 실제 2024 예측 준비 (CatBoost 캐시 재사용, LightGBM 신규/캐시)")
    print("=" * 80)
    val_pred_cb42 = np.load(VAL_PRED_CACHE_SEED42)
    val_pred_cb1 = np.load(VAL_PRED_CACHE_SEED1)

    if os.path.exists(VAL_PRED_CACHE_LGB):
        val_pred_lgb = np.load(VAL_PRED_CACHE_LGB)
        print(f"LightGBM val 예측 캐시 로드: {VAL_PRED_CACHE_LGB}")
    else:
        lgb_train_full = lgb.Dataset(X_2319_enc, label=y_2319, categorical_feature=CAT_COLS)
        lgb_val_full = lgb.Dataset(X_val_enc, label=y_val, categorical_feature=CAT_COLS, reference=lgb_train_full)
        t = time.time()
        booster = lgb.train(
            LGB_PARAMS, lgb_train_full, num_boost_round=5000, valid_sets=[lgb_val_full],
            callbacks=[lgb.early_stopping(150, verbose=False), lgb.log_evaluation(0)],
        )
        val_pred_lgb = booster.predict(X_val_enc, num_iteration=booster.best_iteration)
        np.save(VAL_PRED_CACHE_LGB, val_pred_lgb)
        print(f"LightGBM 학습+저장 완료 :: {time.time()-t:.1f}s (best_iter={booster.best_iteration})")

    print()
    print("=" * 80)
    print("4. 비교: raw 2시드평균 / exp_019 Platt / 3-way 단순평균 / 메타학습기 / 메타+Platt")
    print("=" * 80)
    val_pred_2seed = (val_pred_cb42 + val_pred_cb1) / 2
    npz1_ = np.load(OOF_CACHE_SEED1)
    oof_blend = (oof_cb42 + oof_cb1) / 2
    platt_blend = fit_platt(oof_blend, oof_y, seed=42)

    meta_X_val = np.column_stack([val_pred_cb42, val_pred_cb1, val_pred_lgb])
    meta_val_pred = meta.predict_proba(meta_X_val)[:, 1]

    val_pred_3way_avg = (val_pred_cb42 + val_pred_cb1 + val_pred_lgb) / 3

    variants = {
        "raw 2시드평균": val_pred_2seed,
        "exp_019 Platt(2시드 블렌드 OOF)": apply_platt(platt_blend, val_pred_2seed),
        "3-way 단순평균(cb42+cb1+lgb)": val_pred_3way_avg,
        "메타학습기(LogReg on 3 OOF)": meta_val_pred,
    }
    results = {}
    for name, p in variants.items():
        brier, score = official_score(p, y_val)
        results[name] = (brier, score)
        print(f"[{name}] Brier={brier:.6f} | score={score:.2f}")

    baseline = results["raw 2시드평균"][1]
    print()
    print("=" * 80)
    print("요약 (기준: raw 2시드평균)")
    print("=" * 80)
    for name, (brier, score) in results.items():
        print(f"{name}: score={score:.2f} | Δ={score-baseline:+.2f}")
    best_name = max(results, key=lambda n: results[n][1])
    print(f"\n최선: {best_name} (score={results[best_name][1]:.2f})")

    print("\n완료.")


if __name__ == "__main__":
    main()
