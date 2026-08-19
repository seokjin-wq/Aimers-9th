# EXP_119 decision

- decision: `keep_control`
- selected variant: `catshift_m0095_control`
- based on run: `RUN_001`
- comparison basis: `EXP_117`
- reference variant: `weights_50_35_15`
- decided at: `2026-08-18T12:36:03.825777+00:00`

## Ablation

Fix main78 features, component models, 50/35/15 weights, ExtraTrees shift, count correction, and scales; vary only CatBoost component shift among -0.0090, -0.0095, and -0.0100.

## Result

- selected Brier: `0.2474516579`
- delta Brier vs control: `0.0`
- competition score: `942.8357059559`

## Reason

The existing cat_shift=-0.0095 remained best on the reliability-enhanced 50/35/15 blend; neighboring -0.0090 and -0.0100 both worsened Brier.
