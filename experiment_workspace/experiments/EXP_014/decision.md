# EXP_014 decision

- decision: `keep_control`
- selected variant: `main60_control`
- based on run: `RUN_001`
- comparison basis: `EXP_013`
- reference variant: `catboost_logloss_control`
- decided at: `2026-08-17T16:30:49.610701+00:00`

## Ablation

native CatBoost를 고정하고 저중요도 context, 최근-gap, 기존 custom 전체, count 중복을 각각 제거

## Result

- selected Brier: `0.2479681399`
- delta Brier vs control: `0.0`
- competition score: `736.0832056721`

## Reason

모든 파생 피처 pruning이 main55+count보다 악화되어 전체 19개 파생을 유지
