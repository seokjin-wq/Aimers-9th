"""exp_030 baseline re-confirmation (not a new experiment number) --
compute ONE authoritative local held-out (2024) score for the actual
exp_030 production chain in a single run, instead of the "~828"
approximation in docs/current_best_pipeline.md (which sums exp_027's
818.30 and exp_029's +7.23, measured in two separate script runs).

Chain: exp_027 model (cached OOF/val predictions, no retraining needed)
-> step1-only Platt (train_exp027_calibration_final.py's step1, WITHOUT
   step2's 2025-extrapolation shift -- that shift is exactly what
   exp_030 removed, see experiments/exp_030_no_extrapolation.md)
-> exp_029's count-state trend correction (train_exp029_count_trend.py's
   compute_group_trend/apply_group_trend, reused verbatim -- exp_030's
   own writeup argues this correction is invariant to whether the
   calibrator's intercept carries a constant shift, since the trend
   fit centers by subtracting each season's mean residual: a uniform
   per-row shift cancels out in that subtraction. This script does not
   re-derive that argument, it inherits it).

This produces the single number every new exp_03X in this round should
diff against, replacing the "~828" approximation.
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from metrics import official_score
from train_exp029_count_trend import GROUP_COLS, TREND_STRENGTH, apply_group_trend, compute_group_trend

DATA_DIR = "./data"
WEIGHT_2024 = 100.0


def fit_platt_weighted(raw_pred, y, sample_weight, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y, sample_weight=sample_weight)
    return clf


def main():
    print("=" * 80)
    print("0. exp_027 캐시 로드 (재학습 없음)")
    print("=" * 80)
    npz42 = np.load("./output/exp027_oof_cache_seed42.npz")
    npz1 = np.load("./output/exp027_oof_cache_seed1.npz")
    oof_2319 = (npz42["pred"] + npz1["pred"]) / 2
    y_2319 = npz42["y"]

    val_pred_42 = np.load("./output/exp027_val_pred_seed42.npy")
    val_pred_1 = np.load("./output/exp027_val_pred_seed1.npy")
    val_raw_2024 = (val_pred_42 + val_pred_1) / 2

    train_full = pd.read_csv(
        os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig",
        usecols=["season", "control_success"] + GROUP_COLS,
    )
    y_2024 = train_full.loc[train_full["season"] == 2024, "control_success"].to_numpy()
    assert len(val_raw_2024) == len(y_2024)
    print(f"raw 2024 예측 평균={val_raw_2024.mean():.4f}, 실제 2024 rate={y_2024.mean():.4f}")

    print()
    print("=" * 80)
    print("1. step1-only Platt (exp_022 style, weight=100, exp_023 추세외삽 없음 -- exp_030과 동일)")
    print("=" * 80)
    p_combo = np.concatenate([oof_2319, val_raw_2024])
    y_combo = np.concatenate([y_2319, y_2024])
    sw = np.concatenate([np.ones(len(oof_2319)), np.full(len(val_raw_2024), WEIGHT_2024)])
    calibrator = fit_platt_weighted(p_combo, y_combo, sample_weight=sw, seed=42)
    print(f"coef={calibrator.coef_}, intercept={calibrator.intercept_}")

    oof_calibrated = calibrator.predict_proba(oof_2319.reshape(-1, 1))[:, 1]
    val_calibrated_2024 = calibrator.predict_proba(val_raw_2024.reshape(-1, 1))[:, 1]
    print(f"2024 보정 예측 평균={val_calibrated_2024.mean():.4f} (목표: 실제 rate {y_2024.mean():.4f})")

    step1_brier, step1_score = official_score(val_calibrated_2024, y_2024)
    print(f"[step1 only, count-trend 적용 전] Brier={step1_brier:.6f} | score={step1_score:.2f}")

    print()
    print("=" * 80)
    print("2. count-state 추세 보정 추가 (2019-2023 잔차로 적합 -> 2024 진짜 held-out 검증)")
    print("=" * 80)
    train_2319 = train_full.loc[train_full["season"] < 2024].reset_index(drop=True)
    assert len(train_2319) == len(oof_calibrated)
    train_2319 = train_2319.copy()
    train_2319["residual"] = y_2319 - oof_calibrated
    train_2319["centered_residual"] = (
        train_2319["residual"] - train_2319["season"].map(train_2319.groupby("season")["residual"].mean())
    )

    train_2024 = train_full.loc[train_full["season"] == 2024].reset_index(drop=True)
    trend_2319_only = compute_group_trend(train_2319, target_season=2024)
    correction_2024 = apply_group_trend(train_2024, trend_2319_only)
    final_pred = np.clip(val_calibrated_2024 + TREND_STRENGTH * correction_2024, 0.0, 1.0)
    final_brier, final_score = official_score(final_pred, y_2024)
    print(f"[step1 + count-trend(strength={TREND_STRENGTH})] Brier={final_brier:.6f} | score={final_score:.2f}")
    print(f"count-trend 기여분: Δ={final_score - step1_score:+.2f}")

    print()
    print("=" * 80)
    print(f"exp_030_repro 최종 기준선: score={final_score:.2f} (Brier={final_brier:.6f})")
    print("=" * 80)
    print("이후 모든 exp_03X 실험은 이 숫자와 비교할 것 (docs의 '~828' 근사치 대신).")


if __name__ == "__main__":
    main()
