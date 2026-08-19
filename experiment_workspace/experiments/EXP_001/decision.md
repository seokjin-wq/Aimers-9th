# EXP_001 decision

- decision: `adopt`
- selected variant: `catboost_raw47`
- based on run: `RUN_001`
- comparison basis: `BASELINE_001_main55`
- reference variant: `random_forest_raw47`
- decided at: `2026-08-17T15:11:52.338881+00:00`

## Ablation

제공 raw47을 고정하고 RandomForest 대비 CatBoost 모델군 변경 효과를 검증

## Result

- selected Brier: `0.248072725`
- delta Brier vs control: `-0.0006960696`
- competition score: `694.2168600737`

## Reason

동일 raw47에서 CatBoost가 RandomForest 대비 2024 홀드아웃 Brier를 0.000696070 개선해 채택
