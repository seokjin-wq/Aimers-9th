# 002_feature_ablation: CatBoost 설정을 고정한 main55 피처 출처의 2024 holdout ablation

- 가설: 달력·상태·context 피처 묶음이 2024 홀드아웃 Brier를 개선한다.
- control: `main55_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `068d97225aa6`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| drop_state | 상태 재조합 3개와 의존 파생 제거 | 0.248013596 | -0.000009858 | 1/1 | 717.887 |
| main55_control | control: 선택 제공 41개 + 파생 14개 | 0.248023454 | 0.000000000 | 0/1 | 713.940 |
| drop_context | 기대 승률·LI와 의존 파생 제거 | 0.248027660 | 0.000004206 | 0/1 | 712.257 |
| drop_calendar | 달력 파생 season, month, dayofweek 제거 | 0.248937714 | 0.000914259 | 0/1 | 347.954 |

## 실제 변경 필드

- `main55_control`: control
- `drop_calendar`: features.description, features.exclude, features.expected_count, features.name
- `drop_state`: features.categorical, features.custom, features.description, features.exclude, features.expected_count, features.name
- `drop_context`: features.custom, features.description, features.exclude, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/002_feature_ablation/20260817T144458529874Z_068d97225aa6`

## 실험 계보와 정확한 ablation

- 비교 기준: `BASELINE_001_main55`
- 기준 variant: `main55_control`
- 검증할 변경: main55 대비 달력·상태·context 피처 묶음을 각각 제거해 기여도를 검증

### main55_control

- role: control

### drop_calendar

- declared change: 달력 파생 season, month, dayofweek 제거
- added features: none
- removed features: `season`, `game_month`, `game_dayofweek`
- model changes: none

### drop_state

- declared change: 상태 재조합 3개와 의존 파생 제거
- added features: none
- removed features: `score_diff_pitcher_team`, `num_runners_on`, `base_state`, `runners_x_li`
- model changes: none

### drop_context

- declared change: 기대 승률·LI와 의존 파생 제거
- added features: none
- removed features: `home_win_expectancy`, `away_win_expectancy`, `li`, `win_expectancy_dist50`, `runners_x_li`, `reverse_rate_x_li`, `offspeed_x_li`
- model changes: none
