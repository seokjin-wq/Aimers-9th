# 012_catboost_regularization: CatBoost 규제 단일축 탐색

- 가설: 300-tree 구조를 유지하면서 규제를 조정하면 2024 과적합을 줄여 Brier가 개선된다
- control: `default_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `c67c688e28ec`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| default_control | control: 기본 규제 | 0.247968140 | 0.000000000 | 0/1 | 736.083 |
| random_strength_0 | random_strength 기본 1→0 | 0.248004528 | 0.000036388 | 0/1 | 721.517 |
| l2_30 | l2_leaf_reg 3→30 | 0.248007425 | 0.000039285 | 0/1 | 720.357 |
| rsm_08 | tree별 feature 비율 rsm 0.8 | 0.248010348 | 0.000042208 | 0/1 | 719.187 |
| subsample_09 | row subsample 0.7→0.9 | 0.248014765 | 0.000046625 | 0/1 | 717.419 |
| l2_10 | l2_leaf_reg 3→10 | 0.248017848 | 0.000049708 | 0/1 | 716.185 |
| subsample_05 | row subsample 0.7→0.5 | 0.248024013 | 0.000055873 | 0/1 | 713.717 |
| border_count_64 | numeric border_count를 64로 제한 | 0.248031386 | 0.000063246 | 0/1 | 710.765 |
| rsm_06 | tree별 feature 비율 rsm 0.6 | 0.248037913 | 0.000069773 | 0/1 | 708.152 |
| random_strength_3 | random_strength 기본 1→3 | 0.248071018 | 0.000102878 | 0/1 | 694.900 |

## 실제 변경 필드

- `default_control`: control
- `l2_10`: model.name, model.params.l2_leaf_reg
- `l2_30`: model.name, model.params.l2_leaf_reg
- `random_strength_0`: model.name, model.params.random_strength
- `random_strength_3`: model.name, model.params.random_strength
- `rsm_06`: model.name, model.params.rsm
- `rsm_08`: model.name, model.params.rsm
- `subsample_05`: model.name, model.params.subsample
- `subsample_09`: model.name, model.params.subsample
- `border_count_64`: model.name, model.params.border_count

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/012_catboost_regularization/20260817T161656703786Z_c67c688e28ec`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_011`
- 기준 variant: `uniform_control`
- 검증할 변경: main55+count, depth6, 300 trees를 고정하고 l2, random_strength, rsm, subsample, border_count를 각각 단일축으로 변경

### default_control

- role: control

### l2_10

- declared change: l2_leaf_reg 3→10
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_l2_10`
  - `model.params.l2_leaf_reg`: `3.0` → `10.0`

### l2_30

- declared change: l2_leaf_reg 3→30
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_l2_30`
  - `model.params.l2_leaf_reg`: `3.0` → `30.0`

### random_strength_0

- declared change: random_strength 기본 1→0
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_random0`
  - `model.params.random_strength`: `None` → `0.0`

### random_strength_3

- declared change: random_strength 기본 1→3
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_random3`
  - `model.params.random_strength`: `None` → `3.0`

### rsm_06

- declared change: tree별 feature 비율 rsm 0.6
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_rsm06`
  - `model.params.rsm`: `None` → `0.6`

### rsm_08

- declared change: tree별 feature 비율 rsm 0.8
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_rsm08`
  - `model.params.rsm`: `None` → `0.8`

### subsample_05

- declared change: row subsample 0.7→0.5
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_sub05`
  - `model.params.subsample`: `0.7` → `0.5`

### subsample_09

- declared change: row subsample 0.7→0.9
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_sub09`
  - `model.params.subsample`: `0.7` → `0.9`

### border_count_64

- declared change: numeric border_count를 64로 제한
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_border64`
  - `model.params.border_count`: `None` → `64`
