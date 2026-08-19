# 103_count_residual_scale: Count residual correction strength sweep

- 가설: The 2023 count residual pattern transfers to 2024, but its optimal amplitude differs from the current scale 1.0 after weight and mean refinement.
- control: `residual_scale_1_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `73180399c64f`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| residual_scale_1_control | control: EXP_102 residual scale 1.0 | 0.247463289 | 0.000000000 | 0/1 | 938.180 |
| residual_scale_0p75 | multiply train-only count residual offsets by 0.75 | 0.247463505 | 0.000000216 | 0/1 | 938.093 |
| residual_scale_1p25 | multiply train-only count residual offsets by 1.25 | 0.247464114 | 0.000000825 | 0/1 | 937.849 |
| residual_scale_0p5 | multiply train-only count residual offsets by 0.5 | 0.247464761 | 0.000001472 | 0/1 | 937.590 |
| residual_scale_1p5 | multiply train-only count residual offsets by 1.5 | 0.247465979 | 0.000002690 | 0/1 | 937.103 |
| residual_scale_2p0 | multiply train-only count residual offsets by 2.0 | 0.247472832 | 0.000009543 | 0/1 | 934.359 |

## 실제 변경 필드

- `residual_scale_1_control`: control
- `residual_scale_0p5`: model.name, model.residual_scale
- `residual_scale_0p75`: model.name, model.residual_scale
- `residual_scale_1p25`: model.name, model.residual_scale
- `residual_scale_1p5`: model.name, model.residual_scale
- `residual_scale_2p0`: model.name, model.residual_scale

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/103_count_residual_scale/20260818T092329206678Z_73180399c64f`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_102`
- 기준 variant: `w50_35_15`
- 검증할 변경: Keep features, component models, CPU50/GPU35/Extra15 weights, CatBoost shift -0.0095, count groups, and shrinkage 500 fixed; vary only residual_scale from 0.5 to 2.0.

### residual_scale_1_control

- role: control

### residual_scale_0p5

- declared change: multiply train-only count residual offsets by 0.5
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_count_k500_shift_m0095_w50_35_15_r0p5`
  - `model.residual_scale`: `1.0` → `0.5`

### residual_scale_0p75

- declared change: multiply train-only count residual offsets by 0.75
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_count_k500_shift_m0095_w50_35_15_r0p75`
  - `model.residual_scale`: `1.0` → `0.75`

### residual_scale_1p25

- declared change: multiply train-only count residual offsets by 1.25
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_count_k500_shift_m0095_w50_35_15_r1p25`
  - `model.residual_scale`: `1.0` → `1.25`

### residual_scale_1p5

- declared change: multiply train-only count residual offsets by 1.5
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_count_k500_shift_m0095_w50_35_15_r1p5`
  - `model.residual_scale`: `1.0` → `1.5`

### residual_scale_2p0

- declared change: multiply train-only count residual offsets by 2.0
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_count_k500_shift_m0095_w50_35_15_r2`
  - `model.residual_scale`: `1.0` → `2.0`
