# 079_count_hand_interaction: 카운트×손 범주 상호작용 분해

- 가설: EXP_078 개선은 카운트와 특정 손 유형의 결합에서 나오며 불필요한 범주를 제거하면 더 개선된다.
- control: `count_both_hands_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `60969c5f075c`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_both_hands_control | control: count_state와 pitcher/batter hand categorical | 0.247515859 | 0.000000000 | 0/1 | 917.136 |
| count_batter_hand | control에서 pitcher_hand categorical 제거 | 0.247549634 | 0.000033776 | 0/1 | 903.615 |
| count_same_hand | 양손 원본 categorical 대신 same_hand_matchup categorical | 0.247558423 | 0.000042564 | 0/1 | 900.097 |
| count_hands_same | control에 same_hand_matchup categorical 추가 | 0.247562394 | 0.000046535 | 0/1 | 898.507 |
| count_pitcher_hand | control에서 batter_hand categorical 제거 | 0.247600785 | 0.000084927 | 0/1 | 883.139 |

## 실제 변경 필드

- `count_both_hands_control`: control
- `count_pitcher_hand`: features.categorical, features.description, features.name
- `count_batter_hand`: features.categorical, features.description, features.name
- `count_same_hand`: features.categorical, features.description, features.name
- `count_hands_same`: features.categorical, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/079_count_hand_interaction/20260818T051233513928Z_60969c5f075c`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_078`
- 기준 variant: `count_hands_cat`
- 검증할 변경: Use count+both-hands as control; remove one hand at a time, replace hands by same_hand, or add same_hand to all three.

### count_both_hands_control

- role: control

### count_pitcher_hand

- declared change: control에서 batter_hand categorical 제거
- added features: none
- removed features: none
- model changes: none

### count_batter_hand

- declared change: control에서 pitcher_hand categorical 제거
- added features: none
- removed features: none
- model changes: none

### count_same_hand

- declared change: 양손 원본 categorical 대신 same_hand_matchup categorical
- added features: none
- removed features: none
- model changes: none

### count_hands_same

- declared change: control에 same_hand_matchup categorical 추가
- added features: none
- removed features: none
- model changes: none
