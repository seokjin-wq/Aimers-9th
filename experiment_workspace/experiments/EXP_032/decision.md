# EXP_032 decision

- decision: `keep_control`
- selected variant: `global_control`
- based on run: `RUN_001`
- comparison basis: `EXP_031`
- reference variant: `ensemble_3seed`
- decided at: `2026-08-17T18:18:44.243421+00:00`

## Ablation

GPU CatBoost와 main60을 고정하고 game_type, top_bottom, pitcher_hand 및 game_type×pitcher_hand로 학습 데이터를 분리

## Result

- selected Brier: `0.2478182472`
- delta Brier vs control: `0.0`
- competition score: `796.0866345241`

## Reason

game_type, top_bottom, pitcher_hand 및 교차 분리는 모두 전역 GPU CatBoost보다 Brier가 악화되어 전역 모델 유지
