# EXP_043 decision

- decision: `adopt`
- selected variant: `main77_reverse`
- based on run: `RUN_001`
- comparison basis: `EXP_042`
- reference variant: `batter_lags`
- decided at: `2026-08-17T19:28:41.212668+00:00`

## Ablation

CPU depth6 400 lr0.04를 고정하고 main60→main73→main77→main85→main87 핵심 누적 피처 단계만 비교

## Result

- selected Brier: `0.2469381307`
- delta Brier vs control: `-0.0008808973`
- competition score: `1148.405347731`

## Reason

CPU 결정론 검증에서 success rolling과 reverse short의 큰 개선이 재현됐고 main85·main87 추가는 악화되어 main77 확정
