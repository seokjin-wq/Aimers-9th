# EXP_059 decision

- decision: `adopt`
- selected variant: `d8_i300`
- based on run: `RUN_001`
- comparison basis: `EXP_057`
- reference variant: `extra_w24`
- decided at: `2026-08-18T02:55:05.961751+00:00`

## Ablation

main69 고정 후 depth5~8, 300~600 trees의 기존 결정론적 CPU 후보만 재비교

## Result

- selected Brier: `0.2475677481`
- delta Brier vs control: `-3.152e-05`
- competition score: `896.3637145626`

## Reason

main69에서 depth8 300 lr0.035가 CatBoost Brier를 0.000031520 개선해 새 최적 CatBoost 구성요소로 채택; 전체 최고는 EXP_057 앙상블
