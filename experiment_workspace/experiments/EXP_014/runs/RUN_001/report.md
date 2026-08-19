# 014_custom_feature_pruning: 파생 피처 묶음 pruning

- 가설: main55+count에서 중복·저중요도 파생 피처를 제거하면 일반화 Brier가 개선된다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `af9a1d57c71f`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main60_control | control: main55 + count 5개 | 0.247968140 | 0.000000000 | 0/1 | 736.083 |
| drop_count_redundancy | count_state와 중복되는 count_diff·count_total 제거 | 0.248013550 | 0.000045410 | 0/1 | 717.905 |
| drop_recent_gaps | 최근 성공률과 커리어 차이 3개 제거 | 0.248024188 | 0.000056048 | 0/1 | 713.646 |
| drop_low_context_custom | 저중요도 context 상호작용 5개 제거 | 0.248030637 | 0.000062497 | 0/1 | 711.065 |
| keep_core_custom | 상대적으로 중요한 custom 7개와 count 5개만 유지 | 0.248042378 | 0.000074238 | 0/1 | 706.365 |
| keep_count_only | 기존 custom14를 모두 제거하고 count 5개만 유지 | 0.248156625 | 0.000188485 | 0/1 | 660.631 |

## 실제 변경 필드

- `main60_control`: control
- `drop_low_context_custom`: features.custom, features.description, features.expected_count, features.name
- `drop_recent_gaps`: features.custom, features.description, features.expected_count, features.name
- `keep_count_only`: features.custom, features.description, features.expected_count, features.name
- `keep_core_custom`: features.custom, features.description, features.expected_count, features.name
- `drop_count_redundancy`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/014_custom_feature_pruning/20260817T162618616705Z_af9a1d57c71f`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_013`
- 기준 variant: `catboost_logloss_control`
- 검증할 변경: native CatBoost를 고정하고 저중요도 context, 최근-gap, 기존 custom 전체, count 중복을 각각 제거

### main60_control

- role: control

### drop_low_context_custom

- declared change: 저중요도 context 상호작용 5개 제거
- added features: none
- removed features: `win_expectancy_dist50`, `runners_x_li`, `reverse_rate_x_li`, `late_inning_x_recent_form`, `offspeed_x_li`
- model changes: none

### drop_recent_gaps

- declared change: 최근 성공률과 커리어 차이 3개 제거
- added features: none
- removed features: `pitcher_gap_prev1_career`, `pitcher_gap_prev3_career`, `pitcher_gap_prev5_career`
- model changes: none

### keep_count_only

- declared change: 기존 custom14를 모두 제거하고 count 5개만 유지
- added features: none
- removed features: `pitcher_gap_prev1_career`, `pitcher_gap_prev3_career`, `pitcher_gap_prev5_career`, `win_expectancy_dist50`, `count_diff`, `count_total`, `same_hand_matchup`, `pressure_x_recent_form`, `runners_x_li`, `batter_success_rate_shrunk`, `reverse_rate_x_li`, `middle_rate_x_count_diff`, `late_inning_x_recent_form`, `offspeed_x_li`
- model changes: none

### keep_core_custom

- declared change: 상대적으로 중요한 custom 7개와 count 5개만 유지
- added features: none
- removed features: `win_expectancy_dist50`, `count_diff`, `count_total`, `runners_x_li`, `reverse_rate_x_li`, `late_inning_x_recent_form`, `offspeed_x_li`
- model changes: none

### drop_count_redundancy

- declared change: count_state와 중복되는 count_diff·count_total 제거
- added features: none
- removed features: `count_diff`, `count_total`
- model changes: none
