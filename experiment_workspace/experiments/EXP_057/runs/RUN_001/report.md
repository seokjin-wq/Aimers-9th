# 057_season_state_cat_extra_blend: 시즌 상태 모델 이종 앙상블

- 가설: 새 시즌 상태 피처에서도 CatBoost와 ExtraTrees의 오차 다양성이 유지되어 15~32% 혼합이 Brier를 추가 개선한다
- control: `catboost_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b3ac66fbebdd`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| extra_w24 | ExtraTrees 24% 혼합 | 0.247556760 | -0.000042509 | 1/1 | 900.763 |
| extra_w28 | ExtraTrees 28% 혼합 | 0.247556971 | -0.000042298 | 1/1 | 900.678 |
| extra_w20 | ExtraTrees 20% 혼합 | 0.247558633 | -0.000040635 | 1/1 | 900.013 |
| extra_w32 | ExtraTrees 32% 혼합 | 0.247559266 | -0.000040002 | 1/1 | 899.759 |
| extra_w15 | ExtraTrees 15% 혼합 | 0.247563906 | -0.000035362 | 1/1 | 897.902 |
| catboost_control | control: EXP_056 최고 CatBoost | 0.247599268 | 0.000000000 | 0/1 | 883.746 |

## 실제 변경 필드

- `catboost_control`: control
- `extra_w15`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w20`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w24`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w28`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w32`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/057_season_state_cat_extra_blend/20260818T023727437490Z_b3ac66fbebdd`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_056`
- 기준 variant: `pitcher_batter_season_all`
- 검증할 변경: main69 피처를 고정하고 CatBoost 단독 대비 ExtraTrees 가중치 15,20,24,28,32%만 변경

### catboost_control

- role: control

### extra_w15

- declared change: ExtraTrees 15% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.15`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_native_scale106_shift_m008` → `cat_extra_blend_w15`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### extra_w20

- declared change: ExtraTrees 20% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.2`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_native_scale106_shift_m008` → `cat_extra_blend_w20`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### extra_w24

- declared change: ExtraTrees 24% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.24`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_native_scale106_shift_m008` → `cat_extra_blend_w24`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### extra_w28

- declared change: ExtraTrees 28% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.28`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_native_scale106_shift_m008` → `cat_extra_blend_w28`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### extra_w32

- declared change: ExtraTrees 32% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.32`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_native_scale106_shift_m008` → `cat_extra_blend_w32`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
