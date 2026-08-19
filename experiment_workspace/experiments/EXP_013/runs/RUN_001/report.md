# 013_direct_brier_objective: Brier 직접 최적화 회귀 부스팅

- 가설: 0/1 타깃을 제곱오차로 직접 학습하는 회귀 부스팅이 Logloss 분류보다 2024 Brier를 개선한다
- control: `catboost_logloss_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `6e44aa17ddb8`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| catboost_logloss_control | control: CatBoost Logloss classifier | 0.247968140 | 0.000000000 | 0/1 | 736.083 |
| catboost_rmse_500 | CatBoost RMSE regressor 500 trees | 0.248016262 | 0.000048122 | 0/1 | 716.819 |
| catboost_rmse_300 | CatBoost RMSE regressor 300 trees | 0.248043155 | 0.000075015 | 0/1 | 706.054 |
| lightgbm_rmse | LightGBM regression_l2 | 0.248117964 | 0.000149824 | 0/1 | 676.107 |
| xgboost_rmse | XGBoost squared-error | 0.248181673 | 0.000213533 | 0/1 | 650.604 |

## 실제 변경 필드

- `catboost_logloss_control`: control
- `catboost_rmse_300`: model.family, model.name, model.params.eval_metric, model.params.loss_function
- `catboost_rmse_500`: model.family, model.name, model.params.eval_metric, model.params.iterations, model.params.learning_rate, model.params.loss_function
- `lightgbm_rmse`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.min_child_samples, model.params.n_estimators, model.params.n_jobs, model.params.num_leaves, model.params.objective, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.params.verbosity
- `xgboost_rmse`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.colsample_bytree, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_child_weight, model.params.n_estimators, model.params.n_jobs, model.params.objective, model.params.random_seed, model.params.random_state, model.params.reg_lambda, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tree_method, model.params.verbose

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/013_direct_brier_objective/20260817T162312542438Z_6e44aa17ddb8`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_012`
- 기준 variant: `default_control`
- 검증할 변경: main55+count를 고정하고 CatBoost/LightGBM/XGBoost의 분류 Logloss와 회귀 squared-error 목적을 비교

### catboost_logloss_control

- role: control

### catboost_rmse_300

- declared change: CatBoost RMSE regressor 300 trees
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_regressor`
  - `model.name`: `catboost_native_300` → `catboost_rmse_300`
  - `model.params.eval_metric`: `BrierScore` → `RMSE`
  - `model.params.loss_function`: `Logloss` → `RMSE`

### catboost_rmse_500

- declared change: CatBoost RMSE regressor 500 trees
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_regressor`
  - `model.name`: `catboost_native_300` → `catboost_rmse_500`
  - `model.params.eval_metric`: `BrierScore` → `RMSE`
  - `model.params.iterations`: `300` → `500`
  - `model.params.learning_rate`: `0.05` → `0.03`
  - `model.params.loss_function`: `Logloss` → `RMSE`

### lightgbm_rmse

- declared change: LightGBM regression_l2
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `lightgbm_regressor`
  - `model.name`: `catboost_native_300` → `lightgbm_rmse_l31`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `0.03`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.min_child_samples`: `None` → `200`
  - `model.params.n_estimators`: `None` → `500`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.num_leaves`: `None` → `31`
  - `model.params.objective`: `None` → `regression_l2`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.reg_lambda`: `None` → `3.0`
  - `model.params.subsample`: `0.7` → `0.8`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.params.verbose`: `False` → `None`
  - `model.params.verbosity`: `None` → `-1`

### xgboost_rmse

- declared change: XGBoost squared-error
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `xgboost_regressor`
  - `model.name`: `catboost_native_300` → `xgboost_rmse_d4`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.colsample_bytree`: `None` → `0.8`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `0.03`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_depth`: `None` → `4`
  - `model.params.min_child_weight`: `None` → `50.0`
  - `model.params.n_estimators`: `None` → `600`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.objective`: `None` → `reg:squarederror`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.reg_lambda`: `None` → `3.0`
  - `model.params.subsample`: `0.7` → `0.8`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.params.tree_method`: `None` → `hist`
  - `model.params.verbose`: `False` → `None`
