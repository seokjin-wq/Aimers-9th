"""exp_022 final -- swap in a calibrator that also uses 2024 (heavily
weighted) rather than only 2019-2023 OOF, motivated by a confirmed
season base-rate drift (control_success rate falls every season,
2019=0.565 -> 2024=0.486, linear-trend 2025 extrapolate=0.4747) that
the 2019-2023-only Platt calibrator (exp_018/019) doesn't fully track:
raw champion 2024 predictions average 0.4962 vs the true 2024 rate
0.4861, and the old calibrator only partly closes that gap.

`train_exp022_recency_calibration.py`'s 5-fold CV strictly WITHIN 2024
found: including 2024's (already-genuinely-out-of-sample, since the
val-prediction model was trained only on 2019-2023) predictions in the
calibrator's training set, weighted, monotonically improves held-out
2024 performance and plateaus around weight>=50-150 (~+20 vs the
2019-2023-only baseline, essentially matching a 2024-only fit).

This script builds the PRODUCTION calibrator using ALL of 2024 (weight
100, near the plateau) + the full 2019-2023 OOF, and swaps it into
model_meta.pkl -- underlying models UNCHANGED from exp_018/019_final
(same full-2019-2024-retrained seed={42,1} CatBoost pair, files reused).
No new CatBoost training needed.
"""

import os

import joblib
import numpy as np
import pandas as pd

from calibration import fit_platt
from sklearn.linear_model import LogisticRegression

MODEL_DIR = "./model"
DATA_DIR = "./data"
OOF_CACHE_SEED42 = "./output/exp018_oof_cache.npz"
OOF_CACHE_SEED1 = "./output/exp019_oof_seed1_cache.npz"
VAL_PRED_CACHE_SEED42 = "./output/exp018_champion_val_pred_cache.npy"
VAL_PRED_CACHE_SEED1 = "./output/exp019_champion_val_pred_seed1_cache.npy"
WEIGHT_2024 = 100.0


def fit_platt_weighted(raw_pred, y, sample_weight, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y, sample_weight=sample_weight)
    return clf


def main():
    meta_path = os.path.join(MODEL_DIR, "model_meta.pkl")
    meta = joblib.load(meta_path)
    assert meta["model_type"] == "catboost_seedbag"
    assert meta["seed_model_files"] == ["catboost_model_seed42.cbm", "catboost_model_seed1.cbm"], meta["seed_model_files"]

    npz42 = np.load(OOF_CACHE_SEED42)
    npz1 = np.load(OOF_CACHE_SEED1)
    oof_2319 = (npz42["pred"] + npz1["pred"]) / 2
    y_2319 = npz42["y"]

    val_pred_42 = np.load(VAL_PRED_CACHE_SEED42)
    val_pred_1 = np.load(VAL_PRED_CACHE_SEED1)
    val_pred_2024 = (val_pred_42 + val_pred_1) / 2
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=["season", "control_success"])
    y_2024 = train.loc[train["season"] == 2024, "control_success"].to_numpy()
    assert len(val_pred_2024) == len(y_2024)

    p_combo = np.concatenate([oof_2319, val_pred_2024])
    y_combo = np.concatenate([y_2319, y_2024])
    sw = np.concatenate([np.ones(len(oof_2319)), np.full(len(val_pred_2024), WEIGHT_2024)])
    platt_recency = fit_platt_weighted(p_combo, y_combo, sample_weight=sw, seed=42)
    print(f"2024-가중 Platt 학습 완료 (2019-2023 OOF n={len(oof_2319)}, 2024 n={len(val_pred_2024)}, weight={WEIGHT_2024})")
    print(f"coef={platt_recency.coef_}, intercept={platt_recency.intercept_}")

    meta["calibrator"] = platt_recency
    meta["exp_id"] = "exp_022_recency_calibrated_seedbag42_1"
    joblib.dump(meta, meta_path, compress=3)
    print(f"저장: {meta_path} (calibrator=2024-가중 Platt, 모델 파일은 exp_018/019와 동일)")


if __name__ == "__main__":
    main()
