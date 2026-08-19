# 068_official_trackman_context: 공식 Trackman 상황 통계

- 가설: 공식 Trackman의 볼카운트×투타 손잡이별 물리 특성과 구종 선택 비율이 main69의 상황 신호를 보완한다
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `23e151c38b60`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| track_physics | 공식 Trackman 물리 상황 평균 6개 추가 | 0.247535912 | -0.000001809 | 1/1 | 909.108 |
| main69_control | control: Trackman 미사용 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| track_all | Trackman 물리 6개와 구종 비율 3개 전체 추가 | 0.247554511 | 0.000016791 | 0/1 | 901.662 |
| track_pitchmix | 공식 Trackman 구종 선택 비율 3개 추가 | 0.247574075 | 0.000036354 | 0/1 | 893.831 |

## 실제 변경 필드

- `main69_control`: control
- `track_physics`: features.custom, features.description, features.expected_count, features.name
- `track_pitchmix`: features.custom, features.description, features.expected_count, features.name
- `track_all`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/068_official_trackman_context/20260818T034216716884Z_23e151c38b60`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_062`
- 기준 variant: `extra_w18`
- 검증할 변경: main69 decay85 대비 Trackman 물리 6개, 구종비율 3개, 전체 9개를 season-OOF 방식으로 추가

### main69_control

- role: control

### track_physics

- declared change: 공식 Trackman 물리 상황 평균 6개 추가
- added features: `track_context_rel_speed`, `track_context_spin_rate`, `track_context_induced_vert_break`, `track_context_abs_horz_break`, `track_context_extension`, `track_context_zone_speed`
- removed features: none
- model changes: none

### track_pitchmix

- declared change: 공식 Trackman 구종 선택 비율 3개 추가
- added features: `track_context_fastball_share`, `track_context_breaking_share`, `track_context_offspeed_share`
- removed features: none
- model changes: none

### track_all

- declared change: Trackman 물리 6개와 구종 비율 3개 전체 추가
- added features: `track_context_rel_speed`, `track_context_spin_rate`, `track_context_induced_vert_break`, `track_context_abs_horz_break`, `track_context_extension`, `track_context_zone_speed`, `track_context_fastball_share`, `track_context_breaking_share`, `track_context_offspeed_share`
- removed features: none
- model changes: none
