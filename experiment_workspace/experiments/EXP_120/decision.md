# EXP_120 decision

- decision: `keep_control`
- selected variant: `categorical_control`
- based on run: `RUN_001`
- comparison basis: `EXP_118`
- reference variant: `d8_i300_control`
- decided at: `2026-08-18T12:41:29.196288+00:00`

## Ablation

Fix main78 features and all winning CPU parameters; change exactly one categorical-processing parameter per candidate: max_ctr_complexity=2, one_hot_max_size=5, or one_hot_max_size=16.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `0.0`
- competition score: `928.2905828931`

## Reason

Default CatBoost categorical processing remained best; richer CTR combinations and larger one-hot thresholds all worsened 2024 holdout Brier.
