# 108_restore_excluded_raw: Latest-feature excluded raw column restoration

- 가설: Some raw columns excluded for redundancy on earlier models, especially prev5 form and pitcher strike/fastball rates, regain incremental value after season-state and interaction features changed the representation.
- control: `main72_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `27492b7bb43e`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main72_control | control: current main72 exclusion list | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| restore_prev5_success | restore raw asof_pitcher_prev5_game_success_rate only | 0.247514381 | 0.000002514 | 0/1 | 917.727 |
| restore_run_total | restore raw run_total_before only | 0.247524418 | 0.000012551 | 0/1 | 913.709 |
| restore_strike_rate | restore raw asof_pitcher_strike_rate only | 0.247527122 | 0.000015255 | 0/1 | 912.627 |
| restore_score_diff_home | restore raw score_diff_home only | 0.247529035 | 0.000017169 | 0/1 | 911.861 |
| restore_fastball_rate | restore raw asof_pitcher_fastball_rate only | 0.247535566 | 0.000023699 | 0/1 | 909.247 |
| restore_pitchmix_n | restore raw asof_pitcher_pitchmix_n only | 0.247542089 | 0.000030222 | 0/1 | 906.635 |

## 실제 변경 필드

- `main72_control`: control
- `restore_run_total`: features.description, features.exclude, features.expected_count, features.name
- `restore_score_diff_home`: features.description, features.exclude, features.expected_count, features.name
- `restore_pitchmix_n`: features.description, features.exclude, features.expected_count, features.name
- `restore_strike_rate`: features.description, features.exclude, features.expected_count, features.name
- `restore_fastball_rate`: features.description, features.exclude, features.expected_count, features.name
- `restore_prev5_success`: features.description, features.exclude, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/108_restore_excluded_raw/20260818T102859739498Z_27492b7bb43e`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_095`
- 기준 variant: `all_three`
- 검증할 변경: Keep latest CPU CatBoost and all main72 custom features fixed; restore exactly one excluded official raw column at a time.

### main72_control

- role: control

### restore_run_total

- declared change: restore raw run_total_before only
- added features: `run_total_before`
- removed features: none
- model changes: none

### restore_score_diff_home

- declared change: restore raw score_diff_home only
- added features: `score_diff_home`
- removed features: none
- model changes: none

### restore_pitchmix_n

- declared change: restore raw asof_pitcher_pitchmix_n only
- added features: `asof_pitcher_pitchmix_n`
- removed features: none
- model changes: none

### restore_strike_rate

- declared change: restore raw asof_pitcher_strike_rate only
- added features: `asof_pitcher_strike_rate`
- removed features: none
- model changes: none

### restore_fastball_rate

- declared change: restore raw asof_pitcher_fastball_rate only
- added features: `asof_pitcher_fastball_rate`
- removed features: none
- model changes: none

### restore_prev5_success

- declared change: restore raw asof_pitcher_prev5_game_success_rate only
- added features: `asof_pitcher_prev5_game_success_rate`
- removed features: none
- model changes: none
