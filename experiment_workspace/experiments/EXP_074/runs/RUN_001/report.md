# 074_safe_trackman_context: 익명 투수 연결 폐기 후 안전한 Trackman 상황 집계 재검증

- 가설: 선수 연결은 불안정하지만, 2019~2023 공식 Trackman만으로 만든 손 유형×카운트 물리·구종 평균은 검증 행 집계 없이 추가 신호를 줄 수 있다.
- control: `success_k50_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `3b393d02fb7c`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| success_k50_control | control: EXP_073의 k=50 당해 시즌 성공률 | 0.247529588 | 0.000000000 | 0/1 | 911.640 |
| track_all | control 대비 과거 Trackman 물리 6개와 구종군 비율 3개 모두 추가 | 0.247552871 | 0.000023284 | 0/1 | 902.319 |
| track_pitchmix | control 대비 과거 Trackman 손×카운트 구종군 비율 3개 추가 | 0.247560371 | 0.000030784 | 0/1 | 899.317 |
| track_physics | control 대비 과거 Trackman 손×카운트 물리 평균 6개 추가 | 0.247577442 | 0.000047854 | 0/1 | 892.483 |

## 실제 변경 필드

- `success_k50_control`: control
- `track_physics`: features.custom, features.description, features.expected_count, features.name
- `track_pitchmix`: features.custom, features.description, features.expected_count, features.name
- `track_all`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/074_safe_trackman_context/20260818T044554101007Z_3b393d02fb7c`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_073`
- 기준 variant: `success_k50`
- 검증할 변경: Diagnose reference-only entity linkage, then compare main69 against linked historical Trackman pitcher aggregates without using any validation-row aggregate.

### success_k50_control

- role: control

### track_physics

- declared change: control 대비 과거 Trackman 손×카운트 물리 평균 6개 추가
- added features: `track_context_rel_speed`, `track_context_spin_rate`, `track_context_induced_vert_break`, `track_context_abs_horz_break`, `track_context_extension`, `track_context_zone_speed`
- removed features: none
- model changes: none

### track_pitchmix

- declared change: control 대비 과거 Trackman 손×카운트 구종군 비율 3개 추가
- added features: `track_context_fastball_share`, `track_context_breaking_share`, `track_context_offspeed_share`
- removed features: none
- model changes: none

### track_all

- declared change: control 대비 과거 Trackman 물리 6개와 구종군 비율 3개 모두 추가
- added features: `track_context_rel_speed`, `track_context_spin_rate`, `track_context_induced_vert_break`, `track_context_abs_horz_break`, `track_context_extension`, `track_context_zone_speed`, `track_context_fastball_share`, `track_context_breaking_share`, `track_context_offspeed_share`
- removed features: none
- model changes: none
