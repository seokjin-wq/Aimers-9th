# 024_cat_extra_blend: CatBoost ExtraTrees 이종 앙상블

- 가설: 상관이 낮은 ExtraTrees를 15~35% 혼합하면 CatBoost 단독보다 Brier가 개선된다
- control: `catboost_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a3e1bad91fef`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| extra_w24 | ExtraTrees 24% 혼합 | 0.247777594 | -0.000042727 | 1/1 | 812.360 |
| extra_w20 | ExtraTrees 20% 혼합 | 0.247778696 | -0.000041625 | 1/1 | 811.919 |
| extra_w28 | ExtraTrees 28% 혼합 | 0.247778900 | -0.000041421 | 1/1 | 811.838 |
| extra_w32 | ExtraTrees 32% 혼합 | 0.247782614 | -0.000037707 | 1/1 | 810.351 |
| extra_w15 | ExtraTrees 15% 혼합 | 0.247783459 | -0.000036862 | 1/1 | 810.013 |
| extra_w36 | ExtraTrees 36% 혼합 | 0.247788736 | -0.000031585 | 1/1 | 807.900 |
| catboost_control | control: 현재 최고 CatBoost | 0.247820321 | 0.000000000 | 0/1 | 795.256 |

## 실제 변경 필드

- `catboost_control`: control
- `extra_w15`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w20`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w24`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w28`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w32`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `extra_w36`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/024_cat_extra_blend/20260817T173452243512Z_a3e1bad91fef`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_023`
- 기준 variant: `catboost_control`
- 검증할 변경: 동일 main60에서 CatBoost와 ExtraTrees leaf20을 함께 학습하고 ExtraTrees 가중치 0.15~0.35만 변경

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

### extra_w36

- declared change: ExtraTrees 36% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.36`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_native_scale106_shift_m008` → `cat_extra_blend_w36`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
