# 071_season_state_id_categorical: 시즌 상태 선수 ID 범주 재검증

- 가설: 현재 시즌 상태로 시간 변화가 분리된 뒤에는 선수 ID의 native categorical 효과가 안정적으로 남은 개인차를 포착한다
- control: `batter_team_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `ac237d64382f`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| batter_team_control | control: batter_team만 범주형 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| batter_cat | batter_id 범주형 추가 | 0.247557126 | 0.000019405 | 0/1 | 900.616 |
| pitcher_teams_cat | pitcher_id와 양 팀 ID 범주형 | 0.247663251 | 0.000125530 | 0/1 | 858.133 |
| pitcher_cat | pitcher_id 범주형 추가 | 0.247663919 | 0.000126198 | 0/1 | 857.866 |
| pitcher_batter_cat | pitcher_id와 batter_id 범주형 추가 | 0.247721761 | 0.000184040 | 0/1 | 834.711 |

## 실제 변경 필드

- `batter_team_control`: control
- `pitcher_cat`: features.categorical, features.description, features.name
- `batter_cat`: features.categorical, features.description, features.name
- `pitcher_batter_cat`: features.categorical, features.description, features.name
- `pitcher_teams_cat`: features.categorical, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/071_season_state_id_categorical/20260818T040018646621Z_ac237d64382f`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_070`
- 기준 variant: `cpu45_gpu40_extra15`
- 검증할 변경: main69 decay85에서 pitcher, batter, 둘 다, pitcher+양팀 categorical만 변경

### batter_team_control

- role: control

### pitcher_cat

- declared change: pitcher_id 범주형 추가
- added features: none
- removed features: none
- model changes: none

### batter_cat

- declared change: batter_id 범주형 추가
- added features: none
- removed features: none
- model changes: none

### pitcher_batter_cat

- declared change: pitcher_id와 batter_id 범주형 추가
- added features: none
- removed features: none
- model changes: none

### pitcher_teams_cat

- declared change: pitcher_id와 양 팀 ID 범주형
- added features: none
- removed features: none
- model changes: none
