# EXP_048 decision

- decision: `adopt`
- selected variant: `global200`
- based on run: `RUN_001`
- comparison basis: `EXP_047`
- reference variant: `global100`
- decided at: `2026-08-17T20:04:30.257703+00:00`

## Ablation

CPU main80과 전역 단일 rolling 구조를 고정하고 window 75·100·125·150·200만 변경

## Result

- selected Brier: `0.2466972461`
- delta Brier vs control: `-2.82507e-05`
- competition score: `1244.8336355977`

## Reason

window가 100→150→200으로 갈수록 CPU Brier가 개선되어 window200, BSS 1244.83 채택
