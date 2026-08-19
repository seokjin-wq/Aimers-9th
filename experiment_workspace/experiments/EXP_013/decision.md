# EXP_013 decision

- decision: `keep_control`
- selected variant: `catboost_logloss_control`
- based on run: `RUN_001`
- comparison basis: `EXP_012`
- reference variant: `default_control`
- decided at: `2026-08-17T16:25:32.898820+00:00`

## Ablation

main55+count를 고정하고 CatBoost/LightGBM/XGBoost의 분류 Logloss와 회귀 squared-error 목적을 비교

## Result

- selected Brier: `0.2479681399`
- delta Brier vs control: `0.0`
- competition score: `736.0832056721`

## Reason

CatBoost, LightGBM, XGBoost 회귀형 squared-error 목적이 모두 Logloss 분류보다 악화되어 분류 목적 유지
