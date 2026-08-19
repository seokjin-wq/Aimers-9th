# 008_eda_feature_groups: EDA 제안 피처 묶음 비교

- 가설: EDA에서 확인한 결측·스무딩·경기 맥락·카운트 피처 중 일부가 main55의 2024 Brier를 개선한다
- control: `main55_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `3139b29cd826`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| add_count_state | 카운트·아웃 상태 파생 5개 추가 | 0.247968140 | -0.000041128 | 1/1 | 736.083 |
| add_smoothing | 누적 성공·reverse 스무딩과 log 표본 수 5개 추가 | 0.247985253 | -0.000024014 | 1/1 | 729.233 |
| add_missing_flags | 최근·누적 이력 결측 플래그 3개 추가 | 0.247989430 | -0.000019838 | 1/1 | 727.561 |
| main55_control | control: main55 | 0.248009268 | 0.000000000 | 0/1 | 719.619 |
| add_context | 투수팀 기대승률·log LI·득점권 상호작용 4개 추가 | 0.248048336 | 0.000039068 | 0/1 | 703.980 |

## 실제 변경 필드

- `main55_control`: control
- `add_missing_flags`: features.custom, features.description, features.expected_count, features.name
- `add_smoothing`: features.custom, features.description, features.expected_count, features.name
- `add_context`: features.custom, features.description, features.expected_count, features.name
- `add_count_state`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/008_eda_feature_groups/20260817T155808474432Z_3139b29cd826`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_007`
- 기준 variant: `catboost_control`
- 검증할 변경: native CatBoost를 고정하고 EDA 제안 피처를 결측, 스무딩, 경기 맥락, 카운트 묶음별로 각각 추가

### main55_control

- role: control

### add_missing_flags

- declared change: 최근·누적 이력 결측 플래그 3개 추가
- added features: `recent_history_missing`, `pitcher_history_missing`, `batter_history_missing`
- removed features: none
- model changes: none

### add_smoothing

- declared change: 누적 성공·reverse 스무딩과 log 표본 수 5개 추가
- added features: `pitcher_success_rate_shrunk`, `pitcher_reverse_rate_shrunk`, `success_minus_reverse`, `log1p_pitcher_n`, `log1p_batter_n`
- removed features: none
- model changes: none

### add_context

- declared change: 투수팀 기대승률·log LI·득점권 상호작용 4개 추가
- added features: `pitcher_team_win_expectancy`, `log1p_li`, `scoring_position`, `scoring_position_x_li`
- removed features: none
- model changes: none

### add_count_state

- declared change: 카운트·아웃 상태 파생 5개 추가
- added features: `count_state`, `is_full_count`, `has_two_strikes`, `has_three_balls`, `has_two_outs`
- removed features: none
- model changes: none
