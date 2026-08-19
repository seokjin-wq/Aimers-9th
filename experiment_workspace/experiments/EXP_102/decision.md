# EXP_102 decision

- decision: `adopt`
- selected variant: `w50_35_15`
- based on run: `RUN_001`
- comparison basis: `EXP_101`
- reference variant: `catshift_m0095`
- decided at: `2026-08-18T09:22:48.413539+00:00`

## Ablation

Keep all component models, features, CatBoost shift -0.0095, and train-only count-k500 calibration fixed; vary only CPU/GPU/ExtraTrees weights around 45/40/15.

## Result

- selected Brier: `0.2474713075`
- delta Brier vs control: `-5.567e-07`
- competition score: `934.9697691233`

## Reason

Using identical cached raw component predictions, CPU50/GPU35/Extra15 reduced Brier by 0.000000557 versus 45/40/15. Absolute BSS varied with the fresh GPU run, but the within-run weight comparison is isolated and valid; promote 50/35/15 for calibration-strength testing.
