# 017_count_feature_contribution: 카운트 피처 개별 기여

- 가설: 카운트 파생 5개 중 일부가 개선 대부분을 만들며 count_state 범주화가 추가 개선한다
- control: `main55_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `720c21176a5c`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| all_count_numeric | count 5개 전체 numeric | 0.247875492 | -0.000045205 | 1/1 | 773.171 |
| add_two_outs | has_two_outs 단독 추가 | 0.247891660 | -0.000029038 | 1/1 | 766.699 |
| main55_control | control: main55 + shift | 0.247920697 | 0.000000000 | 0/1 | 755.075 |
| add_two_strikes | has_two_strikes 단독 추가 | 0.247929754 | 0.000009057 | 0/1 | 751.449 |
| add_three_balls | has_three_balls 단독 추가 | 0.247942085 | 0.000021388 | 0/1 | 746.513 |
| add_count_state | count_state 단독 추가 | 0.247943049 | 0.000022352 | 0/1 | 746.127 |
| count_state_categorical | count 5개 전체에서 count_state만 native categorical | 0.247953241 | 0.000032544 | 0/1 | 742.047 |
| add_full_count | is_full_count 단독 추가 | 0.247960245 | 0.000039548 | 0/1 | 739.244 |

## 실제 변경 필드

- `main55_control`: control
- `add_count_state`: features.custom, features.description, features.expected_count, features.name
- `add_full_count`: features.custom, features.description, features.expected_count, features.name
- `add_two_strikes`: features.custom, features.description, features.expected_count, features.name
- `add_three_balls`: features.custom, features.description, features.expected_count, features.name
- `add_two_outs`: features.custom, features.description, features.expected_count, features.name
- `all_count_numeric`: features.custom, features.description, features.expected_count, features.name
- `count_state_categorical`: features.categorical, features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/017_count_feature_contribution/20260817T164028054754Z_720c21176a5c`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_016`
- 기준 variant: `single_seed_control`
- 검증할 변경: shifted native CatBoost와 main55를 고정하고 count_state, full count, 2-strike, 3-ball, 2-out을 각각 단독 추가하고 전체 count_state 범주화 비교

### main55_control

- role: control

### add_count_state

- declared change: count_state 단독 추가
- added features: `count_state`
- removed features: none
- model changes: none

### add_full_count

- declared change: is_full_count 단독 추가
- added features: `is_full_count`
- removed features: none
- model changes: none

### add_two_strikes

- declared change: has_two_strikes 단독 추가
- added features: `has_two_strikes`
- removed features: none
- model changes: none

### add_three_balls

- declared change: has_three_balls 단독 추가
- added features: `has_three_balls`
- removed features: none
- model changes: none

### add_two_outs

- declared change: has_two_outs 단독 추가
- added features: `has_two_outs`
- removed features: none
- model changes: none

### all_count_numeric

- declared change: count 5개 전체 numeric
- added features: `count_state`, `is_full_count`, `has_two_strikes`, `has_three_balls`, `has_two_outs`
- removed features: none
- model changes: none

### count_state_categorical

- declared change: count 5개 전체에서 count_state만 native categorical
- added features: `count_state`, `is_full_count`, `has_two_strikes`, `has_three_balls`, `has_two_outs`
- removed features: none
- model changes: none
