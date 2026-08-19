# 094_count_calibration_repro: 현재 최고 count OOT 보정의 fresh-run 재현성 감사

- 가설: count k500 개선이 GPU 변동보다 커 새 실행에서도 control을 이긴다.
- control: `triple_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `703d2c5a6e6c`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_k500_repro | EXP_088 count residual k500 동일 설정 재현 | 0.247465030 | -0.000007066 | 1/1 | 937.483 |
| count_k2000_repro | EXP_088 count residual k2000 동일 설정 재현 | 0.247465140 | -0.000006956 | 1/1 | 937.439 |
| triple_control | control: EXP_087 same-hand triple fresh run | 0.247472097 | 0.000000000 | 0/1 | 934.654 |

## 실제 변경 필드

- `triple_control`: control
- `count_k500_repro`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale
- `count_k2000_repro`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/094_count_calibration_repro/20260818T073334425645Z_703d2c5a6e6c`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_088`
- 기준 variant: `count_k500`
- 검증할 변경: Freshly rerun the identical triple control, count k500, and count k2000 settings; no feature or parameter search.

### triple_control

- role: control

### count_k500_repro

- declared change: EXP_088 count residual k500 동일 설정 재현
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before']`
  - `model.group_shrinkage`: `None` → `500.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_count_k500`
  - `model.residual_scale`: `None` → `1.0`

### count_k2000_repro

- declared change: EXP_088 count residual k2000 동일 설정 재현
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before']`
  - `model.group_shrinkage`: `None` → `2000.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_count_k2000`
  - `model.residual_scale`: `None` → `1.0`
