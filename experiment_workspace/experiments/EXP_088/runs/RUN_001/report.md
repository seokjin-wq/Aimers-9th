# 088_triple_group_calibration: 2023 OOT residual만 사용한 현재 최고 앙상블 그룹 보정

- 가설: 2023에서 반복된 상황별 잔차 편향이 2024로 전이된다.
- control: `triple_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `7b5509745a5d`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_k500 | 2023 ball×strike residual, shrinkage 500 | 0.247464776 | -0.000007002 | 1/1 | 937.584 |
| count_k2000 | 2023 ball×strike residual, shrinkage 2000 | 0.247464883 | -0.000006895 | 1/1 | 937.541 |
| count_out_k2000 | 2023 ball×strike×out residual, shrinkage 2000 | 0.247468706 | -0.000003072 | 1/1 | 936.011 |
| triple_control | control: EXP_087 same-hand pitchmix triple | 0.247471778 | 0.000000000 | 0/1 | 934.781 |
| count_out_k500 | 2023 ball×strike×out residual, shrinkage 500 | 0.247474372 | 0.000002594 | 0/1 | 933.743 |
| count_out_raw_k2000 | 2023 global bias를 보존한 ball×strike×out residual, shrinkage 2000 | 0.247496533 | 0.000024755 | 0/1 | 924.872 |
| month_count_k2000 | 2023 month×ball×strike residual, shrinkage 2000 | 0.247527202 | 0.000055424 | 0/1 | 912.595 |
| batter_team_k2000 | 2023 batter-team residual, shrinkage 2000 | 0.247626745 | 0.000154966 | 0/1 | 872.747 |

## 실제 변경 필드

- `triple_control`: control
- `count_k500`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale
- `count_k2000`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale
- `count_out_k500`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale
- `count_out_k2000`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale
- `month_count_k2000`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale
- `batter_team_k2000`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale
- `count_out_raw_k2000`: model.center_residual, model.group_columns, model.group_shrinkage, model.name, model.residual_scale

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/088_triple_group_calibration/20260818T063921342559Z_7b5509745a5d`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_087`
- 기준 variant: `same_hand_pitchmix_triple`
- 검증할 변경: Fix EXP_087 features and triple components; fit group residual offsets only from 2019-2022→2023 predictions and vary group columns and shrinkage before applying to 2024.

### triple_control

- role: control

### count_k500

- declared change: 2023 ball×strike residual, shrinkage 500
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before']`
  - `model.group_shrinkage`: `None` → `500.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_count_k500`
  - `model.residual_scale`: `None` → `1.0`

### count_k2000

- declared change: 2023 ball×strike residual, shrinkage 2000
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before']`
  - `model.group_shrinkage`: `None` → `2000.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_count_k2000`
  - `model.residual_scale`: `None` → `1.0`

### count_out_k500

- declared change: 2023 ball×strike×out residual, shrinkage 500
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before', 'outs_before']`
  - `model.group_shrinkage`: `None` → `500.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_count_out_k500`
  - `model.residual_scale`: `None` → `1.0`

### count_out_k2000

- declared change: 2023 ball×strike×out residual, shrinkage 2000
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before', 'outs_before']`
  - `model.group_shrinkage`: `None` → `2000.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_count_out_k2000`
  - `model.residual_scale`: `None` → `1.0`

### month_count_k2000

- declared change: 2023 month×ball×strike residual, shrinkage 2000
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['game_month', 'balls_before', 'strikes_before']`
  - `model.group_shrinkage`: `None` → `2000.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_month_count_k2000`
  - `model.residual_scale`: `None` → `1.0`

### batter_team_k2000

- declared change: 2023 batter-team residual, shrinkage 2000
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `True`
  - `model.group_columns`: `None` → `['batter_team_id']`
  - `model.group_shrinkage`: `None` → `2000.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_batter_team_k2000`
  - `model.residual_scale`: `None` → `1.0`

### count_out_raw_k2000

- declared change: 2023 global bias를 보존한 ball×strike×out residual, shrinkage 2000
- added features: none
- removed features: none
- model changes:
  - `model.center_residual`: `None` → `False`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before', 'outs_before']`
  - `model.group_shrinkage`: `None` → `2000.0`
  - `model.name`: `triple_cpu45_gpu40_extra15` → `triple_group_count_out_raw_k2000`
  - `model.residual_scale`: `None` → `1.0`
