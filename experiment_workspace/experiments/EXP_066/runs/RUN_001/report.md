# 066_season_state_model_families: 시즌 상태 대체 부스팅 모델

- 가설: 현재 시즌 상태 피처는 CatBoost 외 히스토그램·LightGBM·XGBoost에서 다른 오차 구조를 만들어 앙상블 후보가 될 수 있다
- control: `catboost_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `aaf747e71b25`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| catboost_control | control: EXP_060 CatBoost | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| hist31 | HistGradientBoosting leaf31 | 0.247837945 | 0.000300224 | 0/1 | 788.201 |
| lightgbm31 | LightGBM leaves31 | 0.247896689 | 0.000358968 | 0/1 | 764.686 |
| hist63 | HistGradientBoosting leaf63 | 0.247903860 | 0.000366139 | 0/1 | 761.815 |
| xgboost_d4 | XGBoost depth4 | 0.247974336 | 0.000436616 | 0/1 | 733.603 |
| lightgbm63 | LightGBM leaves63 | 0.248037980 | 0.000500259 | 0/1 | 708.126 |

## 실제 변경 필드

- `catboost_control`: control
- `hist31`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.l2_regularization, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.max_leaf_nodes, model.params.min_samples_leaf, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift, model.season_decay
- `hist63`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.l2_regularization, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.max_leaf_nodes, model.params.min_samples_leaf, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift, model.season_decay
- `lightgbm31`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity, model.prediction_scale, model.prediction_shift, model.season_decay
- `lightgbm63`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity, model.prediction_scale, model.prediction_shift, model.season_decay
- `xgboost_d4`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_weight, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tree_method, model.params.verbose, model.prediction_scale, model.prediction_shift, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/066_season_state_model_families/20260818T033316601249Z_aaf747e71b25`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_062`
- 기준 variant: `extra_w18`
- 검증할 변경: main69 고정 후 CatBoost, HistGradientBoosting, LightGBM, XGBoost 대표 설정 비교

### catboost_control

- role: control

### hist31

- declared change: HistGradientBoosting leaf31
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `hist_gradient_boosting`
  - `model.name`: `catboost_d8_decay085` → `histgb_leaf31`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `8` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.l2_regularization`: `None` → `1.0`
  - `model.params.learning_rate`: `0.035` → `0.05`
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
  - `model.season_decay`: `0.85` → `None`

### hist63

- declared change: HistGradientBoosting leaf63
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `hist_gradient_boosting`
  - `model.name`: `catboost_d8_decay085` → `histgb_leaf63`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `8` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.l2_regularization`: `None` → `1.0`
  - `model.params.learning_rate`: `0.035` → `0.05`
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
  - `model.season_decay`: `0.85` → `None`

### lightgbm31

- declared change: LightGBM leaves31
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_d8_decay085` → `lightgbm_l31`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `8` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.035` → `0.03`
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
  - `model.season_decay`: `0.85` → `None`

### lightgbm63

- declared change: LightGBM leaves63
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_d8_decay085` → `lightgbm_l63`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `8` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.035` → `0.03`
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
  - `model.season_decay`: `0.85` → `None`

### xgboost_d4

- declared change: XGBoost depth4
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `xgboost`
  - `model.name`: `catboost_d8_decay085` → `xgboost_d4`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `8` → `None`
  - `model.params.eval_metric`: `BrierScore` → `logloss`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.035` → `0.03`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_depth`: `None` → `4`
  - `model.params.min_child_weight`: `None` → `50.0`
  - `model.params.n_estimators`: `None` → `600`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.reg_lambda`: `None` → `3.0`
  - `model.params.subsample`: `0.7` → `0.8`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.params.tree_method`: `None` → `hist`
  - `model.params.verbose`: `False` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.season_decay`: `0.85` → `None`
