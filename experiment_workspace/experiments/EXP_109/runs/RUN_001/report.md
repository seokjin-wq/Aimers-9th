# 109_latest_catboost_regularization: Latest CatBoost local regularization sweep

- 가설: The expanded 72-feature representation may prefer nearby regularization settings different from the early 55-feature model, improving probability calibration without changing row-independent inputs.
- control: `regularization_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `02a7bf14fa82`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| subsample_08 | subsample 0.7 -> 0.8 only | 0.247504172 | -0.000007695 | 1/1 | 921.814 |
| regularization_control | control: l2=3, random_strength=1, subsample=0.7, rsm=1 | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| l2_8 | l2_leaf_reg 3 -> 8 only | 0.247514132 | 0.000002265 | 0/1 | 917.827 |
| l2_1 | l2_leaf_reg 3 -> 1 only | 0.247546682 | 0.000034815 | 0/1 | 904.797 |
| random_strength_05 | random_strength 1 -> 0.5 only | 0.247559148 | 0.000047282 | 0/1 | 899.806 |
| random_strength_15 | random_strength 1 -> 1.5 only | 0.247560064 | 0.000048198 | 0/1 | 899.440 |
| l2_5 | l2_leaf_reg 3 -> 5 only | 0.247561338 | 0.000049472 | 0/1 | 898.930 |
| rsm_09 | rsm 1.0 -> 0.9 only | 0.247582813 | 0.000070947 | 0/1 | 890.333 |

## 실제 변경 필드

- `regularization_control`: control
- `l2_1`: model.name, model.params.l2_leaf_reg
- `l2_5`: model.name, model.params.l2_leaf_reg
- `l2_8`: model.name, model.params.l2_leaf_reg
- `random_strength_05`: model.name, model.params.random_strength
- `random_strength_15`: model.name, model.params.random_strength
- `subsample_08`: model.name, model.params.subsample
- `rsm_09`: model.name, model.params.rsm

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/109_latest_catboost_regularization/20260818T103834987105Z_02a7bf14fa82`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_108`
- 기준 variant: `main72_control`
- 검증할 변경: Hold main72 features, 2019-2023 training, 2024 validation, depth, iterations, learning rate, decay, and seed fixed; change exactly one of l2_leaf_reg, random_strength, subsample, or rsm per candidate.

### regularization_control

- role: control

### l2_1

- declared change: l2_leaf_reg 3 -> 1 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_l2_1`
  - `model.params.l2_leaf_reg`: `3.0` → `1.0`

### l2_5

- declared change: l2_leaf_reg 3 -> 5 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_l2_5`
  - `model.params.l2_leaf_reg`: `3.0` → `5.0`

### l2_8

- declared change: l2_leaf_reg 3 -> 8 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_l2_8`
  - `model.params.l2_leaf_reg`: `3.0` → `8.0`

### random_strength_05

- declared change: random_strength 1 -> 0.5 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_rs05`
  - `model.params.random_strength`: `None` → `0.5`

### random_strength_15

- declared change: random_strength 1 -> 1.5 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_rs15`
  - `model.params.random_strength`: `None` → `1.5`

### subsample_08

- declared change: subsample 0.7 -> 0.8 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_sub08`
  - `model.params.subsample`: `0.7` → `0.8`

### rsm_09

- declared change: rsm 1.0 -> 0.9 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_rsm09`
  - `model.params.rsm`: `None` → `0.9`
