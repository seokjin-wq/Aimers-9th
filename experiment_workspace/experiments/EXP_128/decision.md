# EXP_128 decision

- decision: `keep_control`
- selected variant: `strength_100_control`
- based on run: `RUN_001`
- comparison basis: `EXP_127`
- reference variant: `count_trend_strength_100`
- decided at: `2026-08-18T14:17:56.069758+00:00`

## Ablation

Fix EXP_127 model, features, count trend groups, trend shrinkage, and all calibration; vary only trend_strength around 1.00 using 0.75, 1.00, 1.25, and 1.50.

## Result

- selected Brier: `0.2474502158`
- delta Brier vs control: `0.0`
- competition score: `943.4129545237`

## Reason

Same-run refinement confirmed trend_strength=1.00: both 0.75 and 1.25 were slightly worse and 1.50 degraded further, so retain the safer full one-season trend without extrapolation.
