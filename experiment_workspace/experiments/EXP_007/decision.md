# EXP_007 decision

- decision: `keep_control`
- selected variant: `catboost_control`
- based on run: `RUN_001`
- comparison basis: `EXP_006`
- reference variant: `d6_i300_control`
- decided at: `2026-08-17T15:57:40.342515+00:00`

## Ablation

main55를 고정하고 CatBoost, LightGBM, XGBoost 모델군과 대표 복잡도만 비교

## Result

- selected Brier: `0.2480092675`
- delta Brier vs control: `0.0`
- competition score: `719.6194426463`

## Reason

LightGBM과 XGBoost 대표 설정이 모두 CatBoost보다 악화되어 native CatBoost 유지
