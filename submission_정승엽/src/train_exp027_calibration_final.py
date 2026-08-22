"""exp_027 calibration -- apply the SAME two-step calibration chain that
worked for the champion (exp_022's 2024-weighted Platt, exp_023's
season-trend prior-shift) to the NEW exp_027 (season-state-augmented)
base model. Mirrors train_exp022_final.py + train_exp023_trend_
extrapolation.py exactly, just pointed at exp_027's OOF/val caches.
"""

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

DATA_DIR = "./data"
MODEL_DIR = "./model"
WEIGHT_2024 = 100.0

SEASONS = np.array([2019, 2020, 2021, 2022, 2023, 2024], dtype=float)
RATES = np.array([0.564670, 0.532712, 0.532762, 0.528920, 0.499957, 0.486105])


def fit_platt_weighted(raw_pred, y, sample_weight, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y, sample_weight=sample_weight)
    return clf


def main():
    meta_path = os.path.join(MODEL_DIR, "model_meta.pkl")
    meta = joblib.load(meta_path)
    assert meta["exp_id"] == "exp_027_season_state_seedbag42_1", meta["exp_id"]
    assert meta["seed_model_files"] == ["catboost_model_seed42.cbm", "catboost_model_seed1.cbm"]

    npz42 = np.load("./output/exp027_oof_cache_seed42.npz")
    npz1 = np.load("./output/exp027_oof_cache_seed1.npz")
    oof_2319 = (npz42["pred"] + npz1["pred"]) / 2
    y_2319 = npz42["y"]

    val_pred_42 = np.load("./output/exp027_val_pred_seed42.npy")
    val_pred_1 = np.load("./output/exp027_val_pred_seed1.npy")
    val_pred_2024 = (val_pred_42 + val_pred_1) / 2
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=["season", "control_success"])
    y_2024 = train.loc[train["season"] == 2024, "control_success"].to_numpy()
    assert len(val_pred_2024) == len(y_2024)

    print(f"OOF(2019-2023) n={len(oof_2319)}, 2024 n={len(val_pred_2024)}")
    print(f"raw 2024 예측 평균={val_pred_2024.mean():.4f}, 실제 2024 rate={y_2024.mean():.4f}")

    # step 1: exp_022 style -- 2024 가중 Platt
    p_combo = np.concatenate([oof_2319, val_pred_2024])
    y_combo = np.concatenate([y_2319, y_2024])
    sw = np.concatenate([np.ones(len(oof_2319)), np.full(len(val_pred_2024), WEIGHT_2024)])
    platt_recency = fit_platt_weighted(p_combo, y_combo, sample_weight=sw, seed=42)
    print(f"step1(exp_022 style, weight={WEIGHT_2024}): coef={platt_recency.coef_}, intercept={platt_recency.intercept_}")
    mean_after_step1 = platt_recency.predict_proba(val_pred_2024.reshape(-1, 1))[:, 1].mean()
    print(f"  2024 예측에 적용 시 평균: {mean_after_step1:.4f} (목표: 실제 2024 rate {y_2024.mean():.4f})")

    # step 2: exp_023 style -- 2025 추세외삽 prior-shift
    slope, intercept_fit = np.polyfit(SEASONS, RATES, 1)
    r_2025_target = slope * 2025 + intercept_fit
    r_source = RATES[-1]
    shift = np.log((r_2025_target * (1 - r_source)) / (r_source * (1 - r_2025_target)))
    print(f"step2(exp_023 style): 2025 외삽={r_2025_target:.4f} (2024 실제={r_source:.4f}), shift={shift:.5f}")

    new_calibrator = LogisticRegression()
    new_calibrator.coef_ = platt_recency.coef_.copy()
    new_calibrator.intercept_ = platt_recency.intercept_ + shift
    new_calibrator.classes_ = platt_recency.classes_.copy()
    new_calibrator.n_features_in_ = platt_recency.n_features_in_

    mean_after_step2 = new_calibrator.predict_proba(val_pred_2024.reshape(-1, 1))[:, 1].mean()
    print(f"  2024 예측에 적용 시 평균: {mean_after_step2:.4f} (2025 외삽 목표 {r_2025_target:.4f} 방향으로 이동 확인용, 2024 자체엔 미적용 목적)")

    meta["calibrator"] = new_calibrator
    meta["exp_id"] = "exp_027_season_state_calibrated_seedbag42_1"
    joblib.dump(meta, meta_path, compress=3)
    print(f"저장: {meta_path} (exp_id={meta['exp_id']})")
    print("완료.")


if __name__ == "__main__":
    main()
