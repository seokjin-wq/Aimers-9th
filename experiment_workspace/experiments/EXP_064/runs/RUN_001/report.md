# 064_stable_context_target_effects: 안정 상황 교차 타깃 효과

- 가설: 선수 ID 대신 표본이 큰 count·hand·base·inning 교차의 시즌 중심화 학습 효과가 CatBoost의 상호작용 추정을 보완한다
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b4eedcce2da1`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main69_control | control: EXP_060 최고 CatBoost | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| count_out_base | 볼카운트×아웃×주자상태 학습 효과 추가 | 0.370355395 | 0.122817674 | 0/1 | 0.000 |
| count_hands | 볼카운트×투수손×타자손 학습 효과 추가 | 0.491125712 | 0.243587992 | 0/1 | 0.000 |
| all_context | 네 가지 시즌 중심화 상황 교차 효과를 모두 추가 | 0.499298828 | 0.251761107 | 0/1 | 0.000 |
| game_pressure | 이닝×공수×경기유형과 압박상태 효과 추가 | 0.507969187 | 0.260431467 | 0/1 | 0.000 |

## 실제 변경 필드

- `main69_control`: control
- `count_hands`: features.custom, features.description, features.expected_count, features.name
- `count_out_base`: features.custom, features.description, features.expected_count, features.name
- `game_pressure`: features.custom, features.description, features.expected_count, features.name
- `all_context`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/064_stable_context_target_effects/20260818T032225118287Z_b4eedcce2da1`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_062`
- 기준 variant: `extra_w18`
- 검증할 변경: main69 decay85 대비 count×hands, count×out×base, inning/game+pressure, 전체 네 효과를 비교

### main69_control

- role: control

### count_hands

- declared change: 볼카운트×투수손×타자손 학습 효과 추가
- added features: `count_hands_target_effect`
- removed features: none
- model changes: none

### count_out_base

- declared change: 볼카운트×아웃×주자상태 학습 효과 추가
- added features: `count_out_base_target_effect`
- removed features: none
- model changes: none

### game_pressure

- declared change: 이닝×공수×경기유형과 압박상태 효과 추가
- added features: `inning_game_target_effect`, `pressure_state_target_effect`
- removed features: none
- model changes: none

### all_context

- declared change: 네 가지 시즌 중심화 상황 교차 효과를 모두 추가
- added features: `count_hands_target_effect`, `count_out_base_target_effect`, `inning_game_target_effect`, `pressure_state_target_effect`
- removed features: none
- model changes: none
