# EXP_127 decision

- decision: `adopt`
- selected variant: `count_trend_strength_100`
- based on run: `RUN_001`
- comparison basis: `EXP_117`
- reference variant: `weights_50_35_15`
- decided at: `2026-08-18T14:04:03.738463+00:00`

## Ablation

Fix main78, all three component models, 50/35/15 weights, affine shifts, and OOT count residual; add only an official-train-only centered count trend offset at strengths 0.25, 0.50, or 1.00.

## Result

- selected Brier: `0.2474451414`
- delta Brier vs control: `-6.3762e-06`
- competition score: `945.4443110442`

## Reason

All train-only count-trend strengths improved 2024 Brier monotonically; full strength achieved the best Brier 0.2474451414 and BSS 945.444 without using any evaluation-row aggregate.
