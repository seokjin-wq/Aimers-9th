# 106_trackman_physics_decomposition: Latest-feature Trackman physics decomposition

- 가설: The small Trackman gain seen on the earlier feature set comes from a subset of velocity, movement, or extension context and can complement the latest same-hand pitch-mix features.
- control: `same_pitchmix_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `58b7515c1850`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| track_velocity | add official Trackman relative-speed and zone-speed context | 0.247508699 | -0.000003168 | 1/1 | 920.002 |
| same_pitchmix_control | control: latest CPU main72 without Trackman context | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| track_extension | add official Trackman extension context only | 0.247542196 | 0.000030330 | 0/1 | 906.592 |
| track_movement | add official Trackman spin, vertical-break, and horizontal-break context | 0.247550183 | 0.000038316 | 0/1 | 903.395 |
| track_all_physics | add all six official Trackman physics context aggregates | 0.247583443 | 0.000071576 | 0/1 | 890.081 |

## 실제 변경 필드

- `same_pitchmix_control`: control
- `track_velocity`: features.custom, features.description, features.expected_count, features.name
- `track_movement`: features.custom, features.description, features.expected_count, features.name
- `track_extension`: features.custom, features.description, features.expected_count, features.name
- `track_all_physics`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/106_trackman_physics_decomposition/20260818T095736207460Z_58b7515c1850`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_068`
- 기준 variant: `track_physics`
- 검증할 변경: Keep latest CPU main72 fixed; compare official pre-validation Trackman velocity pair, movement triple, extension alone, and all six physics context aggregates.

### same_pitchmix_control

- role: control

### track_velocity

- declared change: add official Trackman relative-speed and zone-speed context
- added features: `track_context_rel_speed`, `track_context_zone_speed`
- removed features: none
- model changes: none

### track_movement

- declared change: add official Trackman spin, vertical-break, and horizontal-break context
- added features: `track_context_spin_rate`, `track_context_induced_vert_break`, `track_context_abs_horz_break`
- removed features: none
- model changes: none

### track_extension

- declared change: add official Trackman extension context only
- added features: `track_context_extension`
- removed features: none
- model changes: none

### track_all_physics

- declared change: add all six official Trackman physics context aggregates
- added features: `track_context_rel_speed`, `track_context_spin_rate`, `track_context_induced_vert_break`, `track_context_abs_horz_break`, `track_context_extension`, `track_context_zone_speed`
- removed features: none
- model changes: none
