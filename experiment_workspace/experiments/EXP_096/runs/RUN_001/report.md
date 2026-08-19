# 096_late_history_decomposition: Late-inning pitcher-history contribution decomposition

- 가설: The late-inning pitcher-history block contains one or two useful slopes and noisy remainder; isolating success, reverse, and middle-location histories can improve over the full block.
- control: `same_hand_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `06067ca5ea11`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| late_all_three | EXP_090 reference: add all three late-inning pitcher-history interactions | 0.247501577 | -0.000010289 | 1/1 | 922.853 |
| late_success_reverse | add late success and reverse interactions | 0.247506419 | -0.000005448 | 1/1 | 920.914 |
| same_hand_control | control: EXP_090 same-hand pitch-mix base | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| late_reverse_middle | add late reverse and middle interactions | 0.247529183 | 0.000017316 | 0/1 | 911.802 |
| late_success_middle | add late success and middle interactions | 0.247536407 | 0.000024540 | 0/1 | 908.910 |
| late_middle_only | add late_inning_x_pitcher_middle only | 0.247539042 | 0.000027176 | 0/1 | 907.855 |
| late_success_only | add late_inning_x_pitcher_success only | 0.247544205 | 0.000032338 | 0/1 | 905.788 |
| late_reverse_only | add late_inning_x_pitcher_reverse only | 0.247545335 | 0.000033469 | 0/1 | 905.336 |

## 실제 변경 필드

- `same_hand_control`: control
- `late_success_only`: features.custom, features.description, features.expected_count, features.name
- `late_reverse_only`: features.custom, features.description, features.expected_count, features.name
- `late_middle_only`: features.custom, features.description, features.expected_count, features.name
- `late_success_reverse`: features.custom, features.description, features.expected_count, features.name
- `late_success_middle`: features.custom, features.description, features.expected_count, features.name
- `late_reverse_middle`: features.custom, features.description, features.expected_count, features.name
- `late_all_three`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/096_late_history_decomposition/20260818T075720910169Z_06067ca5ea11`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_090`
- 기준 variant: `late_pitcher_history`
- 검증할 변경: Hold the EXP_090 same-hand pitch-mix control and model fixed; compare three late-inning pitcher-history interactions individually, in pairs, and together.

### same_hand_control

- role: control

### late_success_only

- declared change: add late_inning_x_pitcher_success only
- added features: `late_inning_x_pitcher_success`
- removed features: none
- model changes: none

### late_reverse_only

- declared change: add late_inning_x_pitcher_reverse only
- added features: `late_inning_x_pitcher_reverse`
- removed features: none
- model changes: none

### late_middle_only

- declared change: add late_inning_x_pitcher_middle only
- added features: `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none

### late_success_reverse

- declared change: add late success and reverse interactions
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`
- removed features: none
- model changes: none

### late_success_middle

- declared change: add late success and middle interactions
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none

### late_reverse_middle

- declared change: add late reverse and middle interactions
- added features: `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none

### late_all_three

- declared change: EXP_090 reference: add all three late-inning pitcher-history interactions
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none
