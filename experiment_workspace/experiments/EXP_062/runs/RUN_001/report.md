# 062_d8_decay_cat_extra_blend: depth8 최근성 CatBoost 이종 앙상블

- 가설: EXP_060의 최근성 depth8 CatBoost와 ExtraTrees를 혼합하면 새 최고 구성의 편향과 분산을 동시에 낮춘다
- control: `cat_d8_decay85`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `ebf887277ebd`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| extra_w18 | ExtraTrees 18% 혼합 | 0.247515025 | -0.000022696 | 1/1 | 917.469 |
| extra_w24 | ExtraTrees 24% 혼합 | 0.247516338 | -0.000021382 | 1/1 | 916.944 |
| extra_w30 | ExtraTrees 30% 혼합 | 0.247522091 | -0.000015630 | 1/1 | 914.641 |
| cat_d8_decay85 | control: EXP_060 최고 CatBoost | 0.247537721 | 0.000000000 | 0/1 | 908.384 |

## 실제 변경 필드

- `cat_d8_decay85`: control
- `extra_w18`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_season_decay, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift, model.season_decay
- `extra_w24`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_season_decay, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift, model.season_decay
- `extra_w30`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_season_decay, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/062_d8_decay_cat_extra_blend/20260818T030728526324Z_ebf887277ebd`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_060`
- 기준 variant: `decay085`
- 검증할 변경: main69 고정, depth8 decay0.85 CatBoost 단독 대비 ExtraTrees 18,24,30% 혼합

### cat_d8_decay85

- role: control

### extra_w18

- declared change: ExtraTrees 18% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_season_decay`: `None` → `0.85`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.18`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_d8_decay085` → `cat_extra_d8_decay85_w18`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.season_decay`: `0.85` → `None`

### extra_w24

- declared change: ExtraTrees 24% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_season_decay`: `None` → `0.85`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.24`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_d8_decay085` → `cat_extra_d8_decay85_w24`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.season_decay`: `0.85` → `None`

### extra_w30

- declared change: ExtraTrees 30% 혼합
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_season_decay`: `None` → `0.85`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.extra_params`: `None` → `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}`
  - `model.extra_shift`: `None` → `-0.01`
  - `model.extra_weight`: `None` → `0.3`
  - `model.family`: `catboost` → `cat_extra_blend`
  - `model.name`: `catboost_d8_decay085` → `cat_extra_d8_decay85_w30`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 300, 'depth': 8, 'learning_rate': 0.035, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
  - `model.season_decay`: `0.85` → `None`
