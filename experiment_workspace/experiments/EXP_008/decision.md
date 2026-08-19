# EXP_008 decision

- decision: `adopt`
- selected variant: `add_count_state`
- based on run: `RUN_001`
- comparison basis: `EXP_007`
- reference variant: `catboost_control`
- decided at: `2026-08-17T16:01:00.389279+00:00`

## Ablation

native CatBoost를 고정하고 EDA 제안 피처를 결측, 스무딩, 경기 맥락, 카운트 묶음별로 각각 추가

## Result

- selected Brier: `0.2479681399`
- delta Brier vs control: `-4.11276e-05`
- competition score: `736.0832056721`

## Reason

카운트·아웃 상태 5개가 Brier를 0.000041128 개선해 단일 묶음 최선으로 채택; 스무딩과 결측 플래그도 후속 조합 후보로 유지
