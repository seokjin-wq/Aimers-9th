# 070_cpu_gpu_extra_triple: CPU·GPU·ExtraTrees 3모델 앙상블

- 가설: CPU CatBoost, GPU CatBoost, ExtraTrees의 서로 다른 오차를 결합하면 2모델 앙상블보다 Brier가 낮아진다
- control: `cpu_only`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `da90de56c100`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| cpu45_gpu40_extra15 | CPU45 GPU40 Extra15 | 0.247496556 | -0.000041164 | 1/1 | 924.862 |
| cpu40_gpu45_extra15 | CPU40 GPU45 Extra15 | 0.247496623 | -0.000041098 | 1/1 | 924.836 |
| cpu40_gpu40_extra20 | CPU40 GPU40 Extra20 | 0.247497728 | -0.000039993 | 1/1 | 924.393 |
| cpu_only | control: CPU depth8 decay85 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |

## 실제 변경 필드

- `cpu_only`: control
- `cpu40_gpu45_extra15`: model.cat_scale, model.cat_shift, model.cpu_params.allow_writing_files, model.cpu_params.depth, model.cpu_params.eval_metric, model.cpu_params.iterations, model.cpu_params.l2_leaf_reg, model.cpu_params.learning_rate, model.cpu_params.loss_function, model.cpu_params.random_seed, model.cpu_params.subsample, model.cpu_params.task_type, model.cpu_params.thread_count, model.cpu_params.verbose, model.cpu_weight, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.gpu_params.allow_writing_files, model.gpu_params.bagging_temperature, model.gpu_params.bootstrap_type, model.gpu_params.border_count, model.gpu_params.depth, model.gpu_params.devices, model.gpu_params.eval_metric, model.gpu_params.iterations, model.gpu_params.l2_leaf_reg, model.gpu_params.learning_rate, model.gpu_params.loss_function, model.gpu_params.random_seed, model.gpu_params.task_type, model.gpu_params.verbose, model.gpu_weight, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `cpu45_gpu40_extra15`: model.cat_scale, model.cat_shift, model.cpu_params.allow_writing_files, model.cpu_params.depth, model.cpu_params.eval_metric, model.cpu_params.iterations, model.cpu_params.l2_leaf_reg, model.cpu_params.learning_rate, model.cpu_params.loss_function, model.cpu_params.random_seed, model.cpu_params.subsample, model.cpu_params.task_type, model.cpu_params.thread_count, model.cpu_params.verbose, model.cpu_weight, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.gpu_params.allow_writing_files, model.gpu_params.bagging_temperature, model.gpu_params.bootstrap_type, model.gpu_params.border_count, model.gpu_params.depth, model.gpu_params.devices, model.gpu_params.eval_metric, model.gpu_params.iterations, model.gpu_params.l2_leaf_reg, model.gpu_params.learning_rate, model.gpu_params.loss_function, model.gpu_params.random_seed, model.gpu_params.task_type, model.gpu_params.verbose, model.gpu_weight, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `cpu40_gpu40_extra20`: model.cat_scale, model.cat_shift, model.cpu_params.allow_writing_files, model.cpu_params.depth, model.cpu_params.eval_metric, model.cpu_params.iterations, model.cpu_params.l2_leaf_reg, model.cpu_params.learning_rate, model.cpu_params.loss_function, model.cpu_params.random_seed, model.cpu_params.subsample, model.cpu_params.task_type, model.cpu_params.thread_count, model.cpu_params.verbose, model.cpu_weight, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.gpu_params.allow_writing_files, model.gpu_params.bagging_temperature, model.gpu_params.bootstrap_type, model.gpu_params.border_count, model.gpu_params.depth, model.gpu_params.devices, model.gpu_params.eval_metric, model.gpu_params.iterations, model.gpu_params.l2_leaf_reg, model.gpu_params.learning_rate, model.gpu_params.loss_function, model.gpu_params.random_seed, model.gpu_params.task_type, model.gpu_params.verbose, model.gpu_weight, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/070_cpu_gpu_extra_triple/20260818T035139410969Z_da90de56c100`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_062`
- 기준 variant: `extra_w18`
- 검증할 변경: main69 고정 후 CPU/GPU/Extra 비중 40/45/15,45/40/15,40/40/20 비교

### cpu_only

- role: control

### cpu40_gpu45_extra15

- declared change: CPU40 GPU45 Extra15
- added features: none
- removed features: none
- model changes:
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.cpu_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cpu_weight`: `None` → `0.4`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.15`
  - `model.family`: `catboost` → `cat_cpu_gpu_extra_blend`
  - `model.gpu_params`: `None` → `{'iterations': 600, 'depth': 7, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.gpu_weight`: `None` → `0.45`
  - `model.name`: `catboost_d8_decay085` → `triple_cpu40_gpu45_extra15`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### cpu45_gpu40_extra15

- declared change: CPU45 GPU40 Extra15
- added features: none
- removed features: none
- model changes:
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.cpu_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cpu_weight`: `None` → `0.45`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.15`
  - `model.family`: `catboost` → `cat_cpu_gpu_extra_blend`
  - `model.gpu_params`: `None` → `{'iterations': 600, 'depth': 7, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.gpu_weight`: `None` → `0.4`
  - `model.name`: `catboost_d8_decay085` → `triple_cpu45_gpu40_extra15`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### cpu40_gpu40_extra20

- declared change: CPU40 GPU40 Extra20
- added features: none
- removed features: none
- model changes:
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.cpu_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cpu_weight`: `None` → `0.4`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.2`
  - `model.family`: `catboost` → `cat_cpu_gpu_extra_blend`
  - `model.gpu_params`: `None` → `{'iterations': 600, 'depth': 7, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.gpu_weight`: `None` → `0.4`
  - `model.name`: `catboost_d8_decay085` → `triple_cpu40_gpu40_extra20`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
