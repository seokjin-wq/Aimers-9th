# EXP_093 decision

- decision: `adopt`
- selected variant: `late_history`
- based on run: `RUN_001`
- comparison basis: `EXP_092`
- reference variant: `full_count_history`
- decided at: `2026-08-18T07:32:37.743670+00:00`

## Ablation

Fix same-hand CPU base; compare late-inning block, full-count block, and their six-feature union.

## Result

- selected Brier: `0.2475015773`
- delta Brier vs control: `-1.02894e-05`
- competition score: `922.8525101891`

## Reason

factorial 재검증에서 late-history 단독이 BSS 922.85로 다시 최고였고, full-count 단독 920.34 및 결합 909.79보다 우수했다. late-history만 유지한다.
