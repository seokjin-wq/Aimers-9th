# 095_same_hand_pitchmix_decomposition: Same-hand pitch-mix contribution decomposition

- 가설: The three same-hand pitch-mix interactions contain unequal signal, so a smaller subset can improve Brier score by removing noisy interactions.
- control: `count_hands_base`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `0f0433cd7fd9`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| all_three | EXP_084 reference: add all three same-hand pitch-mix interactions | 0.247511867 | -0.000003992 | 1/1 | 918.734 |
| count_hands_base | control: EXP_084 count+hands base without same-hand pitch-mix interactions | 0.247515859 | 0.000000000 | 0/1 | 917.136 |
| fastball_offspeed | add same_hand_x_fastball and same_hand_x_offspeed | 0.247531460 | 0.000015602 | 0/1 | 910.890 |
| offspeed_only | add same_hand_x_offspeed only | 0.247547486 | 0.000031627 | 0/1 | 904.475 |
| fastball_only | add same_hand_x_fastball only | 0.247548295 | 0.000032436 | 0/1 | 904.151 |
| breaking_offspeed | add same_hand_x_breaking and same_hand_x_offspeed | 0.247555078 | 0.000039219 | 0/1 | 901.436 |
| fastball_breaking | add same_hand_x_fastball and same_hand_x_breaking | 0.247561634 | 0.000045776 | 0/1 | 898.811 |
| breaking_only | add same_hand_x_breaking only | 0.247562057 | 0.000046199 | 0/1 | 898.642 |

## 실제 변경 필드

- `count_hands_base`: control
- `fastball_only`: features.custom, features.description, features.expected_count, features.name
- `breaking_only`: features.custom, features.description, features.expected_count, features.name
- `offspeed_only`: features.custom, features.description, features.expected_count, features.name
- `fastball_breaking`: features.custom, features.description, features.expected_count, features.name
- `fastball_offspeed`: features.custom, features.description, features.expected_count, features.name
- `breaking_offspeed`: features.custom, features.description, features.expected_count, features.name
- `all_three`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/095_same_hand_pitchmix_decomposition/20260818T074823769450Z_0f0433cd7fd9`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_084`
- 기준 variant: `same_hand_pitchmix`
- 검증할 변경: Keep the EXP_084 count+hands control fixed and compare each same-hand pitch-mix interaction alone, all three pairs, and the existing all-three variant.

### count_hands_base

- role: control

### fastball_only

- declared change: add same_hand_x_fastball only
- added features: `same_hand_x_fastball`
- removed features: none
- model changes: none

### breaking_only

- declared change: add same_hand_x_breaking only
- added features: `same_hand_x_breaking`
- removed features: none
- model changes: none

### offspeed_only

- declared change: add same_hand_x_offspeed only
- added features: `same_hand_x_offspeed`
- removed features: none
- model changes: none

### fastball_breaking

- declared change: add same_hand_x_fastball and same_hand_x_breaking
- added features: `same_hand_x_fastball`, `same_hand_x_breaking`
- removed features: none
- model changes: none

### fastball_offspeed

- declared change: add same_hand_x_fastball and same_hand_x_offspeed
- added features: `same_hand_x_fastball`, `same_hand_x_offspeed`
- removed features: none
- model changes: none

### breaking_offspeed

- declared change: add same_hand_x_breaking and same_hand_x_offspeed
- added features: `same_hand_x_breaking`, `same_hand_x_offspeed`
- removed features: none
- model changes: none

### all_three

- declared change: EXP_084 reference: add all three same-hand pitch-mix interactions
- added features: `same_hand_x_fastball`, `same_hand_x_breaking`, `same_hand_x_offspeed`
- removed features: none
- model changes: none
