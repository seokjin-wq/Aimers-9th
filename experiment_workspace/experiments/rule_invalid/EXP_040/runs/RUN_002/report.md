# 040_sequence_diverse_models: 순차 피처 이종 모델 후보

- 가설: 순차 피처 ExtraTrees와 seed 평균이 CatBoost 오차를 보완한다
- control: `cat_single_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `08c7d5c398c1`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| cat_single_control | control: CatBoost depth6 900 | 0.246899243 | 0.000000000 | 0/1 | 1163.972 |
| cat_ensemble3 | 동일 CatBoost 3-seed 확률 평균 | 0.246907346 | 0.000008103 | 0/1 | 1160.729 |
| extra_leaf50 | ExtraTrees leaf50 | 0.247329809 | 0.000430566 | 0/1 | 991.613 |
| extra_leaf20 | ExtraTrees leaf20 | 0.247636774 | 0.000737531 | 0/1 | 868.732 |
| extra_leaf10 | ExtraTrees leaf10 | 0.248290663 | 0.001391420 | 0/1 | 606.974 |
| extra_leaf5 | ExtraTrees leaf5 | 0.249222008 | 0.002322764 | 0/1 | 234.148 |

## 실제 변경 필드

- `cat_single_control`: control
- `cat_ensemble3`: model.family, model.name, model.params.random_seed, model.seeds
- `extra_leaf5`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_features, model.params.min_samples_leaf, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.task_type, model.prediction_scale, model.prediction_shift
- `extra_leaf10`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_features, model.params.min_samples_leaf, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.task_type, model.prediction_scale, model.prediction_shift
- `extra_leaf20`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_features, model.params.min_samples_leaf, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.task_type, model.prediction_scale, model.prediction_shift
- `extra_leaf50`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_features, model.params.min_samples_leaf, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.task_type, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/040_sequence_diverse_models/20260817T185801156155Z_08c7d5c398c1`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_039`
- 기준 variant: `d6_i900`
- 검증할 변경: main85를 고정하고 CatBoost 3-seed 평균과 ExtraTrees min_samples_leaf 5·10·20·50만 비교

### cat_single_control

- role: control

### cat_ensemble3

- declared change: 동일 CatBoost 3-seed 확률 평균
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_ensemble`
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `catboost_gpu_d6_i900_ensemble3`
  - `model.params.random_seed`: `42` → `None`
  - `model.seeds`: `None` → `[17, 42, 97]`

### extra_leaf5

- declared change: ExtraTrees leaf5
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `extra_trees`
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `extratrees_leaf5`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.bagging_temperature`: `1.0` → `None`
  - `model.params.bootstrap_type`: `Bayesian` → `None`
  - `model.params.border_count`: `128` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.devices`: `0` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `900` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.02` → `None`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_features`: `None` → `0.7`
  - `model.params.min_samples_leaf`: `None` → `5`
  - `model.params.n_estimators`: `None` → `100`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.task_type`: `GPU` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`

### extra_leaf10

- declared change: ExtraTrees leaf10
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `extra_trees`
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `extratrees_leaf10`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.bagging_temperature`: `1.0` → `None`
  - `model.params.bootstrap_type`: `Bayesian` → `None`
  - `model.params.border_count`: `128` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.devices`: `0` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `900` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.02` → `None`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_features`: `None` → `0.7`
  - `model.params.min_samples_leaf`: `None` → `10`
  - `model.params.n_estimators`: `None` → `100`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.task_type`: `GPU` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`

### extra_leaf20

- declared change: ExtraTrees leaf20
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `extra_trees`
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `extratrees_leaf20_screen`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.bagging_temperature`: `1.0` → `None`
  - `model.params.bootstrap_type`: `Bayesian` → `None`
  - `model.params.border_count`: `128` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.devices`: `0` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `900` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.02` → `None`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_features`: `None` → `0.7`
  - `model.params.min_samples_leaf`: `None` → `20`
  - `model.params.n_estimators`: `None` → `100`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.task_type`: `GPU` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`

### extra_leaf50

- declared change: ExtraTrees leaf50
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `extra_trees`
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `extratrees_leaf50`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.bagging_temperature`: `1.0` → `None`
  - `model.params.bootstrap_type`: `Bayesian` → `None`
  - `model.params.border_count`: `128` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.devices`: `0` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `900` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.02` → `None`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_features`: `None` → `0.7`
  - `model.params.min_samples_leaf`: `None` → `50`
  - `model.params.n_estimators`: `None` → `100`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.task_type`: `GPU` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`
