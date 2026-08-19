# EXP_129 decision

- decision: `adopt`
- selected variant: `shrinkage_0`
- based on run: `RUN_001`
- comparison basis: `EXP_127`
- reference variant: `count_trend_strength_100`
- decided at: `2026-08-18T14:32:54.746337+00:00`

## Ablation

Fix EXP_127 trend strength 1.00 and every model/calibration setting; vary only count-trend shrinkage across 0, 2500, 5000, and control 10000.

## Result

- selected Brier: `0.2474451307`
- delta Brier vs control: `-1.78e-08`
- competition score: `945.4485865537`

## Reason

Zero shrinkage was consistently best in the diagnostic and same-run model comparison, simplifying the 12 high-support count trends, although the Brier gain over k=10000 is negligible (1.78e-8).
