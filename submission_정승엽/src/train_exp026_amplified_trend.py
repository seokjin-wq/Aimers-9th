"""exp_026 -- amplify exp_023's trend-extrapolation prior-shift by a
fixed factor ALPHA, motivated by a genuine backtest (see
experiments/exp_026_amplified_trend.md): simulating "as if 2024 were
still unknown" (fit calibrator on 2019-2023 OOF only, trend-extrapolate
2019-2023's season rates to a 2024 estimate, apply as a prior-shift, then
score against 2024's REAL held-out labels) shows plain 1x trend
extrapolation captures only part of the available correction (+9.29 vs a
no-drift-correction baseline) while the oracle upper bound (shifting all
the way to 2024's true rate) reaches +22.69 -- because the plain linear
trend UNDERSHOT how far 2024's rate actually fell. Moderate amplification
(alpha=1.5, i.e. 50% more shift than plain exp_023) recovers about 40% of
that extra gap (+13.02) in the same backtest.

IMPORTANT CAVEAT (communicated to the user): this is a single historical
instance (2024 is the only season with both a real cached champion
model AND real ground truth to check against) -- there is no guarantee
the same undershoot direction/magnitude repeats for 2025. This script
produces a SEPARATE archive, not a change to the default submit.zip
(which stays on exp_023's plain, less aggressive shift) -- explicitly
so the safer exp_023 gets tested on the real leaderboard first before
committing to a more aggressive, less-validated correction.

Mechanically: model_meta.pkl currently holds exp_023's calibrator
(old_intercept = exp_022_intercept + 1x*shift). This adds
(ALPHA-1)*shift on top, so the final intercept = exp_022_intercept +
ALPHA*shift -- exactly the same closed-form prior-shift construction as
exp_023, just scaled.
"""

import os

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

MODEL_DIR = "./model"
ALPHA = 1.5

SEASONS = np.array([2019, 2020, 2021, 2022, 2023, 2024], dtype=float)
RATES = np.array([0.564670, 0.532712, 0.532762, 0.528920, 0.499957, 0.486105])


def main():
    slope, intercept_fit = np.polyfit(SEASONS, RATES, 1)
    r_2025_target = slope * 2025 + intercept_fit
    r_source = RATES[-1]
    shift_1x = np.log((r_2025_target * (1 - r_source)) / (r_source * (1 - r_2025_target)))
    print(f"1x shift(exp_023와 동일)={shift_1x:.5f}, ALPHA={ALPHA} -> 최종 배율 shift={ALPHA*shift_1x:.5f}")

    meta_path = os.path.join(MODEL_DIR, "model_meta.pkl")
    meta = joblib.load(meta_path)
    assert meta["exp_id"] == "exp_023_trend_extrapolated_seedbag42_1", (
        f"model/model_meta.pkl가 exp_023 상태가 아님({meta['exp_id']}) -- "
        "먼저 train_exp023_trend_extrapolation.py를 실행해 exp_023 상태로 되돌린 뒤 이 스크립트를 실행할 것"
    )
    exp023_calibrator = meta["calibrator"]
    extra_shift = (ALPHA - 1.0) * shift_1x
    print(f"exp_023 calibrator: coef={exp023_calibrator.coef_}, intercept={exp023_calibrator.intercept_}")
    print(f"추가로 더할 shift(=({ALPHA}-1)*1x shift)={extra_shift:.5f}")

    new_calibrator = LogisticRegression()
    new_calibrator.coef_ = exp023_calibrator.coef_.copy()
    new_calibrator.intercept_ = exp023_calibrator.intercept_ + extra_shift
    new_calibrator.classes_ = exp023_calibrator.classes_.copy()
    new_calibrator.n_features_in_ = exp023_calibrator.n_features_in_
    print(f"exp_026 calibrator(x{ALPHA} 증폭): coef={new_calibrator.coef_}, intercept={new_calibrator.intercept_}")

    val_pred_42 = np.load("./output/exp018_champion_val_pred_cache.npy")
    val_pred_1 = np.load("./output/exp019_champion_val_pred_seed1_cache.npy")
    val_pred_2024 = (val_pred_42 + val_pred_1) / 2
    old_mean = exp023_calibrator.predict_proba(val_pred_2024.reshape(-1, 1))[:, 1].mean()
    new_mean = new_calibrator.predict_proba(val_pred_2024.reshape(-1, 1))[:, 1].mean()
    print(f"2024 예측에 적용 시 평균: exp_023={old_mean:.4f} -> exp_026={new_mean:.4f}")

    meta["calibrator"] = new_calibrator
    meta["exp_id"] = f"exp_026_amplified_trend_x{ALPHA}_seedbag42_1"
    joblib.dump(meta, meta_path, compress=3)
    print(f"저장: {meta_path} (calibrator=exp_023 shift x{ALPHA} 증폭, 모델 파일은 이전과 동일)")


if __name__ == "__main__":
    main()
