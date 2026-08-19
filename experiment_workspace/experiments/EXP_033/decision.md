# EXP_033 decision

- decision: `keep_control`
- selected variant: `global_control`
- based on run: `RUN_001`
- comparison basis: `EXP_032`
- reference variant: `global_control`
- decided at: `2026-08-17T18:22:03.782815+00:00`

## Ablation

CatBoost와 main60을 고정하고 2019~2022→2023 예측에서 학습한 mean-shift, affine, Platt, beta, isotonic 보정만 변경

## Result

- selected Brier: `0.2478144436`
- delta Brier vs control: `0.0`
- competition score: `797.6092695832`

## Reason

2023 OOT에서 학습한 모든 확률 보정이 2024 Brier를 악화시켜 직접 affine 보정 기준을 유지
