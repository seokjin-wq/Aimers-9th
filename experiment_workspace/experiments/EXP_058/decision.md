# EXP_058 decision

- decision: `keep_control`
- selected variant: `main69_control`
- based on run: `RUN_001`
- comparison basis: `EXP_057`
- reference variant: `extra_w24`
- decided at: `2026-08-18T02:48:40.155312+00:00`

## Ablation

main69 CatBoost 대비 시즌-커리어 delta 7개, 최근폼 delta 3개, 전체 10개를 비교

## Result

- selected Brier: `0.2475992681`
- delta Brier vs control: `0.0`
- competition score: `883.7459693801`

## Reason

시즌-커리어 및 최근폼 차이를 명시한 모든 후보가 main69보다 악화되어 중복 상호작용을 제거하고 main69 유지
