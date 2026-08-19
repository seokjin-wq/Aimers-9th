# EXP_116 decision

- decision: `adopt`
- selected variant: `triple_history_reliability`
- based on run: `RUN_001`
- comparison basis: `EXP_111`
- reference variant: `triple_cpu_sub08`
- decided at: `2026-08-18T12:02:41.899080+00:00`

## Ablation

Keep the full EXP_111 triple model, CPU subsample=0.8, weights, calibration, and count residual correction fixed; change only main72 versus main78 reliability features.

## Result

- selected Brier: `0.2474572802`
- delta Brier vs control: `-1.0636e-06`
- competition score: `940.5850213257`

## Reason

Reliability features improved same-run triple Brier by 1.064e-06 and were independently supported by a 1.618e-05 CPU gain; adopt as a cautious new compliant best BSS 940.585.
