# 102_count_triple_weights: Count-calibrated triple weight refinement

- 가설: On the latest features and corrected cache, a nearby CPU/GPU/ExtraTrees mixture improves the count-calibrated ensemble beyond 45/40/15.
- control: `w45_40_15_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a4bef650c15a`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| w50_35_15 | CPU50 GPU35 Extra15 | 0.247471308 | -0.000000557 | 1/1 | 934.970 |
| w45_40_15_control | control: EXP_101 CPU45 GPU40 Extra15 | 0.247471864 | 0.000000000 | 0/1 | 934.747 |
| w50_30_20 | CPU50 GPU30 Extra20 | 0.247471963 | 0.000000099 | 0/1 | 934.707 |
| w45_35_20 | CPU45 GPU35 Extra20 | 0.247472276 | 0.000000412 | 0/1 | 934.582 |
| w40_45_15 | CPU40 GPU45 Extra15 | 0.247472957 | 0.000001093 | 0/1 | 934.309 |
| w50_40_10 | CPU50 GPU40 Extra10 | 0.247473692 | 0.000001828 | 0/1 | 934.015 |
| w40_50_10 | CPU40 GPU50 Extra10 | 0.247475829 | 0.000003965 | 0/1 | 933.160 |

## 실제 변경 필드

- `w45_40_15_control`: control
- `w50_35_15`: model.cpu_weight, model.gpu_weight, model.name
- `w40_45_15`: model.cpu_weight, model.gpu_weight, model.name
- `w45_35_20`: model.extra_weight, model.gpu_weight, model.name
- `w50_40_10`: model.cpu_weight, model.extra_weight, model.name
- `w40_50_10`: model.cpu_weight, model.extra_weight, model.gpu_weight, model.name
- `w50_30_20`: model.cpu_weight, model.extra_weight, model.gpu_weight, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/102_count_triple_weights/20260818T091032367011Z_a4bef650c15a`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_101`
- 기준 variant: `catshift_m0095`
- 검증할 변경: Keep all component models, features, CatBoost shift -0.0095, and train-only count-k500 calibration fixed; vary only CPU/GPU/ExtraTrees weights around 45/40/15.

### w45_40_15_control

- role: control

### w50_35_15

- declared change: CPU50 GPU35 Extra15
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.5`
  - `model.gpu_weight`: `0.4` → `0.35`
  - `model.name`: `triple_group_count_k500_catshift_m0095` → `triple_group_count_k500_shift_m0095_w50_35_15`

### w40_45_15

- declared change: CPU40 GPU45 Extra15
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.4`
  - `model.gpu_weight`: `0.4` → `0.45`
  - `model.name`: `triple_group_count_k500_catshift_m0095` → `triple_group_count_k500_shift_m0095_w40_45_15`

### w45_35_20

- declared change: CPU45 GPU35 Extra20
- added features: none
- removed features: none
- model changes:
  - `model.extra_weight`: `0.15` → `0.2`
  - `model.gpu_weight`: `0.4` → `0.35`
  - `model.name`: `triple_group_count_k500_catshift_m0095` → `triple_group_count_k500_shift_m0095_w45_35_20`

### w50_40_10

- declared change: CPU50 GPU40 Extra10
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.5`
  - `model.extra_weight`: `0.15` → `0.1`
  - `model.name`: `triple_group_count_k500_catshift_m0095` → `triple_group_count_k500_shift_m0095_w50_40_10`

### w40_50_10

- declared change: CPU40 GPU50 Extra10
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.4`
  - `model.extra_weight`: `0.15` → `0.1`
  - `model.gpu_weight`: `0.4` → `0.5`
  - `model.name`: `triple_group_count_k500_catshift_m0095` → `triple_group_count_k500_shift_m0095_w40_50_10`

### w50_30_20

- declared change: CPU50 GPU30 Extra20
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.5`
  - `model.extra_weight`: `0.15` → `0.2`
  - `model.gpu_weight`: `0.4` → `0.3`
  - `model.name`: `triple_group_count_k500_catshift_m0095` → `triple_group_count_k500_shift_m0095_w50_30_20`
