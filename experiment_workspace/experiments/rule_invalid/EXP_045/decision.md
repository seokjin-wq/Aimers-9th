# EXP_045 decision

- decision: `adopt`
- selected variant: `best_three`
- based on run: `RUN_002`
- comparison basis: `EXP_044`
- reference variant: `main77_control`
- decided at: `2026-08-17T20:54:35.498891+00:00`

## Ablation

CPU main77을 고정하고 투수 success EWMA 0.05·0.10, 타자 success EWMA 0.10·0.20, 투수 reverse EWMA 0.05·0.10만 개별·조합 추가

## Result

- selected Brier: `0.2469303451`
- delta Brier vs control: `-7.7855e-06`
- competition score: `1151.5219637307`

## Reason

RUN_002 CPU 재현에서도 세 EWMA 조합이 Brier 7.79e-6 개선되어 best_three 채택
