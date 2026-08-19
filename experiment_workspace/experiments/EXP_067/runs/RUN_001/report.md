# 067_2023_residual_catboost: 2023 잔차 CatBoost 보정

- 가설: 2019~2022 모델의 2023 OOT 잔차에서 반복되는 비선형 패턴을 학습하면 2024 예측의 남은 편향을 줄일 수 있다
- control: `base_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `8cad4a6d639d`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| base_control | control: EXP_060 depth8 decay85 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| residual_w025 | 2023 OOT 잔차 예측의 25% 적용 | 0.247725479 | 0.000187758 | 0/1 | 833.223 |
| residual_w050 | 2023 OOT 잔차 예측의 50% 적용 | 0.248449070 | 0.000911349 | 0/1 | 543.562 |
| residual_w075 | 2023 OOT 잔차 예측의 75% 적용 | 0.249708494 | 0.002170773 | 0/1 | 39.404 |
| residual_w100 | 2023 OOT 잔차 예측을 전부 적용 | 0.251503751 | 0.003966030 | 0/1 | 0.000 |

## 실제 변경 필드

- `base_control`: control
- `residual_w025`: model.base_params.allow_writing_files, model.base_params.depth, model.base_params.eval_metric, model.base_params.iterations, model.base_params.l2_leaf_reg, model.base_params.learning_rate, model.base_params.loss_function, model.base_params.random_seed, model.base_params.subsample, model.base_params.task_type, model.base_params.thread_count, model.base_params.verbose, model.base_scale, model.base_season_decay, model.base_shift, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift, model.residual_params.allow_writing_files, model.residual_params.depth, model.residual_params.iterations, model.residual_params.l2_leaf_reg, model.residual_params.learning_rate, model.residual_params.loss_function, model.residual_params.random_seed, model.residual_params.task_type, model.residual_params.thread_count, model.residual_params.verbose, model.residual_weight, model.season_decay
- `residual_w050`: model.base_params.allow_writing_files, model.base_params.depth, model.base_params.eval_metric, model.base_params.iterations, model.base_params.l2_leaf_reg, model.base_params.learning_rate, model.base_params.loss_function, model.base_params.random_seed, model.base_params.subsample, model.base_params.task_type, model.base_params.thread_count, model.base_params.verbose, model.base_scale, model.base_season_decay, model.base_shift, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift, model.residual_params.allow_writing_files, model.residual_params.depth, model.residual_params.iterations, model.residual_params.l2_leaf_reg, model.residual_params.learning_rate, model.residual_params.loss_function, model.residual_params.random_seed, model.residual_params.task_type, model.residual_params.thread_count, model.residual_params.verbose, model.residual_weight, model.season_decay
- `residual_w075`: model.base_params.allow_writing_files, model.base_params.depth, model.base_params.eval_metric, model.base_params.iterations, model.base_params.l2_leaf_reg, model.base_params.learning_rate, model.base_params.loss_function, model.base_params.random_seed, model.base_params.subsample, model.base_params.task_type, model.base_params.thread_count, model.base_params.verbose, model.base_scale, model.base_season_decay, model.base_shift, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift, model.residual_params.allow_writing_files, model.residual_params.depth, model.residual_params.iterations, model.residual_params.l2_leaf_reg, model.residual_params.learning_rate, model.residual_params.loss_function, model.residual_params.random_seed, model.residual_params.task_type, model.residual_params.thread_count, model.residual_params.verbose, model.residual_weight, model.season_decay
- `residual_w100`: model.base_params.allow_writing_files, model.base_params.depth, model.base_params.eval_metric, model.base_params.iterations, model.base_params.l2_leaf_reg, model.base_params.learning_rate, model.base_params.loss_function, model.base_params.random_seed, model.base_params.subsample, model.base_params.task_type, model.base_params.thread_count, model.base_params.verbose, model.base_scale, model.base_season_decay, model.base_shift, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift, model.residual_params.allow_writing_files, model.residual_params.depth, model.residual_params.iterations, model.residual_params.l2_leaf_reg, model.residual_params.learning_rate, model.residual_params.loss_function, model.residual_params.random_seed, model.residual_params.task_type, model.residual_params.thread_count, model.residual_params.verbose, model.residual_weight, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/067_2023_residual_catboost/20260818T033747038423Z_8cad4a6d639d`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_062`
- 기준 variant: `extra_w18`
- 검증할 변경: main69 depth8 decay85 base 고정, 2023 잔차모델 보정 가중치 0.25,0.5,0.75,1.0 비교

### base_control

- role: control

### residual_w025

- declared change: 2023 OOT 잔차 예측의 25% 적용
- added features: none
- removed features: none
- model changes:
  - `model.base_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.base_scale`: `None` → `1.06`
  - `model.base_season_decay`: `None` → `0.85`
  - `model.base_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_residual_correction`
  - `model.name`: `catboost_d8_decay085` → `cat_residual_w025`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.residual_params`: `None` → `{'iterations': 200, 'depth': 4, 'learning_rate': 0.03, 'l2_leaf_reg': 10.0, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'RMSE', 'allow_writing_files': False, 'verbose': False}`
  - `model.residual_weight`: `None` → `0.25`
  - `model.season_decay`: `0.85` → `None`

### residual_w050

- declared change: 2023 OOT 잔차 예측의 50% 적용
- added features: none
- removed features: none
- model changes:
  - `model.base_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.base_scale`: `None` → `1.06`
  - `model.base_season_decay`: `None` → `0.85`
  - `model.base_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_residual_correction`
  - `model.name`: `catboost_d8_decay085` → `cat_residual_w050`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.residual_params`: `None` → `{'iterations': 200, 'depth': 4, 'learning_rate': 0.03, 'l2_leaf_reg': 10.0, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'RMSE', 'allow_writing_files': False, 'verbose': False}`
  - `model.residual_weight`: `None` → `0.5`
  - `model.season_decay`: `0.85` → `None`

### residual_w075

- declared change: 2023 OOT 잔차 예측의 75% 적용
- added features: none
- removed features: none
- model changes:
  - `model.base_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.base_scale`: `None` → `1.06`
  - `model.base_season_decay`: `None` → `0.85`
  - `model.base_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_residual_correction`
  - `model.name`: `catboost_d8_decay085` → `cat_residual_w075`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.residual_params`: `None` → `{'iterations': 200, 'depth': 4, 'learning_rate': 0.03, 'l2_leaf_reg': 10.0, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'RMSE', 'allow_writing_files': False, 'verbose': False}`
  - `model.residual_weight`: `None` → `0.75`
  - `model.season_decay`: `0.85` → `None`

### residual_w100

- declared change: 2023 OOT 잔차 예측을 전부 적용
- added features: none
- removed features: none
- model changes:
  - `model.base_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.base_scale`: `None` → `1.06`
  - `model.base_season_decay`: `None` → `0.85`
  - `model.base_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_residual_correction`
  - `model.name`: `catboost_d8_decay085` → `cat_residual_w100`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.residual_params`: `None` → `{'iterations': 200, 'depth': 4, 'learning_rate': 0.03, 'l2_leaf_reg': 10.0, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'RMSE', 'allow_writing_files': False, 'verbose': False}`
  - `model.residual_weight`: `None` → `1.0`
  - `model.season_decay`: `0.85` → `None`
