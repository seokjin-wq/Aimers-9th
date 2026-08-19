# EXP_011 decision

- decision: `keep_control`
- selected variant: `uniform_control`
- based on run: `RUN_001`
- comparison basis: `EXP_009`
- reference variant: `count_control`
- decided at: `2026-08-17T16:15:54.621196+00:00`

## Ablation

main55+count와 CatBoost 구조를 고정하고 시즌이 한 해 과거로 갈 때의 sample weight decay만 1.0, 0.85, 0.70, 0.50, 0.25로 변경

## Result

- selected Brier: `0.2479681399`
- delta Brier vs control: `0.0`
- competition score: `736.0832056721`

## Reason

모든 최근성 decay가 균등 가중치보다 악화되어 2019~2023 동일 가중치를 유지
