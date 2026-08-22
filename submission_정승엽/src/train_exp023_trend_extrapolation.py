"""exp_023 -- extend exp_022's recency-weighted calibration ONE MORE
STEP: exp_022's calibrator effectively targets 2024's actual rate
(empirically confirmed: mean(calibrated preds on 2024)=0.48646 vs
actual 0.486105, essentially exact). But the season base-rate has been
falling every year (2019=0.565 -> 2024=0.486, see exp_022), and a
walk-forward check (using only data available at the time -- fit a
linear trend on seasons 1..k, extrapolate season k+1, compare to that
season's ACTUAL rate) shows trend-extrapolation is the best predictor
of the NEXT season's rate, and gets MORE accurate as more seasons
accumulate:

  predict 2021 (from 2019-2020): trend err=0.0320, last-season err=0.0000 (coincidence, 2020~2021 nearly equal)
  predict 2022 (from 2019-2021): trend err=0.0174, last-season err=0.0038
  predict 2023 (from 2019-2022): trend err=0.0130, last-season err=0.0290 (trend wins)
  predict 2024 (from 2019-2023): trend err=0.0057, last-season err=0.0139 (trend wins by 2.4x)

Both real cases with >=4 seasons of history (which is what we have for
predicting 2025, with 6) favor trend extrapolation over "just use the
last season". Linear trend on all 6 seasons (2019-2024) extrapolates
2025's rate to ~0.4747, vs 2024's actual 0.486105 -- a further ~1.1pp
downward shift beyond what exp_022 already captures.

This applies that as a PRIOR-SHIFT correction (label-shift adaptation,
standard technique for adjusting a classifier's output when the
deployment population's class prior differs from the calibration
population's): for a probability p calibrated to source rate r_s, the
probability re-targeted to a hypothesized deployment rate r_t is

    p' = p*(r_t/r_s) / [p*(r_t/r_s) + (1-p)*((1-r_t)/(1-r_s))]

Taking logit of both sides shows this is EXACTLY a constant additive
shift in logit space: logit(p') = logit(p) + log[r_t(1-r_s)/(r_s(1-r_t))].
Since exp_022's calibrator is already a 1-feature LogisticRegression
(Platt: sigmoid(slope*p + intercept)), this correction is applied by
building a NEW LogisticRegression with the SAME slope and an intercept
shifted by that constant -- no custom class needed, still a plain
sklearn object, safe to pickle/unpickle in submission/script.py exactly
like exp_018/019/022's calibrators.

No further CatBoost training or OOF computation needed -- this is a
pure closed-form adjustment of exp_022's already-fitted calibrator.
"""

import os

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

MODEL_DIR = "./model"

SEASONS = np.array([2019, 2020, 2021, 2022, 2023, 2024], dtype=float)
RATES = np.array([0.564670, 0.532712, 0.532762, 0.528920, 0.499957, 0.486105])


def main():
    slope, intercept = np.polyfit(SEASONS, RATES, 1)
    r_2025_target = slope * 2025 + intercept
    r_source = RATES[-1]  # exp_022's calibrator effectively targets 2024's rate (empirically confirmed 0.48646 vs actual 0.486105)
    print(f"선형 추세: slope={slope:.5f}/season, 2025 외삽={r_2025_target:.4f} (2024 실제={r_source:.4f})")

    meta_path = os.path.join(MODEL_DIR, "model_meta.pkl")
    meta = joblib.load(meta_path)
    assert meta["exp_id"] == "exp_022_recency_calibrated_seedbag42_1", meta["exp_id"]
    old_calibrator = meta["calibrator"]
    old_coef, old_intercept = old_calibrator.coef_, old_calibrator.intercept_
    print(f"exp_022 calibrator: coef={old_coef}, intercept={old_intercept}")

    shift = np.log((r_2025_target * (1 - r_source)) / (r_source * (1 - r_2025_target)))
    print(f"prior-shift 보정량(logit): {shift:.5f}")

    new_calibrator = LogisticRegression()
    new_calibrator.coef_ = old_coef.copy()
    new_calibrator.intercept_ = old_intercept + shift
    new_calibrator.classes_ = old_calibrator.classes_.copy()
    new_calibrator.n_features_in_ = old_calibrator.n_features_in_
    print(f"exp_023 calibrator(2025 외삽 반영): coef={new_calibrator.coef_}, intercept={new_calibrator.intercept_}")

    # sanity check: apply to the cached 2024 predictions, confirm the mean
    # shifts toward r_2025_target as intended (not evaluated as a "score"
    # since we have no 2025 labels -- this is a sanity/direction check only)
    val_pred_42 = np.load("./output/exp018_champion_val_pred_cache.npy")
    val_pred_1 = np.load("./output/exp019_champion_val_pred_seed1_cache.npy")
    val_pred_2024 = (val_pred_42 + val_pred_1) / 2
    old_mean = old_calibrator.predict_proba(val_pred_2024.reshape(-1, 1))[:, 1].mean()
    new_mean = new_calibrator.predict_proba(val_pred_2024.reshape(-1, 1))[:, 1].mean()
    print(f"2024 예측에 적용 시 평균: exp_022={old_mean:.4f} -> exp_023={new_mean:.4f} (목표 {r_2025_target:.4f} 방향)")

    meta["calibrator"] = new_calibrator
    meta["exp_id"] = "exp_023_trend_extrapolated_seedbag42_1"
    joblib.dump(meta, meta_path, compress=3)
    print(f"저장: {meta_path} (calibrator=2025 외삽 prior-shift 적용, 모델 파일은 exp_018/019/022와 동일)")


if __name__ == "__main__":
    main()
