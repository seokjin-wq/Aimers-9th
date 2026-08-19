# 046_sequence_diverse_boosting: 순차 피처 이종 부스팅 재검증

- 가설: main80의 이종 모델 오차가 CatBoost를 보완한다
- control: `cat_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `0cd4317b64db`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| cat_control | control: CPU CatBoost | 0.246930345 | 0.000000000 | 0/1 | 1151.522 |
| hist63 | HistGradientBoosting leaves63 | 0.247102373 | 0.000172028 | 0/1 | 1082.658 |
| hist31 | HistGradientBoosting leaves31 | 0.247148944 | 0.000218599 | 0/1 | 1064.015 |
| lgb31 | LightGBM leaves31 | 0.247164652 | 0.000234307 | 0/1 | 1057.727 |
| lgb63 | LightGBM leaves63 | 0.247202378 | 0.000272033 | 0/1 | 1042.625 |
| lgb127 | LightGBM leaves127 | 0.247327108 | 0.000396763 | 0/1 | 992.694 |
| logistic | LogisticRegression C0.01 | 0.247921818 | 0.000991473 | 0/1 | 754.626 |

## 실제 변경 필드

- `cat_control`: control
- `lgb31`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity, model.prediction_scale, model.prediction_shift
- `lgb63`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity, model.prediction_scale, model.prediction_shift
- `lgb127`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity, model.prediction_scale, model.prediction_shift
- `hist31`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.l2_regularization, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.max_leaf_nodes, model.params.min_samples_leaf, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift
- `hist63`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.l2_regularization, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.max_leaf_nodes, model.params.min_samples_leaf, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift
- `logistic`: model.family, model.name, model.native_categorical, model.params.C, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.random_seed, model.params.random_state, model.params.solver, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tol, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/046_sequence_diverse_boosting/20260817T194747434407Z_0cd4317b64db`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_045`
- 기준 variant: `best_three`
- 검증할 변경: main80을 고정하고 CPU CatBoost 대비 LightGBM leaves31·63·127, HistGB leaves31·63, Logistic C0.01만 변경

### cat_control

- role: control

### lgb31

- declared change: LightGBM leaves31
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_top_d6_i400_lr040` → `lightgbm_l31`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `400` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.04` → `0.03`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_depth`: `None` → `-1`
  - `model.params.min_child_samples`: `None` → `200`
  - `model.params.n_estimators`: `None` → `500`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.num_leaves`: `None` → `31`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.reg_lambda`: `None` → `3.0`
  - `model.params.subsample`: `0.7` → `0.8`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.params.verbose`: `False` → `None`
  - `model.params.verbosity`: `None` → `-1`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### lgb63

- declared change: LightGBM leaves63
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_top_d6_i400_lr040` → `lightgbm_l63`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `400` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.04` → `0.03`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_depth`: `None` → `-1`
  - `model.params.min_child_samples`: `None` → `200`
  - `model.params.n_estimators`: `None` → `500`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.num_leaves`: `None` → `63`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.reg_lambda`: `None` → `3.0`
  - `model.params.subsample`: `0.7` → `0.8`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.params.verbose`: `False` → `None`
  - `model.params.verbosity`: `None` → `-1`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### lgb127

- declared change: LightGBM leaves127
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_top_d6_i400_lr040` → `lightgbm_l127`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `400` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.04` → `0.03`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_depth`: `None` → `-1`
  - `model.params.min_child_samples`: `None` → `200`
  - `model.params.n_estimators`: `None` → `500`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.num_leaves`: `None` → `127`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.reg_lambda`: `None` → `3.0`
  - `model.params.subsample`: `0.7` → `0.8`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.params.verbose`: `False` → `None`
  - `model.params.verbosity`: `None` → `-1`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### hist31

- declared change: HistGradientBoosting leaves31
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `hist_gradient_boosting`
  - `model.name`: `catboost_top_d6_i400_lr040` → `histgb_leaf31`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `400` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.l2_regularization`: `None` → `1.0`
  - `model.params.learning_rate`: `0.04` → `0.05`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_iter`: `None` → `300`
  - `model.params.max_leaf_nodes`: `None` → `31`
  - `model.params.min_samples_leaf`: `None` → `50`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`

### hist63

- declared change: HistGradientBoosting leaves63
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `hist_gradient_boosting`
  - `model.name`: `catboost_top_d6_i400_lr040` → `histgb_leaf63`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `400` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.l2_regularization`: `None` → `1.0`
  - `model.params.learning_rate`: `0.04` → `0.05`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_iter`: `None` → `300`
  - `model.params.max_leaf_nodes`: `None` → `63`
  - `model.params.min_samples_leaf`: `None` → `50`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`

### logistic

- declared change: LogisticRegression C0.01
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `logistic_regression`
  - `model.name`: `catboost_top_d6_i400_lr040` → `logistic_c01`
  - `model.native_categorical`: `True` → `None`
  - `model.params.C`: `None` → `0.1`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `400` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.04` → `None`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_iter`: `None` → `100`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.solver`: `None` → `lbfgs`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.params.tol`: `None` → `1e-05`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`
