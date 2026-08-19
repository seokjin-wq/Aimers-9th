# 081_composite_count_states: 행 단위 복합 카운트 상태 범주

- 가설: 카운트와 손·아웃 상호작용을 하나의 복합 범주로 직접 표현하면 separate categorical보다 ordered statistics가 안정적으로 학습된다.
- control: `separate_count_hands_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `7f4cf5ecfd0a`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| separate_count_hands_control | control: count_state와 양손을 separate categorical | 0.247515859 | 0.000000000 | 0/1 | 917.136 |
| count_hands_out_plus | control에 count×양손×outs 복합 범주 추가 | 0.247548204 | 0.000032346 | 0/1 | 904.187 |
| count_hands_composite_only | separate categorical 대신 count×양손 복합 범주만 추가 | 0.247559225 | 0.000043367 | 0/1 | 899.775 |
| count_out_plus | control에 count×outs 복합 범주 추가 | 0.247565626 | 0.000049768 | 0/1 | 897.213 |
| count_hands_composite_plus | control에 count×양손 복합 범주 추가 | 0.247574276 | 0.000058418 | 0/1 | 893.750 |
| count_hands_out_only | count×양손×outs 복합 범주만 추가 | 0.247579132 | 0.000063274 | 0/1 | 891.806 |
| count_matchup_composite | count×동일손 여부 복합 범주만 추가 | 0.247598353 | 0.000082494 | 0/1 | 884.112 |

## 실제 변경 필드

- `separate_count_hands_control`: control
- `count_hands_composite_only`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `count_hands_composite_plus`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `count_matchup_composite`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `count_out_plus`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `count_hands_out_only`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `count_hands_out_plus`: features.categorical, features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/081_composite_count_states/20260818T053140084814Z_7f4cf5ecfd0a`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_080`
- 기준 variant: `count_hands_promoted`
- 검증할 변경: Screen composite count×hands, count×same-hand, count×outs, and count×hands×outs categories, alone or alongside the EXP_078 separate categories.

### separate_count_hands_control

- role: control

### count_hands_composite_only

- declared change: separate categorical 대신 count×양손 복합 범주만 추가
- added features: `count_hands_state`
- removed features: none
- model changes: none

### count_hands_composite_plus

- declared change: control에 count×양손 복합 범주 추가
- added features: `count_hands_state`
- removed features: none
- model changes: none

### count_matchup_composite

- declared change: count×동일손 여부 복합 범주만 추가
- added features: `count_matchup_state`
- removed features: none
- model changes: none

### count_out_plus

- declared change: control에 count×outs 복합 범주 추가
- added features: `count_out_state`
- removed features: none
- model changes: none

### count_hands_out_only

- declared change: count×양손×outs 복합 범주만 추가
- added features: `count_hands_out_state`
- removed features: none
- model changes: none

### count_hands_out_plus

- declared change: control에 count×양손×outs 복합 범주 추가
- added features: `count_hands_out_state`
- removed features: none
- model changes: none
