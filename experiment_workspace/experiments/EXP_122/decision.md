# EXP_122 decision

- decision: `keep_control`
- selected variant: `main78_control`
- based on run: `RUN_001`
- comparison basis: `EXP_114`
- reference variant: `reliability_k100_control`
- decided at: `2026-08-18T13:02:37.311712+00:00`

## Ablation

Fix main78 reliability CPU winner; add only ball/strike reliability-weighted rates, only three pitch-mix reliability-weighted rates, or all five.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `0.0`
- competition score: `928.2905828931`

## Reason

Reliability-weighted ball/strike rates, pitch-mix rates, and their union all worsened Brier; retain only the original six reliability features.
