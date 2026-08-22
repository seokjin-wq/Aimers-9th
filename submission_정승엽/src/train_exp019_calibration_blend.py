"""exp_019 -- refine exp_018's calibrator. exp_018's Platt/Isotonic were
fit on seed=42-only OOF, then applied to the exp_010 champion's actual
2-seed (42+1) AVERAGED predictions -- a mismatch between what the
calibrator saw (single-seed OOF) and what it's applied to (2-seed
average, which has lower variance / different distribution than either
single seed). This experiment builds a matching 2-seed-AVERAGED OOF
(same 5-fold row split, random_state=42, reused from
output/exp018_oof_cache.npz for the seed=42 half; new cross-fit for the
seed=1 half) and refits Platt/Isotonic on that blended OOF, to see if a
better-matched calibrator improves further on top of exp_018's 769.12.

Also re-checks calibration_bins on the winning variant to see whether
residual asymmetric bias remains (motivates further work, e.g. more
folds, if any).
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
from sklearn.model_selection import KFold

from calibration import fit_platt, apply_platt, fit_isotonic, apply_isotonic
from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRUNK_COLS,
    POST_SHRINKAGE_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)
from metrics import official_score, calibration_bins, expected_calibration_error
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
VAL_PRED_CACHE_SEED42 = "./output/exp018_champion_val_pred_cache.npy"
VAL_PRED_CACHE_SEED1 = "./output/exp019_champion_val_pred_seed1_cache.npy"

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

    print()
    print("=" * 80)
    print("1. seed=42 OOF는 캐시 재사용, seed=1 OOF는 동일 fold split으로 신규 cross-fit")
    print("=" * 80)
    npz42 = np.load(OOF_CACHE_SEED42)
    oof_pred_42, oof_y = npz42["pred"], npz42["y"]
    assert np.array_equal(oof_y, y_2319), "fold 구성이 다름 -- KFold 파라미터 불일치"
    print(f"seed=42 OOF 캐시 로드 완료 (n={len(oof_pred_42)})")

    if os.path.exists(OOF_CACHE_SEED1):
        npz1 = np.load(OOF_CACHE_SEED1)
        oof_pred_1 = npz1["pred"]
        print(f"seed=1 OOF 캐시 로드 완료: {OOF_CACHE_SEED1}")
    else:
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=KFOLD_SEED)
        oof_pred_1 = np.zeros(len(train_2319))
        cb_params_seed1 = dict(
            iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=1, thread_count=-1, verbose=False,
        )
        t0 = time.time()
        for fold, (tr_idx, ho_idx) in enumerate(kf.split(train_2319)):
            X_tr, y_tr = X_2319.iloc[tr_idx], y_2319[tr_idx]
            X_ho = X_2319.iloc[ho_idx]
            train_pool = cb.Pool(X_tr, y_tr, cat_features=CAT_COLS)
            clf = cb.CatBoostClassifier(**cb_params_seed1)
            clf.fit(train_pool, verbose=False)
            oof_pred_1[ho_idx] = clf.predict_proba(X_ho)[:, 1]
            print(f"  fold {fold+1}/{N_FOLDS} 완료 ({time.time()-t0:.1f}s 누적)")
        os.makedirs("./output", exist_ok=True)
        np.savez(OOF_CACHE_SEED1, pred=oof_pred_1, y=y_2319)
        print(f"저장(캐시): {OOF_CACHE_SEED1}")

    oof_pred_blend = (oof_pred_42 + oof_pred_1) / 2
    brier_b, score_b = official_score(oof_pred_blend, oof_y)
    print(f"블렌드 OOF(2019-2023, 참고용): Brier={brier_b:.6f}, score={score_b:.2f}")

    print()
    print("=" * 80)
    print("2. 블렌드 OOF로 Platt/Isotonic 재학습")
    print("=" * 80)
    platt_blend = fit_platt(oof_pred_blend, oof_y, seed=42)
    iso_blend = fit_isotonic(oof_pred_blend, oof_y)

    print()
    print("=" * 80)
    print("3. 실제 챔피언 2024 예측 준비 (seed=42 캐시 재사용, seed=1 신규/캐시)")
    print("=" * 80)
    val_pred_42 = np.load(VAL_PRED_CACHE_SEED42)
    if os.path.exists(VAL_PRED_CACHE_SEED1):
        val_pred_1 = np.load(VAL_PRED_CACHE_SEED1)
        print(f"seed=1 val 예측 캐시 로드: {VAL_PRED_CACHE_SEED1}")
    else:
        cb_params_seed1_full = dict(
            iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=1, thread_count=-1, verbose=False,
        )
        train_pool_full = cb.Pool(X_2319, y_2319, cat_features=CAT_COLS)
        val_pool_full = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
        t = time.time()
        clf = cb.CatBoostClassifier(**cb_params_seed1_full)
        clf.fit(train_pool_full, eval_set=val_pool_full, early_stopping_rounds=100)
        val_pred_1 = clf.predict_proba(X_val)[:, 1]
        np.save(VAL_PRED_CACHE_SEED1, val_pred_1)
        print(f"seed=1 학습+저장 완료 :: {time.time()-t:.1f}s")

    val_pred_2seed = (val_pred_42 + val_pred_1) / 2
    brier_champ, score_champ = official_score(val_pred_2seed, y_val)
    print(f"[exp_010 챔피언(2시드평균) 재현] Brier={brier_champ:.6f} | score={score_champ:.2f}")

    print()
    print("=" * 80)
    print("4. 비교: raw vs exp_018(seed42-only OOF Platt) vs 신규(블렌드 OOF Platt/Isotonic)")
    print("=" * 80)
    npz42_old = np.load(OOF_CACHE_SEED42)
    platt_old = fit_platt(npz42_old["pred"], npz42_old["y"], seed=42)

    variants = {
        "raw(무보정)": val_pred_2seed,
        "exp_018 Platt(seed42-only OOF)": apply_platt(platt_old, val_pred_2seed),
        "신규 Platt(블렌드 OOF)": apply_platt(platt_blend, val_pred_2seed),
        "신규 Isotonic(블렌드 OOF)": apply_isotonic(iso_blend, val_pred_2seed),
    }
    results = {}
    for name, p in variants.items():
        brier, score = official_score(p, y_val)
        results[name] = (brier, score)
        print(f"[{name}] Brier={brier:.6f} | score={score:.2f}")

    baseline = results["raw(무보정)"][1]
    print()
    print("=" * 80)
    print("요약 (기준: raw 2시드평균)")
    print("=" * 80)
    for name, (brier, score) in results.items():
        print(f"{name}: score={score:.2f} | Δ={score-baseline:+.2f}")
    best_name = max(results, key=lambda n: results[n][1])
    print(f"\n최선: {best_name} (score={results[best_name][1]:.2f})")

    print()
    print("=" * 80)
    print("5. 최선 변형의 잔차 보정곡선 (calibration_bins)")
    print("=" * 80)
    best_pred = variants[best_name]
    bins = calibration_bins(best_pred, y_val, n_bins=10)
    ece = expected_calibration_error(best_pred, y_val)
    print(f"ECE={ece:.6f}")
    print(bins)

    print("\n완료.")


if __name__ == "__main__":
    main()
