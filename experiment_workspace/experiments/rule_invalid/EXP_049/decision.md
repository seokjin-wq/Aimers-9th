# EXP_049 decision

- decision: `keep_control`
- selected variant: `global200_control`
- based on run: `RUN_001`
- comparison basis: `EXP_048`
- reference variant: `global200`
- decided at: `2026-08-17T20:20:56.974751+00:00`

## Ablation

CPU main80과 전역 단일 rolling을 고정하고 window 175·200·225·250·300·400만 변경

## Result

- selected Brier: `0.2466972461`
- delta Brier vs control: `0.0`
- competition score: `1244.8336355977`

## Reason

window175~400 탐색에서 window200의 Brier 0.2466972461가 최저였으므로 유지
