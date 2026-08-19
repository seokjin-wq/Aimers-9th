# 126_oot_simplex_blend_weights: OOT-learned simplex blend weights

- 가설: Nonnegative ensemble weights learned only from 2019-2022 to 2023 OOT predictions will better combine CPU/GPU/Extra errors for 2024 than fixed manual weights.
- control: `manual_weights_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `922489f64e9a`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| manual_weights_control | control: fixed manual CPU/GPU/Extra weights 50/35/15 | 0.247451584 | 0.000000000 | 0/1 | 942.865 |
| oot_weight_strength_025 | move 25% from manual weights toward 2023 OOT simplex optimum | 0.247454678 | 0.000003095 | 0/1 | 941.627 |
| oot_weight_strength_050 | move 50% from manual weights toward 2023 OOT simplex optimum | 0.247464262 | 0.000012679 | 0/1 | 937.790 |
| oot_weight_strength_100 | use 2023 OOT simplex-optimal weights directly | 0.247502896 | 0.000051312 | 0/1 | 922.325 |

## 실제 변경 필드

- `manual_weights_control`: control
- `oot_weight_strength_025`: model.learned_weight_strength, model.name
- `oot_weight_strength_050`: model.learned_weight_strength, model.name
- `oot_weight_strength_100`: model.learned_weight_strength, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/126_oot_simplex_blend_weights/20260818T133306011733Z_922489f64e9a`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_117`
- 기준 variant: `weights_50_35_15`
- 검증할 변경: Fix main78 features, all component models, shifts, and count correction; blend manual 50/35/15 weights toward 2023 OOT simplex-optimal weights by 25%, 50%, or 100%.

### manual_weights_control

- role: control

### oot_weight_strength_025

- declared change: move 25% from manual weights toward 2023 OOT simplex optimum
- added features: none
- removed features: none
- model changes:
  - `model.learned_weight_strength`: `None` → `0.25`
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_oot_weights_s025`

### oot_weight_strength_050

- declared change: move 50% from manual weights toward 2023 OOT simplex optimum
- added features: none
- removed features: none
- model changes:
  - `model.learned_weight_strength`: `None` → `0.5`
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_oot_weights_s050`

### oot_weight_strength_100

- declared change: use 2023 OOT simplex-optimal weights directly
- added features: none
- removed features: none
- model changes:
  - `model.learned_weight_strength`: `None` → `1.0`
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_oot_weights_s100`
