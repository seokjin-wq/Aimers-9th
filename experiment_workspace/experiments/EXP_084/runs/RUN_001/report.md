# 084_hand_pitchmix_interactions: EDA 기반 손 조합과 사전 구종 구성의 행 단위 상호작용

- 가설: 손 조합별로 과거 구종 구성과 제구 성공의 기울기가 달라 명시적 교호항이 추가 신호를 준다.
- control: `count_hands_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `237b4ed0a916`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| same_hand_pitchmix | 동일손 여부×과거 구종군 비율 3개 추가 | 0.247511867 | -0.000003992 | 1/1 | 918.734 |
| count_hands_control | control: EXP_080 CPU count+hands base | 0.247515859 | 0.000000000 | 0/1 | 917.136 |
| separate_hands_pitchmix | 투수손·타자손 각각과 과거 구종군 비율 6개 추가 | 0.247569593 | 0.000053735 | 0/1 | 895.625 |
| hand_matchup_category | 네 가지 투수손×타자손 조합 categorical 추가 | 0.247575725 | 0.000059867 | 0/1 | 893.170 |
| full_matchup_pitchmix | 네 손 조합 indicator×세 과거 구종군 비율 12개 추가 | 0.247614023 | 0.000098165 | 0/1 | 877.839 |

## 실제 변경 필드

- `count_hands_control`: control
- `hand_matchup_category`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `same_hand_pitchmix`: features.custom, features.description, features.expected_count, features.name
- `separate_hands_pitchmix`: features.custom, features.description, features.expected_count, features.name
- `full_matchup_pitchmix`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/084_hand_pitchmix_interactions/20260818T055848271636Z_237b4ed0a916`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_080`
- 기준 variant: `count_hands_promoted`
- 검증할 변경: Fix EXP_080 CPU base and add pure hand-matchup, same-hand×pitchmix, separate-hand×pitchmix, or full four-matchup×pitchmix interactions using only each row's asof values.

### count_hands_control

- role: control

### hand_matchup_category

- declared change: 네 가지 투수손×타자손 조합 categorical 추가
- added features: `hand_matchup_state`
- removed features: none
- model changes: none

### same_hand_pitchmix

- declared change: 동일손 여부×과거 구종군 비율 3개 추가
- added features: `same_hand_x_fastball`, `same_hand_x_breaking`, `same_hand_x_offspeed`
- removed features: none
- model changes: none

### separate_hands_pitchmix

- declared change: 투수손·타자손 각각과 과거 구종군 비율 6개 추가
- added features: `pitcher_hand_x_fastball`, `pitcher_hand_x_breaking`, `pitcher_hand_x_offspeed`, `batter_hand_x_fastball`, `batter_hand_x_breaking`, `batter_hand_x_offspeed`
- removed features: none
- model changes: none

### full_matchup_pitchmix

- declared change: 네 손 조합 indicator×세 과거 구종군 비율 12개 추가
- added features: `matchup0_x_fastball`, `matchup0_x_breaking`, `matchup0_x_offspeed`, `matchup1_x_fastball`, `matchup1_x_breaking`, `matchup1_x_offspeed`, `matchup2_x_fastball`, `matchup2_x_breaking`, `matchup2_x_offspeed`, `matchup3_x_fastball`, `matchup3_x_breaking`, `matchup3_x_offspeed`
- removed features: none
- model changes: none
