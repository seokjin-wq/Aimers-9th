# EXP_121 decision

- decision: `keep_control`
- selected variant: `hist_weight_0_control`
- based on run: `RUN_001`
- comparison basis: `EXP_117`
- reference variant: `weights_50_35_15`
- decided at: `2026-08-18T12:57:09.085371+00:00`

## Ablation

Fix main78 features, CPU/GPU weights 50/35, all component parameters and calibration; replace only 0%, 2.5%, or 5% of the ExtraTrees weight with a fixed HistGB component trained on official pre-validation data.

## Result

- selected Brier: `0.2474514942`
- delta Brier vs control: `0.0`
- competition score: `942.9012125876`

## Reason

With identical cached raw predictions, replacing ExtraTrees weight with 2.5% or 5% HistGB worsened Brier; retain the three-model 50/35/15 blend.
