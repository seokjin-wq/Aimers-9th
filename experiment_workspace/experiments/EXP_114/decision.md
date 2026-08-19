# EXP_114 decision

- decision: `keep_control`
- selected variant: `reliability_k100_control`
- based on run: `RUN_001`
- comparison basis: `EXP_113`
- reference variant: `all_six_control`
- decided at: `2026-08-18T11:32:24.266918+00:00`

## Ablation

Fix all main72 features and CPU subsample=0.8; change only the denominator k used in the same six reliability features across 50, 100, and 200.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `0.0`
- competition score: `928.2905828931`

## Reason

Reliability k=100 remained clearly best; both k=50 and k=200 worsened Brier by more than 4e-05, so retain k=100.
