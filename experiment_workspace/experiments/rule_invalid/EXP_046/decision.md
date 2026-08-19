# EXP_046 decision

- decision: `keep_control`
- selected variant: `cat_control`
- based on run: `RUN_001`
- comparison basis: `EXP_045`
- reference variant: `best_three`
- decided at: `2026-08-17T19:51:49.269181+00:00`

## Ablation

main80을 고정하고 CPU CatBoost 대비 LightGBM leaves31·63·127, HistGB leaves31·63, Logistic C0.01만 변경

## Result

- selected Brier: `0.2469303451`
- delta Brier vs control: `0.0`
- competition score: `1151.5219637307`

## Reason

모든 이종 모델 단독이 악화했고 저장 예측 최적 혼합도 BSS 1165.37로 CatBoost 대비 이득이 작아 CPU CatBoost 유지
