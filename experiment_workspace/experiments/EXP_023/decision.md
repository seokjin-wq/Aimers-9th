# EXP_023 decision

- decision: `keep_control`
- selected variant: `catboost_control`
- based on run: `RUN_001`
- comparison basis: `EXP_022`
- reference variant: `default_control`
- decided at: `2026-08-17T17:33:04.693672+00:00`

## Ablation

같은 main60 정보에서 logistic C, HistGradientBoosting leaf 수, ExtraTrees leaf 크기만 비교

## Result

- selected Brier: `0.2478203209`
- delta Brier vs control: `0.0`
- competition score: `795.2564988937`

## Reason

모든 대체 모델 단독 점수가 CatBoost보다 낮았다. 다만 ExtraTrees leaf20은 CatBoost와 상관 0.807로 다양성이 있어 EXP_024 앙상블 후보로 넘긴다.
