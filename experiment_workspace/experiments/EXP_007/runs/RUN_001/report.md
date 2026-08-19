# 007_boosting_family: 부스팅 모델군 비교

- 가설: LightGBM 또는 XGBoost가 현재 CatBoost보다 2024 Brier를 크게 개선한다
- control: `catboost_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `c3d0b2afa616`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| catboost_control | control: native CatBoost depth6 300 trees | 0.248009268 | 0.000000000 | 0/1 | 719.619 |
| lightgbm_l31 | LightGBM 31 leaves | 0.248115102 | 0.000105834 | 0/1 | 677.253 |
| xgboost_d4 | XGBoost depth4 | 0.248179828 | 0.000170560 | 0/1 | 651.343 |
| lightgbm_l63 | LightGBM 63 leaves | 0.248197367 | 0.000188100 | 0/1 | 644.321 |
| lightgbm_l127 | LightGBM 127 leaves | 0.248243272 | 0.000234004 | 0/1 | 625.945 |
| xgboost_d6 | XGBoost depth6 | 0.248253672 | 0.000244405 | 0/1 | 621.782 |

## 실제 변경 필드

- `catboost_control`: control
- `lightgbm_l31`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity
- `lightgbm_l63`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity
- `lightgbm_l127`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity
- `xgboost_d4`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_weight, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tree_method, model.params.verbose
- `xgboost_d6`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_weight, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tree_method, model.params.verbose

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/007_boosting_family/20260817T155457807603Z_c3d0b2afa616`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_006`
- 기준 variant: `d6_i300_control`
- 검증할 변경: main55를 고정하고 CatBoost, LightGBM, XGBoost 모델군과 대표 복잡도만 비교

### catboost_control

- role: control

### lightgbm_l31

- declared change: LightGBM 31 leaves
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_native_300` → `lightgbm_l31`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `0.03`
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

### lightgbm_l63

- declared change: LightGBM 63 leaves
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_native_300` → `lightgbm_l63`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `0.03`
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

### lightgbm_l127

- declared change: LightGBM 127 leaves
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm`
  - `model.name`: `catboost_native_300` → `lightgbm_l127`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `0.03`
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

### xgboost_d4

- declared change: XGBoost depth4
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `xgboost`
  - `model.name`: `catboost_native_300` → `xgboost_d4`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `logloss`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `0.03`
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

### xgboost_d6

- declared change: XGBoost depth6
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `xgboost`
  - `model.name`: `catboost_native_300` → `xgboost_d6`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `logloss`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `0.03`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_depth`: `None` → `6`
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
