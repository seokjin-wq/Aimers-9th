# exp_053: context grouped rolling signals

- 가설: 경기·공격팀별 최근 success/middle 비율이 global200이 놓친 환경 편향을 보완한다
- control: `control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `44203078aafb`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| batter_team_middle200 | batter team recent200 middle 한 개 추가 | 0.246550964 | -0.000096722 | 1/1 | 1303.392 |
| pitcher_team_success200 | pitcher team recent200 success 한 개 추가 | 0.246585179 | -0.000062506 | 1/1 | 1289.695 |
| game_middle200 | game recent200 middle 한 개 추가 | 0.246588000 | -0.000059685 | 1/1 | 1288.566 |
| batter_team_success200 | batter team recent200 success 한 개 추가 | 0.246589742 | -0.000057944 | 1/1 | 1287.869 |
| pitcher_team_middle200 | pitcher team recent200 middle 한 개 추가 | 0.246599639 | -0.000048046 | 1/1 | 1283.906 |
| game_success200 | game recent200 success 한 개 추가 | 0.246610484 | -0.000037202 | 1/1 | 1279.565 |
| control | control: EXP050 best | 0.246647686 | 0.000000000 | 0/1 | 1264.673 |

## 실제 변경 필드

- `control`: control
- `game_success200`: features.custom, features.description, features.expected_count, features.name
- `pitcher_team_success200`: features.custom, features.description, features.expected_count, features.name
- `batter_team_success200`: features.custom, features.description, features.expected_count, features.name
- `game_middle200`: features.custom, features.description, features.expected_count, features.name
- `pitcher_team_middle200`: features.custom, features.description, features.expected_count, features.name
- `batter_team_middle200`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/exp_053/20260817T203738300166Z_44203078aafb`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_050`
- 기준 variant: `d6_i600`
- 검증할 변경: EXP050 최고 설정을 고정하고 game·pitcher_team·batter_team 기준 recent200 success 또는 middle 한 개만 추가

### control

- role: control

### game_success200

- declared change: game recent200 success 한 개 추가
- added features: `game_recent200_success`
- removed features: none
- model changes: none

### pitcher_team_success200

- declared change: pitcher team recent200 success 한 개 추가
- added features: `pitcher_team_recent200_success`
- removed features: none
- model changes: none

### batter_team_success200

- declared change: batter team recent200 success 한 개 추가
- added features: `batter_team_recent200_success`
- removed features: none
- model changes: none

### game_middle200

- declared change: game recent200 middle 한 개 추가
- added features: `game_recent200_middle`
- removed features: none
- model changes: none

### pitcher_team_middle200

- declared change: pitcher team recent200 middle 한 개 추가
- added features: `pitcher_team_recent200_middle`
- removed features: none
- model changes: none

### batter_team_middle200

- declared change: batter team recent200 middle 한 개 추가
- added features: `batter_team_recent200_middle`
- removed features: none
- model changes: none
