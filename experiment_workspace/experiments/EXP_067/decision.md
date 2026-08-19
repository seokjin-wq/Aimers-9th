# EXP_067 decision

- decision: `reject`
- selected variant: `base_control`
- based on run: `RUN_001`
- comparison basis: `EXP_062`
- reference variant: `extra_w18`
- decided at: `2026-08-18T03:40:49.052922+00:00`

## Ablation

main69 depth8 decay85 base 고정, 2023 잔차모델 보정 가중치 0.25,0.5,0.75,1.0 비교

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

2019~2022→2023 잔차 CatBoost 패턴이 2024에 전이되지 않아 25% 보정부터 Brier 0.000187758 악화; 잔차 보정 전체 기각
