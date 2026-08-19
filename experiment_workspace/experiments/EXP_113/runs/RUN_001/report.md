# 113_reliability_decomposition: History reliability block decomposition

- 가설: The EXP_112 gain is concentrated in one of reliability level, success-rate weighting, or reverse/middle weighting; removing non-contributing blocks can reduce noise.
- control: `all_six_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `c3865b5e52b3`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| all_six_control | control: EXP_112 six-feature reliability winner | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| remove_levels | remove standalone pitcher/batter reliability levels only | 0.247491635 | 0.000003643 | 0/1 | 926.832 |
| remove_success_weighted | remove pitcher/batter success-rate weighted features only | 0.247519679 | 0.000031686 | 0/1 | 915.606 |
| remove_failure_weighted | remove pitcher reverse/middle weighted features only | 0.247550553 | 0.000062560 | 0/1 | 903.247 |

## 실제 변경 필드

- `all_six_control`: control
- `remove_levels`: features.custom, features.description, features.expected_count, features.name
- `remove_success_weighted`: features.custom, features.description, features.expected_count, features.name
- `remove_failure_weighted`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/113_reliability_decomposition/20260818T112352272963Z_c3865b5e52b3`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_112`
- 기준 variant: `history_reliability`
- 검증할 변경: Use the six-feature EXP_112 winner as control; remove exactly one two-feature block at a time: reliability levels, success-weighted rates, or reverse/middle-weighted rates.

### all_six_control

- role: control

### remove_levels

- declared change: remove standalone pitcher/batter reliability levels only
- added features: none
- removed features: `pitcher_history_reliability_k100`, `batter_history_reliability_k100`
- model changes: none

### remove_success_weighted

- declared change: remove pitcher/batter success-rate weighted features only
- added features: none
- removed features: `pitcher_success_x_reliability`, `batter_success_x_reliability`
- model changes: none

### remove_failure_weighted

- declared change: remove pitcher reverse/middle weighted features only
- added features: none
- removed features: `pitcher_reverse_x_reliability`, `pitcher_middle_x_reliability`
- model changes: none
