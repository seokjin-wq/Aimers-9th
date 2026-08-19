# EXP_026 decision

- decision: `adopt`
- selected variant: `count_k500`
- based on run: `RUN_001`
- comparison basis: `EXP_025`
- reference variant: `d6_i400_lr040`
- decided at: `2026-08-17T17:51:12.377913+00:00`

## Ablation

2019~2022→2023 OOF 잔차만 사용해 pitcher, batter, team, count별 shrinkage offset을 학습하고 2019~2023→2024 예측에 적용

## Result

- selected Brier: `0.2478180702`
- delta Brier vs control: `-9.578e-07`
- competition score: `796.1575008434`

## Reason

직전 시즌 선수·팀 잔차는 전이되지 않아 크게 악화했고, count 조합 보정만 Brier를 0.000000958 소폭 개선했다. 전체 최고는 EXP_024 앙상블이다.
