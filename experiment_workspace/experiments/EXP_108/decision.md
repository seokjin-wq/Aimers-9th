# EXP_108 decision

- decision: `keep_control`
- selected variant: `main72_control`
- based on run: `RUN_001`
- comparison basis: `EXP_095`
- reference variant: `all_three`
- decided at: `2026-08-18T10:36:47.178817+00:00`

## Ablation

Keep latest CPU CatBoost and all main72 custom features fixed; restore exactly one excluded official raw column at a time.

## Result

- selected Brier: `0.2475118666`
- delta Brier vs control: `0.0`
- competition score: `918.7335789118`

## Reason

All six individually restored raw columns worsened 2024 holdout Brier; retain main72 control and do not combine negative candidates.
