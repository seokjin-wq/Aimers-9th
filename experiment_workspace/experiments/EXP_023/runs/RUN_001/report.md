# 023_diverse_model_families: 선형·히스토그램·랜덤트리 후보

- 가설: 확률 이력의 매끄러운 선형 효과 또는 다른 tree 구조가 CatBoost와 다른 오차를 만들어 독립 성능이나 앙상블을 개선한다
- control: `catboost_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b251bedf3158`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| catboost_control | control: 현재 최고 CatBoost | 0.247820321 | 0.000000000 | 0/1 | 795.256 |
| extratrees_leaf100 | ExtraTrees min leaf 100 | 0.248006832 | 0.000186511 | 0/1 | 720.594 |
| histgb_leaf31 | HistGradientBoosting 31 leaves | 0.248053439 | 0.000233118 | 0/1 | 701.937 |
| histgb_leaf63 | HistGradientBoosting 63 leaves | 0.248143867 | 0.000323546 | 0/1 | 665.738 |
| extratrees_leaf20 | ExtraTrees min leaf 20 | 0.248214141 | 0.000393820 | 0/1 | 637.607 |
| logistic_c1 | one-hot logistic C=1.0 | 0.248921940 | 0.001101620 | 0/1 | 354.268 |
| logistic_c01 | one-hot logistic C=0.1 | 0.248936028 | 0.001115707 | 0/1 | 348.629 |
| logistic_c001 | one-hot logistic C=0.01 | 0.249025030 | 0.001204709 | 0/1 | 313.000 |

## 실제 변경 필드

- `catboost_control`: control
- `logistic_c001`: model.family, model.name, model.native_categorical, model.params.C, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.random_seed, model.params.random_state, model.params.solver, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tol, model.prediction_scale, model.prediction_shift
- `logistic_c01`: model.family, model.name, model.native_categorical, model.params.C, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.random_seed, model.params.random_state, model.params.solver, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tol, model.prediction_scale, model.prediction_shift
- `logistic_c1`: model.family, model.name, model.native_categorical, model.params.C, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_iter, model.params.random_seed, model.params.random_state, model.params.solver, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.tol, model.prediction_scale, model.prediction_shift
- `histgb_leaf31`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.l2_regularization, model.params.loss_function, model.params.max_iter, model.params.max_leaf_nodes, model.params.min_samples_leaf, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift
- `histgb_leaf63`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.l2_regularization, model.params.loss_function, model.params.max_iter, model.params.max_leaf_nodes, model.params.min_samples_leaf, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift
- `extratrees_leaf20`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_features, model.params.min_samples_leaf, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift
- `extratrees_leaf100`: model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_features, model.params.min_samples_leaf, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/023_diverse_model_families/20260817T172214224590Z_b251bedf3158`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_022`
- 기준 variant: `default_control`
- 검증할 변경: 같은 main60 정보에서 logistic C, HistGradientBoosting leaf 수, ExtraTrees leaf 크기만 비교

### catboost_control

- role: control

### logistic_c001

- declared change: one-hot logistic C=0.01
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `logistic_regression`
  - `model.name`: `catboost_native_scale106_shift_m008` → `logistic_c001`
  - `model.native_categorical`: `True` → `None`
  - `model.params.C`: `None` → `0.01`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `None`
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

### logistic_c01

- declared change: one-hot logistic C=0.1
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `logistic_regression`
  - `model.name`: `catboost_native_scale106_shift_m008` → `logistic_c01`
  - `model.native_categorical`: `True` → `None`
  - `model.params.C`: `None` → `0.1`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `None`
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

### logistic_c1

- declared change: one-hot logistic C=1.0
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `logistic_regression`
  - `model.name`: `catboost_native_scale106_shift_m008` → `logistic_c1`
  - `model.native_categorical`: `True` → `None`
  - `model.params.C`: `None` → `1.0`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `None`
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

### histgb_leaf31

- declared change: HistGradientBoosting 31 leaves
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `hist_gradient_boosting`
  - `model.name`: `catboost_native_scale106_shift_m008` → `histgb_leaf31`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.l2_regularization`: `None` → `1.0`
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

### histgb_leaf63

- declared change: HistGradientBoosting 63 leaves
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `hist_gradient_boosting`
  - `model.name`: `catboost_native_scale106_shift_m008` → `histgb_leaf63`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.l2_regularization`: `None` → `1.0`
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

### extratrees_leaf20

- declared change: ExtraTrees min leaf 20
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `extra_trees`
  - `model.name`: `catboost_native_scale106_shift_m008` → `extratrees_leaf20`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `None`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_features`: `None` → `0.7`
  - `model.params.min_samples_leaf`: `None` → `20`
  - `model.params.n_estimators`: `None` → `300`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`

### extratrees_leaf100

- declared change: ExtraTrees min leaf 100
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `extra_trees`
  - `model.name`: `catboost_native_scale106_shift_m008` → `extratrees_leaf100`
  - `model.native_categorical`: `True` → `None`
  - `model.params.allow_writing_files`: `False` → `None`
  - `model.params.depth`: `6` → `None`
  - `model.params.eval_metric`: `BrierScore` → `None`
  - `model.params.iterations`: `300` → `None`
  - `model.params.l2_leaf_reg`: `3.0` → `None`
  - `model.params.learning_rate`: `0.05` → `None`
  - `model.params.loss_function`: `Logloss` → `None`
  - `model.params.max_features`: `None` → `0.7`
  - `model.params.min_samples_leaf`: `None` → `100`
  - `model.params.n_estimators`: `None` → `300`
  - `model.params.n_jobs`: `None` → `8`
  - `model.params.random_seed`: `42` → `None`
  - `model.params.random_state`: `None` → `42`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `None`
  - `model.params.thread_count`: `8` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `-0.01`
