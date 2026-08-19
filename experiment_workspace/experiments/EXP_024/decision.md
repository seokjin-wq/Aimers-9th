# EXP_024 decision

- decision: `adopt`
- selected variant: `extra_w24`
- based on run: `RUN_001`
- comparison basis: `EXP_023`
- reference variant: `catboost_control`
- decided at: `2026-08-17T17:40:37.520132+00:00`

## Ablation

동일 main60에서 CatBoost와 ExtraTrees leaf20을 함께 학습하고 ExtraTrees 가중치 0.15~0.35만 변경

## Result

- selected Brier: `0.2477775942`
- delta Brier vs control: `-4.27267e-05`
- competition score: `812.3603933826`

## Reason

CatBoost 76% + ExtraTrees leaf20 24%가 Brier 0.2477775942, BSS 812.360으로 control보다 0.000042727 개선해 새 최고였다.
