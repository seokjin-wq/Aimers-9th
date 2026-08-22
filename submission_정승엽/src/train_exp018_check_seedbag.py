"""exp_018 step 2b -- quick check: does the Platt calibrator fit on
seed=42's OOF predictions (train_exp018_calibration.py) still help when
applied to the actual exp_010 champion (2-seed 42+1 average), not just
single-seed 42? Reuses the already-cached seed=42 val prediction and
the already-fit Platt calibrator's logic by refitting Platt from the
cached OOF (fast, no retraining) -- only NEW compute here is training
seed=1 once to get its actual 2024 predictions.
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
OOF_CACHE = "./output/exp018_oof_cache.npz"
VAL_PRED_CACHE_SEED42 = "./output/exp018_champion_val_pred_cache.npy"

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

    X_train = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET].to_numpy()

    print()
    print("=" * 80)
    print("1. seed=1 학습 (seed=42는 캐시 재사용)")
    print("=" * 80)
    cb_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=1, thread_count=-1, verbose=False,
    )
    train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
    t = time.time()
    clf = cb.CatBoostClassifier(**cb_params)
    clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    pred_seed1 = clf.predict_proba(X_val)[:, 1]
    print(f"seed=1 학습 완료 :: {time.time()-t:.1f}s")

    pred_seed42 = np.load(VAL_PRED_CACHE_SEED42)
    pred_2seed_avg = (pred_seed42 + pred_seed1) / 2
    brier_champ, score_champ = official_score(pred_2seed_avg, y_val)
    print(f"[exp_010 챔피언(2시드평균) 재현] Brier={brier_champ:.6f} | score={score_champ:.2f}")

    print()
    print("=" * 80)
    print("2. seed=42 OOF로 학습한 Platt/Isotonic을 2시드평균에 적용")
    print("=" * 80)
    npz = np.load(OOF_CACHE)
    oof_pred, oof_y = npz["pred"], npz["y"]
    platt = fit_platt(oof_pred, oof_y, seed=42)
    iso = fit_isotonic(oof_pred, oof_y)

    variants = {
        "raw(2시드평균, 무보정)": pred_2seed_avg,
        "Platt(seed42 OOF로 학습)": apply_platt(platt, pred_2seed_avg),
        "Isotonic(seed42 OOF로 학습)": apply_isotonic(iso, pred_2seed_avg),
    }
    results = {}
    for name, p in variants.items():
        brier, score = official_score(p, y_val)
        results[name] = (brier, score)
        print(f"[{name}] Brier={brier:.6f} | score={score:.2f}")

    baseline = results["raw(2시드평균, 무보정)"][1]
    print()
    print("=" * 80)
    print("요약 (기준: exp_010 챔피언 raw 2시드평균)")
    print("=" * 80)
    for name, (brier, score) in results.items():
        print(f"{name}: score={score:.2f} | Δ={score-baseline:+.2f}")

    print("\n완료.")


if __name__ == "__main__":
    main()
