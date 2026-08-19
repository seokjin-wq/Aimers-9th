# 107_track_velocity_triple_promotion: Trackman velocity promotion to corrected triple

- 가설: The official Trackman velocity pair retains its CPU gain in the corrected CPU50/GPU35/Extra15 ensemble with train-only count calibration.
- control: `current_corrected_triple`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `04234e24d9c3`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| current_corrected_triple | control: EXP_103 corrected count-calibrated triple | 0.247463438 | 0.000000000 | 0/1 | 938.120 |
| track_velocity_corrected_triple | add EXP_106 official Trackman relative-speed and zone-speed context | 0.247464288 | 0.000000850 | 0/1 | 937.780 |

## 실제 변경 필드

- `current_corrected_triple`: control
- `track_velocity_corrected_triple`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/107_track_velocity_triple_promotion/20260818T100304891715Z_04234e24d9c3`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_106`
- 기준 variant: `track_velocity`
- 검증할 변경: Keep EXP_103 corrected count-calibrated triple fixed; compare current main72 against main72 plus only Trackman relative-speed and zone-speed context.

### current_corrected_triple

- role: control

### track_velocity_corrected_triple

- declared change: add EXP_106 official Trackman relative-speed and zone-speed context
- added features: `track_context_rel_speed`, `track_context_zone_speed`
- removed features: none
- model changes: none
