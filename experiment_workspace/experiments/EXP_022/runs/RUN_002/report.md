# 022_catboost_structure: CatBoost 부스팅 구조와 bootstrap

- 가설: 현재 symmetric tree와 기본 bootstrap보다 다른 샘플링 또는 tree grow 정책이 일반화 Brier를 개선한다
- control: `default_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `7f3fb6ed9024`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| default_control | control: 기본 bootstrap, SymmetricTree | 0.247820321 | 0.000000000 | 0/1 | 795.256 |
| no_bootstrap | bootstrap 없음 | 0.247822872 | 0.000002551 | 0/1 | 794.235 |
| bernoulli | Bernoulli bootstrap | 0.247839942 | 0.000019621 | 0/1 | 787.402 |
| leaf_estimation_1 | leaf estimation 1회 | 0.247842626 | 0.000022306 | 0/1 | 786.327 |
| leaf_estimation_20 | leaf estimation 20회 | 0.247845177 | 0.000024856 | 0/1 | 785.306 |
| bayesian | Bayesian bootstrap | 0.247867335 | 0.000047014 | 0/1 | 776.436 |
| lossguide | Lossguide grow policy | 0.247894516 | 0.000074196 | 0/1 | 765.555 |
| depthwise | Depthwise grow policy | 0.247956811 | 0.000136490 | 0/1 | 740.618 |

## 실제 변경 필드

- `default_control`: control
- `bernoulli`: model.name, model.params.bootstrap_type
- `bayesian`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.subsample
- `no_bootstrap`: model.name, model.params.bootstrap_type, model.params.subsample
- `depthwise`: model.name, model.params.grow_policy, model.params.min_data_in_leaf
- `lossguide`: model.name, model.params.grow_policy, model.params.max_leaves, model.params.min_data_in_leaf
- `leaf_estimation_1`: model.name, model.params.leaf_estimation_iterations
- `leaf_estimation_20`: model.name, model.params.leaf_estimation_iterations

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/022_catboost_structure/20260817T171345506411Z_7f3fb6ed9024`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_021`
- 기준 variant: `main60_control`
- 검증할 변경: 최고 피처와 affine 보정을 고정하고 bootstrap_type, boosting_type, grow_policy, leaf estimation만 한 종류씩 변경

### default_control

- role: control

### bernoulli

- declared change: Bernoulli bootstrap
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_bernoulli`
  - `model.params.bootstrap_type`: `None` → `Bernoulli`

### bayesian

- declared change: Bayesian bootstrap
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_bayesian`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.subsample`: `0.7` → `None`

### no_bootstrap

- declared change: bootstrap 없음
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_no_bootstrap`
  - `model.params.bootstrap_type`: `None` → `No`
  - `model.params.subsample`: `0.7` → `None`

### depthwise

- declared change: Depthwise grow policy
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_depthwise`
  - `model.params.grow_policy`: `None` → `Depthwise`
  - `model.params.min_data_in_leaf`: `None` → `20`

### lossguide

- declared change: Lossguide grow policy
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_lossguide`
  - `model.params.grow_policy`: `None` → `Lossguide`
  - `model.params.max_leaves`: `None` → `64`
  - `model.params.min_data_in_leaf`: `None` → `20`

### leaf_estimation_1

- declared change: leaf estimation 1회
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_leaf1`
  - `model.params.leaf_estimation_iterations`: `None` → `1`

### leaf_estimation_20

- declared change: leaf estimation 20회
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_leaf20`
  - `model.params.leaf_estimation_iterations`: `None` → `20`
