# 033_probability_calibration: 직전 시즌 확률 보정

- 가설: 직전 시즌 out-of-time 예측으로 학습한 보정 함수가 다음 시즌 calibration을 개선한다
- control: `global_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b2c89b5ce24e`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| global_control | control: 직접 고른 affine 보정 GPU CatBoost | 0.247814444 | 0.000000000 | 0/1 | 797.609 |
| mean_shift | 2023 평균 예측 오차만 보정 | 0.247970665 | 0.000156222 | 0/1 | 735.072 |
| beta | 2023 beta calibration | 0.248152383 | 0.000337939 | 0/1 | 662.329 |
| isotonic | 2023 isotonic 비모수 보정 | 0.248253612 | 0.000439168 | 0/1 | 621.806 |
| affine | 2023 선형 최소제곱 보정 | 0.249167319 | 0.001352876 | 0/1 | 256.041 |
| platt | 2023 logit Platt 보정 | 0.249219082 | 0.001404638 | 0/1 | 235.320 |

## 실제 변경 필드

- `global_control`: control
- `mean_shift`: model.calibration_method, model.cat_params.allow_writing_files, model.cat_params.bagging_temperature, model.cat_params.bootstrap_type, model.cat_params.border_count, model.cat_params.depth, model.cat_params.devices, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.task_type, model.cat_params.verbose, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.task_type, model.params.verbose, model.prediction_scale, model.prediction_shift
- `affine`: model.calibration_method, model.cat_params.allow_writing_files, model.cat_params.bagging_temperature, model.cat_params.bootstrap_type, model.cat_params.border_count, model.cat_params.depth, model.cat_params.devices, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.task_type, model.cat_params.verbose, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.task_type, model.params.verbose, model.prediction_scale, model.prediction_shift
- `platt`: model.calibration_c, model.calibration_method, model.cat_params.allow_writing_files, model.cat_params.bagging_temperature, model.cat_params.bootstrap_type, model.cat_params.border_count, model.cat_params.depth, model.cat_params.devices, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.task_type, model.cat_params.verbose, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.task_type, model.params.verbose, model.prediction_scale, model.prediction_shift
- `beta`: model.calibration_c, model.calibration_method, model.cat_params.allow_writing_files, model.cat_params.bagging_temperature, model.cat_params.bootstrap_type, model.cat_params.border_count, model.cat_params.depth, model.cat_params.devices, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.task_type, model.cat_params.verbose, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.task_type, model.params.verbose, model.prediction_scale, model.prediction_shift
- `isotonic`: model.calibration_method, model.cat_params.allow_writing_files, model.cat_params.bagging_temperature, model.cat_params.bootstrap_type, model.cat_params.border_count, model.cat_params.depth, model.cat_params.devices, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.task_type, model.cat_params.verbose, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.task_type, model.params.verbose, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/033_probability_calibration/20260817T182043107786Z_b2c89b5ce24e`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_032`
- 기준 variant: `global_control`
- 검증할 변경: CatBoost와 main60을 고정하고 2019~2022→2023 예측에서 학습한 mean-shift, affine, Platt, beta, isotonic 보정만 변경

### global_control

- role: control

### mean_shift

- declared change: 2023 평균 예측 오차만 보정
- added features: none
- removed features: none
- model changes:
  - `model.calibration_method`: `None` → `mean_shift`
  - `model.cat_params`: `None` → `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.family`: `catboost` → `catboost_probability_calibrated`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catcal_mean_shift`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### affine

- declared change: 2023 선형 최소제곱 보정
- added features: none
- removed features: none
- model changes:
  - `model.calibration_method`: `None` → `affine`
  - `model.cat_params`: `None` → `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.family`: `catboost` → `catboost_probability_calibrated`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catcal_affine`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### platt

- declared change: 2023 logit Platt 보정
- added features: none
- removed features: none
- model changes:
  - `model.calibration_c`: `None` → `1000.0`
  - `model.calibration_method`: `None` → `platt`
  - `model.cat_params`: `None` → `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.family`: `catboost` → `catboost_probability_calibrated`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catcal_platt`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### beta

- declared change: 2023 beta calibration
- added features: none
- removed features: none
- model changes:
  - `model.calibration_c`: `None` → `1000.0`
  - `model.calibration_method`: `None` → `beta`
  - `model.cat_params`: `None` → `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.family`: `catboost` → `catboost_probability_calibrated`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catcal_beta`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### isotonic

- declared change: 2023 isotonic 비모수 보정
- added features: none
- removed features: none
- model changes:
  - `model.calibration_method`: `None` → `isotonic`
  - `model.cat_params`: `None` → `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.family`: `catboost` → `catboost_probability_calibrated`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catcal_isotonic`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 600, 'depth': 6, 'learning_rate': 0.025, 'l2_leaf_reg': 3.0, 'bootstrap_type': 'Bayesian', 'bagging_temperature': 1.0, 'border_count': 128, 'random_seed': 42, 'task_type': 'GPU', 'devices': '0', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
