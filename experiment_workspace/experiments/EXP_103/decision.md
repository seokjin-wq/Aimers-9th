# EXP_103 decision

- decision: `keep_control`
- selected variant: `residual_scale_1_control`
- based on run: `RUN_001`
- comparison basis: `EXP_102`
- reference variant: `w50_35_15`
- decided at: `2026-08-18T09:35:44.778171+00:00`

## Ablation

Keep features, component models, CPU50/GPU35/Extra15 weights, CatBoost shift -0.0095, count groups, and shrinkage 500 fixed; vary only residual_scale from 0.5 to 2.0.

## Result

- selected Brier: `0.247463289`
- delta Brier vs control: `0.0`
- competition score: `938.1796493859`

## Reason

Residual scale 1.0 remained best at BSS 938.180. Both attenuation (0.5, 0.75) and amplification (1.25, 1.5, 2.0) worsened Brier, so retain the original OOT count-offset amplitude.
