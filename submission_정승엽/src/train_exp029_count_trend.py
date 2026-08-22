"""exp_029 -- count-state (balls_before, strikes_before) season-trend
post-hoc correction, ported from a teammate's EXP_127/130 (see this
project's teammate-analysis notes and experiments/exp_029_count_trend.md
for the full writeup). Layered ON TOP of exp_027's already-calibrated
predictions (exp_022 recency-weighted Platt + exp_023 trend-extrapolation
chain, already fit) -- this corrects a DIFFERENT axis (per-count-state
season drift not explained by the model+global calibration), distinct
from exp_027's per-PITCHER recency features.

Method (leak-safe, closed-form, no retraining):
1. Take exp_027's OOF predictions (2019-2023, 5-fold cross-fit) and the
   true out-of-sample 2024 predictions, run BOTH through the existing
   exp_027 calibrator (exp_022+023 chain) to get calibrated predictions
   for all 6 seasons.
2. residual = actual - calibrated_prediction, per row.
3. Center by season (subtract that season's mean residual) -- isolates
   the COUNT-STATE-SPECIFIC drift only, since the season-level average
   drift is already handled by exp_022/023's global calibration; adding
   it again here would double-count (confirmed empirically: an
   uncentered / raw-label-trend version of this experiment catastrophically
   overcorrected, see the writeup).
4. Per (balls_before, strikes_before) group, average the centered
   residual by season, fit OLS trend across seasons, extrapolate one
   step past the last available season.
5. Apply as a flat probability-space addition, strength=1.0 (the
   teammate's own un-tuned default -- deliberately not hand-optimizing
   the strength against the same holdout used to validate it).
"""

import os

import joblib
import numpy as np
import pandas as pd

from metrics import official_score

DATA_DIR = "./data"
MODEL_DIR = "./model"
GROUP_COLS = ["balls_before", "strikes_before"]
TREND_STRENGTH = 1.0


def compute_group_trend(residual_df, group_cols=GROUP_COLS, target_season=None):
    """residual_df must have columns group_cols + ['season', 'centered_residual'].
    Returns {group_key: predicted_centered_residual_at target_season}."""
    grp = residual_df.groupby(group_cols + ["season"])["centered_residual"].mean().reset_index()
    trend = {}
    for key, sub in grp.groupby(group_cols):
        sub = sub.sort_values("season")
        slope, intercept = np.polyfit(sub["season"], sub["centered_residual"], 1)
        trend[key] = slope * target_season + intercept
    return trend


def apply_group_trend(df, trend, group_cols=GROUP_COLS):
    keys = list(zip(*[df[c] for c in group_cols])) if len(group_cols) > 1 else df[group_cols[0]].tolist()
    return np.array([trend.get(k, 0.0) for k in keys])


def main():
    print("=" * 80)
    print("0. OOF + 2024 예측을 exp_027 calibrator로 보정, 잔차 계산")
    print("=" * 80)
    # ./model/model_meta.pkl was restored to exp_023 (safe default) after
    # exp_027 was archived -- read exp_027's calibrated meta from its own
    # archive instead of assuming it's still live in ./model/.
    meta = joblib.load("./submission/archive/exp027_season_state_calibrated/model/model_meta.pkl")
    assert meta["exp_id"] == "exp_027_season_state_calibrated_seedbag42_1", meta["exp_id"]
    calibrator = meta["calibrator"]

    train_full = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig",
                              usecols=["season", "control_success"] + GROUP_COLS)

    npz42 = np.load("./output/exp027_oof_cache_seed42.npz")
    npz1 = np.load("./output/exp027_oof_cache_seed1.npz")
    oof_raw = (npz42["pred"] + npz1["pred"]) / 2
    y_2319 = npz42["y"]
    train_2319 = train_full.loc[train_full["season"] < 2024].reset_index(drop=True)
    assert len(train_2319) == len(oof_raw)

    val42 = np.load("./output/exp027_val_pred_seed42.npy")
    val1 = np.load("./output/exp027_val_pred_seed1.npy")
    val_raw_2024 = (val42 + val1) / 2
    train_2024 = train_full.loc[train_full["season"] == 2024].reset_index(drop=True)
    y_2024 = train_2024["control_success"].to_numpy()
    assert len(train_2024) == len(val_raw_2024)

    oof_calibrated = calibrator.predict_proba(oof_raw.reshape(-1, 1))[:, 1]
    val_calibrated_2024 = calibrator.predict_proba(val_raw_2024.reshape(-1, 1))[:, 1]

    train_2319 = train_2319.copy()
    train_2319["residual"] = y_2319 - oof_calibrated
    train_2024 = train_2024.copy()
    train_2024["residual"] = y_2024 - val_calibrated_2024

    combined = pd.concat([train_2319, train_2024], ignore_index=True)
    season_mean_resid = combined.groupby("season")["residual"].transform("mean")
    combined["centered_residual"] = combined["residual"] - season_mean_resid

    baseline_brier, baseline_score = official_score(val_calibrated_2024, y_2024)
    print(f"baseline(exp_027 calibrated, count-trend 적용 전, 2024 held-out): score={baseline_score:.2f}")

    print()
    print("=" * 80)
    print("1. 2019-2023만으로 count-state trend 적합 -> 2024 예측(진짜 held-out 검증)")
    print("=" * 80)
    trend_2319_only = compute_group_trend(train_2319.assign(
        centered_residual=train_2319["residual"] - train_2319["season"].map(train_2319.groupby("season")["residual"].mean())
    ), target_season=2024)
    correction_2024 = apply_group_trend(train_2024, trend_2319_only)
    for strength in [0.5, 1.0, 1.5, 2.0]:
        adjusted = np.clip(val_calibrated_2024 + strength * correction_2024, 0.0, 1.0)
        brier, score = official_score(adjusted, y_2024)
        print(f"  strength={strength}: score={score:.2f}  Δ={score-baseline_score:+.2f}")

    print()
    print("=" * 80)
    print(f"2. 프로덕션용: 2019-2024 전체(OOF+2024 held-out 잔차)로 count-state trend 적합 -> 2025 외삽 (strength={TREND_STRENGTH})")
    print("=" * 80)
    trend_full = compute_group_trend(combined, target_season=2025)
    for key, v in sorted(trend_full.items()):
        print(f"  {GROUP_COLS}={key}: 2025 외삽 centered_residual={v:+.5f}")

    correction_dict_path = "./output/exp029_count_trend_2025.pkl"
    joblib.dump({"group_cols": GROUP_COLS, "trend": trend_full, "strength": TREND_STRENGTH}, correction_dict_path)
    print(f"저장: {correction_dict_path} (제출 파이프라인에서 사용)")

    print("\n완료.")


if __name__ == "__main__":
    main()
