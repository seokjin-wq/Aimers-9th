# 117_reliability_blend_weights: Reliability triple blend-weight refinement

- 가설: The reliability-enhanced CPU component may deserve more weight than the original 45/40/15 allocation, improving the corrected triple blend.
- control: `weights_45_40_15_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `7eabc346f415`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| weights_50_35_15 | move 5% weight GPU -> CPU only | 0.247451579 | -0.000000451 | 1/1 | 942.867 |
| weights_55_30_15 | move 10% weight GPU -> CPU only | 0.247451703 | -0.000000327 | 1/1 | 942.818 |
| weights_45_40_15_control | control: EXP_116 winner CPU/GPU/Extra=45/40/15 | 0.247452030 | 0.000000000 | 0/1 | 942.687 |
| weights_50_40_10 | move 5% weight ExtraTrees -> CPU only | 0.247452409 | 0.000000379 | 0/1 | 942.535 |

## 실제 변경 필드

- `weights_45_40_15_control`: control
- `weights_50_35_15`: model.cpu_weight, model.gpu_weight, model.name
- `weights_55_30_15`: model.cpu_weight, model.gpu_weight, model.name
- `weights_50_40_10`: model.cpu_weight, model.extra_weight, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/117_reliability_blend_weights/20260818T120325331805Z_7eabc346f415`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_116`
- 기준 variant: `triple_history_reliability`
- 검증할 변경: Fix main78 reliability features, all component parameters, shifts, count correction, and ExtraTrees weight where applicable; vary only CPU/GPU/Extra blend weights around 45/40/15.

### weights_45_40_15_control

- role: control

### weights_50_35_15

- declared change: move 5% weight GPU -> CPU only
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.5`
  - `model.gpu_weight`: `0.4` → `0.35`
  - `model.name`: `triple_group_count_k500_catshift_m0095_cpu_sub08` → `triple_count_m0095_sub08_w50_35_15`

### weights_55_30_15

- declared change: move 10% weight GPU -> CPU only
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.55`
  - `model.gpu_weight`: `0.4` → `0.3`
  - `model.name`: `triple_group_count_k500_catshift_m0095_cpu_sub08` → `triple_count_m0095_sub08_w55_30_15`

### weights_50_40_10

- declared change: move 5% weight ExtraTrees -> CPU only
- added features: none
- removed features: none
- model changes:
  - `model.cpu_weight`: `0.45` → `0.5`
  - `model.extra_weight`: `0.15` → `0.1`
  - `model.name`: `triple_group_count_k500_catshift_m0095_cpu_sub08` → `triple_count_m0095_sub08_w50_40_10`
