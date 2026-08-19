# EXP_123 decision

- decision: `keep_control`
- selected variant: `unconstrained_control`
- based on run: `RUN_001`
- comparison basis: `EXP_118`
- reference variant: `d8_i300_control`
- decided at: `2026-08-18T13:07:42.674605+00:00`

## Ablation

Fix main78 features and winning CPU parameters; add monotonic constraints only for success rates, only reverse/middle failure rates, or all four directional constraints.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `0.0`
- competition score: `928.2905828931`

## Reason

All EDA-guided monotonic constraints substantially worsened 2024 Brier, indicating conditional non-monotonicity already captured by the unconstrained model.
