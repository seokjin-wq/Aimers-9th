# EXP_066 decision

- decision: `keep_control`
- selected variant: `catboost_control`
- based on run: `RUN_001`
- comparison basis: `EXP_062`
- reference variant: `extra_w18`
- decided at: `2026-08-18T03:36:17.092592+00:00`

## Ablation

main69 고정 후 CatBoost, HistGradientBoosting, LightGBM, XGBoost 대표 설정 비교

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

main69에서 HistGB, LightGBM, XGBoost 단독이 모두 CatBoost보다 크게 악화되어 주력 모델은 CatBoost 유지; Hist63은 소량 앙상블 다양성 후보만 보존
