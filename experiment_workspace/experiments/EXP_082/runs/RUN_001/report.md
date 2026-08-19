# 082_context_categories: 카운트×양손 기준의 인접 상황 범주 추가

- 가설: 카운트와 양손 범주가 활성화된 상태에서 아웃·이닝·팀·월·원시 카운트·주자수 중 하나가 고차 상호작용을 추가한다.
- control: `count_hands_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `84586b045b75`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_hands_control | control: count_state와 양손 categorical | 0.247515859 | 0.000000000 | 0/1 | 917.136 |
| add_runners | control에 num_runners_on categorical 추가 | 0.247529655 | 0.000013796 | 0/1 | 911.613 |
| add_pitcher_team | control에 pitcher_team_id categorical 추가 | 0.247537145 | 0.000021287 | 0/1 | 908.614 |
| add_inning | control에 inning categorical 추가 | 0.247560477 | 0.000044618 | 0/1 | 899.274 |
| add_raw_count | control에 balls_before·strikes_before categorical 추가 | 0.247560499 | 0.000044640 | 0/1 | 899.266 |
| add_outs | control에 outs_before categorical 추가 | 0.247567802 | 0.000051943 | 0/1 | 896.342 |
| add_month | control에 game_month categorical 추가 | 0.247568850 | 0.000052992 | 0/1 | 895.923 |

## 실제 변경 필드

- `count_hands_control`: control
- `add_outs`: features.categorical, features.description, features.name
- `add_inning`: features.categorical, features.description, features.name
- `add_pitcher_team`: features.categorical, features.description, features.name
- `add_month`: features.categorical, features.description, features.name
- `add_raw_count`: features.categorical, features.description, features.name
- `add_runners`: features.categorical, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/082_context_categories/20260818T053930927464Z_84586b045b75`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_080`
- 기준 variant: `count_hands_promoted`
- 검증할 변경: Fix EXP_078 count+hands categories; add exactly one adjacent low-cardinality categorical block at a time.

### count_hands_control

- role: control

### add_outs

- declared change: control에 outs_before categorical 추가
- added features: none
- removed features: none
- model changes: none

### add_inning

- declared change: control에 inning categorical 추가
- added features: none
- removed features: none
- model changes: none

### add_pitcher_team

- declared change: control에 pitcher_team_id categorical 추가
- added features: none
- removed features: none
- model changes: none

### add_month

- declared change: control에 game_month categorical 추가
- added features: none
- removed features: none
- model changes: none

### add_raw_count

- declared change: control에 balls_before·strikes_before categorical 추가
- added features: none
- removed features: none
- model changes: none

### add_runners

- declared change: control에 num_runners_on categorical 추가
- added features: none
- removed features: none
- model changes: none
