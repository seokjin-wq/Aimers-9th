# EXP_110 decision

- decision: `keep_control`
- selected variant: `subsample_08_control`
- based on run: `RUN_001`
- comparison basis: `EXP_109`
- reference variant: `subsample_08`
- decided at: `2026-08-18T10:50:50.927587+00:00`

## Ablation

Fix the EXP_109 winning model and main72 features; vary only subsample across 0.75, 0.80, 0.85, and 0.90.

## Result

- selected Brier: `0.2475041715`
- delta Brier vs control: `0.0`
- competition score: `921.8140127173`

## Reason

The EXP_109 subsample=0.80 winner remained best; neighboring 0.75, 0.85, and 0.90 all worsened Brier, so keep 0.80.
