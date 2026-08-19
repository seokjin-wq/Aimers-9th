# EXP_130 decision

- decision: `adopt`
- selected variant: `ols_slope`
- based on run: `RUN_001`
- comparison basis: `EXP_129`
- reference variant: `shrinkage_0`
- decided at: `2026-08-18T14:47:44.158894+00:00`

## Ablation

Fix EXP_129 shrinkage 0, trend strength 1.0, features, models, weights, and calibration; vary only count trend estimator among WLS, OLS, and first-to-last endpoint slope.

## Result

- selected Brier: `0.2474451493`
- delta Brier vs control: `-5.03e-08`
- competition score: `945.4411373303`

## Reason

Equal-season OLS matched the prior train/validation diagnostic and slightly improved same-run Brier by 5.03e-8; endpoint extrapolation worsened. Adopt OLS, while noting the estimator gain is negligible versus the material EXP_127 trend gain.
