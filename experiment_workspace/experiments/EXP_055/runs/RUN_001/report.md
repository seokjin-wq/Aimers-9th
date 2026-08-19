# 055_official_train_target_effects: 공식 학습 타깃 효과 피처

- 가설: 공식 학습 행에서만 계산한 leave-one-out 투수·타자·팀 효과가 숫자 ID를 직접 쓰는 CatBoost보다 2024 일반화를 개선한다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `04f9e23432c8`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main60_control | control: 합법 main60 CatBoost | 0.247820321 | 0.000000000 | 0/1 | 795.256 |
| pitcher_te50 | 공식 학습 타깃만 사용한 투수 LOO 효과(k=50) 1개 추가 | 0.290860151 | 0.043039830 | 0/1 | 0.000 |
| pitcher_batter_te50 | 투수와 타자 LOO 효과(k=50) 2개 추가 | 0.313031074 | 0.065210753 | 0/1 | 0.000 |
| all_entity_team_te | 투수·타자 효과(k=50)와 양 팀 효과(k=500) 4개 추가 | 0.513471264 | 0.265650943 | 0/1 | 0.000 |

## 실제 변경 필드

- `main60_control`: control
- `pitcher_te50`: features.custom, features.description, features.expected_count, features.name
- `pitcher_batter_te50`: features.custom, features.description, features.expected_count, features.name
- `all_entity_team_te`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/055_official_train_target_effects/20260818T022851324150Z_04f9e23432c8`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_054`
- 기준 variant: `extra_w24_safe`
- 검증할 변경: main60 CatBoost를 고정하고 official-train-only 투수 TE, 투수+타자 TE, 투수+타자+팀 TE만 단계적으로 추가

### main60_control

- role: control

### pitcher_te50

- declared change: 공식 학습 타깃만 사용한 투수 LOO 효과(k=50) 1개 추가
- added features: `pitcher_target_effect_k50`
- removed features: none
- model changes: none

### pitcher_batter_te50

- declared change: 투수와 타자 LOO 효과(k=50) 2개 추가
- added features: `pitcher_target_effect_k50`, `batter_target_effect_k50`
- removed features: none
- model changes: none

### all_entity_team_te

- declared change: 투수·타자 효과(k=50)와 양 팀 효과(k=500) 4개 추가
- added features: `pitcher_target_effect_k50`, `batter_target_effect_k50`, `pitcher_team_target_effect_k500`, `batter_team_target_effect_k500`
- removed features: none
- model changes: none
