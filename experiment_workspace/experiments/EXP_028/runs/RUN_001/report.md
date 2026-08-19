# 028_eda_individual_features: EDA 파생 피처 개별 스크리닝

- 가설: 묶음 추가에서 상쇄된 EDA 피처 중 일부는 최신 main60+team+GPU 기준에서 단독으로 Brier를 개선한다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `cabb64a8efb0`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| add_scoring_position_x_li | scoring_position_x_li 단독 추가 | 0.247802388 | -0.000016593 | 1/1 | 802.435 |
| add_pitcher_reverse_rate_shrunk | pitcher_reverse_rate_shrunk 단독 추가 | 0.247803964 | -0.000015018 | 1/1 | 801.804 |
| add_log1p_li | log1p_li 단독 추가 | 0.247811881 | -0.000007100 | 1/1 | 798.635 |
| add_batter_history_missing | batter_history_missing 단독 추가 | 0.247813965 | -0.000005016 | 1/1 | 797.801 |
| add_scoring_position | scoring_position 단독 추가 | 0.247817647 | -0.000001335 | 1/1 | 796.327 |
| add_recent_history_missing | recent_history_missing 단독 추가 | 0.247818146 | -0.000000835 | 1/1 | 796.127 |
| main60_control | control: GPU main60 | 0.247818981 | 0.000000000 | 0/1 | 795.793 |
| add_pitcher_team_win_expectancy | pitcher_team_win_expectancy 단독 추가 | 0.247819873 | 0.000000892 | 0/1 | 795.436 |
| add_pitcher_history_missing | pitcher_history_missing 단독 추가 | 0.247819901 | 0.000000920 | 0/1 | 795.425 |
| add_success_minus_reverse | success_minus_reverse 단독 추가 | 0.247825757 | 0.000006776 | 0/1 | 793.080 |
| add_log1p_batter_n | log1p_batter_n 단독 추가 | 0.247826638 | 0.000007657 | 0/1 | 792.728 |
| add_pitcher_success_rate_shrunk | pitcher_success_rate_shrunk 단독 추가 | 0.247828494 | 0.000009512 | 0/1 | 791.985 |
| add_log1p_pitcher_n | log1p_pitcher_n 단독 추가 | 0.247829290 | 0.000010309 | 0/1 | 791.666 |

## 실제 변경 필드

- `main60_control`: control
- `add_recent_history_missing`: features.custom, features.description, features.expected_count, features.name
- `add_pitcher_history_missing`: features.custom, features.description, features.expected_count, features.name
- `add_batter_history_missing`: features.custom, features.description, features.expected_count, features.name
- `add_pitcher_success_rate_shrunk`: features.custom, features.description, features.expected_count, features.name
- `add_pitcher_reverse_rate_shrunk`: features.custom, features.description, features.expected_count, features.name
- `add_success_minus_reverse`: features.custom, features.description, features.expected_count, features.name
- `add_log1p_pitcher_n`: features.custom, features.description, features.expected_count, features.name
- `add_log1p_batter_n`: features.custom, features.description, features.expected_count, features.name
- `add_pitcher_team_win_expectancy`: features.custom, features.description, features.expected_count, features.name
- `add_log1p_li`: features.custom, features.description, features.expected_count, features.name
- `add_scoring_position`: features.custom, features.description, features.expected_count, features.name
- `add_scoring_position_x_li`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/028_eda_individual_features/20260817T175553136113Z_cabb64a8efb0`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_027`
- 기준 variant: `gpu_d6_i600`
- 검증할 변경: GPU 모델을 고정하고 missing, shrinkage, log-count, context 파생 12개를 각각 하나씩만 추가

### main60_control

- role: control

### add_recent_history_missing

- declared change: recent_history_missing 단독 추가
- added features: `recent_history_missing`
- removed features: none
- model changes: none

### add_pitcher_history_missing

- declared change: pitcher_history_missing 단독 추가
- added features: `pitcher_history_missing`
- removed features: none
- model changes: none

### add_batter_history_missing

- declared change: batter_history_missing 단독 추가
- added features: `batter_history_missing`
- removed features: none
- model changes: none

### add_pitcher_success_rate_shrunk

- declared change: pitcher_success_rate_shrunk 단독 추가
- added features: `pitcher_success_rate_shrunk`
- removed features: none
- model changes: none

### add_pitcher_reverse_rate_shrunk

- declared change: pitcher_reverse_rate_shrunk 단독 추가
- added features: `pitcher_reverse_rate_shrunk`
- removed features: none
- model changes: none

### add_success_minus_reverse

- declared change: success_minus_reverse 단독 추가
- added features: `success_minus_reverse`
- removed features: none
- model changes: none

### add_log1p_pitcher_n

- declared change: log1p_pitcher_n 단독 추가
- added features: `log1p_pitcher_n`
- removed features: none
- model changes: none

### add_log1p_batter_n

- declared change: log1p_batter_n 단독 추가
- added features: `log1p_batter_n`
- removed features: none
- model changes: none

### add_pitcher_team_win_expectancy

- declared change: pitcher_team_win_expectancy 단독 추가
- added features: `pitcher_team_win_expectancy`
- removed features: none
- model changes: none

### add_log1p_li

- declared change: log1p_li 단독 추가
- added features: `log1p_li`
- removed features: none
- model changes: none

### add_scoring_position

- declared change: scoring_position 단독 추가
- added features: `scoring_position`
- removed features: none
- model changes: none

### add_scoring_position_x_li

- declared change: scoring_position_x_li 단독 추가
- added features: `scoring_position_x_li`
- removed features: none
- model changes: none
