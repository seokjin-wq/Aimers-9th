# 010_previous_season_target_features: 직전 시즌 타깃 이력 피처

- 가설: 이전 시즌만으로 만든 투수·타자·팀 제구율이 커리어 누적률보다 최근 실력을 잘 반영해 2024 Brier를 개선한다
- control: `main55_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `4ac15b964309`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main55_control | control: main55 | 0.248009268 | 0.000000000 | 0/1 | 719.619 |
| add_full_prev_season | 시즌 prior와 직전 시즌 선수·팀 스무딩 이력 추가 | 0.248212027 | 0.000202759 | 0/1 | 638.453 |
| add_season_priors | 직전 시즌 전체 제구율과 선형 추세 prior 추가 | 0.248370564 | 0.000361296 | 0/1 | 574.989 |
| add_player_prev_season | 시즌 prior와 직전 시즌 투수·타자 스무딩 이력 추가 | 0.248390713 | 0.000381445 | 0/1 | 566.923 |
| add_pitcher_prev_season | 시즌 prior와 직전 시즌 투수 스무딩 이력 추가 | 0.248507264 | 0.000497997 | 0/1 | 520.267 |

## 실제 변경 필드

- `main55_control`: control
- `add_season_priors`: features.custom, features.description, features.expected_count, features.name
- `add_pitcher_prev_season`: features.custom, features.description, features.expected_count, features.name
- `add_player_prev_season`: features.custom, features.description, features.expected_count, features.name
- `add_full_prev_season`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/010_previous_season_target_features/20260817T160815242704Z_4ac15b964309`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_009`
- 기준 variant: `main55_control`
- 검증할 변경: main55를 기준으로 누수 없는 시즌 전체 prior, 직전 시즌 투수, 투수·타자, 선수·팀 타깃 이력을 단계적으로 추가

### main55_control

- role: control

### add_season_priors

- declared change: 직전 시즌 전체 제구율과 선형 추세 prior 추가
- added features: `previous_season_target_rate`, `season_trend_prior`
- removed features: none
- model changes: none

### add_pitcher_prev_season

- declared change: 시즌 prior와 직전 시즌 투수 스무딩 이력 추가
- added features: `previous_season_target_rate`, `season_trend_prior`, `pitcher_prev_season_rate`, `pitcher_prev_season_log_n`, `pitcher_prev_season_delta`
- removed features: none
- model changes: none

### add_player_prev_season

- declared change: 시즌 prior와 직전 시즌 투수·타자 스무딩 이력 추가
- added features: `previous_season_target_rate`, `season_trend_prior`, `pitcher_prev_season_rate`, `pitcher_prev_season_log_n`, `pitcher_prev_season_delta`, `batter_prev_season_rate`, `batter_prev_season_log_n`, `batter_prev_season_delta`
- removed features: none
- model changes: none

### add_full_prev_season

- declared change: 시즌 prior와 직전 시즌 선수·팀 스무딩 이력 추가
- added features: `previous_season_target_rate`, `season_trend_prior`, `pitcher_prev_season_rate`, `pitcher_prev_season_log_n`, `pitcher_prev_season_delta`, `batter_prev_season_rate`, `batter_prev_season_log_n`, `batter_prev_season_delta`, `pitcher_team_prev_season_rate`, `batter_team_prev_season_rate`
- removed features: none
- model changes: none
