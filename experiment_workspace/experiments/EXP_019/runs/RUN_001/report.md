# 019_identifier_categorical: 식별자 범주형 개별 기여

- 가설: 팀 또는 선수 ID를 한꺼번에 범주화한 이전 실험의 악화는 일부 ID 때문이며, 개별 범주화는 잔차 편향을 줄인다
- control: `numeric_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `cfbe63f5735b`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| batter_team_cat | batter_team_id만 범주형 추가 | 0.247830842 | -0.000044650 | 1/1 | 791.045 |
| both_teams_cat | 양 팀 ID를 범주형 추가 | 0.247831041 | -0.000044451 | 1/1 | 790.965 |
| numeric_control | control: 기본 3개만 범주형 | 0.247875492 | 0.000000000 | 0/1 | 773.171 |
| hands_cat | 투타 손 유형을 범주형 추가 | 0.247886327 | 0.000010835 | 0/1 | 768.834 |
| pitcher_team_cat | pitcher_team_id만 범주형 추가 | 0.247902118 | 0.000026625 | 0/1 | 762.512 |
| batter_id_cat | batter_id만 범주형 추가 | 0.247927383 | 0.000051891 | 0/1 | 752.399 |
| pitcher_id_cat | pitcher_id만 범주형 추가 | 0.248068198 | 0.000192705 | 0/1 | 696.029 |

## 실제 변경 필드

- `numeric_control`: control
- `pitcher_id_cat`: features.categorical, features.description, features.name
- `batter_id_cat`: features.categorical, features.description, features.name
- `pitcher_team_cat`: features.categorical, features.description, features.name
- `batter_team_cat`: features.categorical, features.description, features.name
- `both_teams_cat`: features.categorical, features.description, features.name
- `hands_cat`: features.categorical, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/019_identifier_categorical/20260817T165331774474Z_cfbe63f5735b`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_018`
- 기준 variant: `d6_i300_control`
- 검증할 변경: main55+count와 CatBoost 설정을 고정하고 pitcher/batter/team/hand ID를 한 종류씩만 native categorical로 추가

### numeric_control

- role: control

### pitcher_id_cat

- declared change: pitcher_id만 범주형 추가
- added features: none
- removed features: none
- model changes: none

### batter_id_cat

- declared change: batter_id만 범주형 추가
- added features: none
- removed features: none
- model changes: none

### pitcher_team_cat

- declared change: pitcher_team_id만 범주형 추가
- added features: none
- removed features: none
- model changes: none

### batter_team_cat

- declared change: batter_team_id만 범주형 추가
- added features: none
- removed features: none
- model changes: none

### both_teams_cat

- declared change: 양 팀 ID를 범주형 추가
- added features: none
- removed features: none
- model changes: none

### hands_cat

- declared change: 투타 손 유형을 범주형 추가
- added features: none
- removed features: none
- model changes: none
