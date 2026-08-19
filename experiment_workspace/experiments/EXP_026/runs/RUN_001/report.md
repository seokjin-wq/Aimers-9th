# 026_prior_season_group_residual: 직전 시즌 그룹 잔차 보정

- 가설: 2023에서 반복된 선수·팀·상황별 예측 편향이 2024에도 유지되어 직전 시즌 잔차 보정이 Brier를 개선한다
- control: `catboost_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `c3ddefd74140`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_k500 | ball-strike-out 조합 잔차 | 0.247818070 | -0.000000958 | 1/1 | 796.158 |
| catboost_control | control: depth6 400 lr0.04, 그룹 보정 없음 | 0.247819028 | 0.000000000 | 0/1 | 795.774 |
| month_k1000 | game_month 잔차 | 0.248042462 | 0.000223434 | 0/1 | 706.331 |
| pitcher_team_k200 | pitcher_team_id 잔차 | 0.248158995 | 0.000339967 | 0/1 | 659.682 |
| batter_team_k200 | batter_team_id 잔차 | 0.248165647 | 0.000346619 | 0/1 | 657.019 |
| pitcher_bteam_k200 | pitcher_id × batter_team_id 잔차 | 0.248332952 | 0.000513924 | 0/1 | 590.045 |
| pitcher_k500 | pitcher_id 잔차, shrinkage 500 | 0.248544710 | 0.000725682 | 0/1 | 505.277 |
| pitcher_k200 | pitcher_id 잔차, shrinkage 200 | 0.249185837 | 0.001366809 | 0/1 | 248.628 |
| batter_k200 | batter_id 잔차, shrinkage 200 | 0.249262464 | 0.001443436 | 0/1 | 217.953 |
| pitcher_k50 | pitcher_id 잔차, shrinkage 50 | 0.250291566 | 0.002472538 | 0/1 | 0.000 |
| batter_k50 | batter_id 잔차, shrinkage 50 | 0.250504680 | 0.002685652 | 0/1 | 0.000 |

## 실제 변경 필드

- `catboost_control`: control
- `pitcher_k50`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `pitcher_k200`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `pitcher_k500`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `batter_k50`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `batter_k200`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `pitcher_team_k200`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `batter_team_k200`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `count_k500`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `month_k1000`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift
- `pitcher_bteam_k200`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.family, model.group_columns, model.group_shrinkage, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/026_prior_season_group_residual/20260817T174851246517Z_c3ddefd74140`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_025`
- 기준 variant: `d6_i400_lr040`
- 검증할 변경: 2019~2022→2023 OOF 잔차만 사용해 pitcher, batter, team, count별 shrinkage offset을 학습하고 2019~2023→2024 예측에 적용

### catboost_control

- role: control

### pitcher_k50

- declared change: pitcher_id 잔차, shrinkage 50
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['pitcher_id']`
  - `model.group_shrinkage`: `None` → `50.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_pitcher_k50`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### pitcher_k200

- declared change: pitcher_id 잔차, shrinkage 200
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['pitcher_id']`
  - `model.group_shrinkage`: `None` → `200.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_pitcher_k200`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### pitcher_k500

- declared change: pitcher_id 잔차, shrinkage 500
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['pitcher_id']`
  - `model.group_shrinkage`: `None` → `500.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_pitcher_k500`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### batter_k50

- declared change: batter_id 잔차, shrinkage 50
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['batter_id']`
  - `model.group_shrinkage`: `None` → `50.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_batter_k50`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### batter_k200

- declared change: batter_id 잔차, shrinkage 200
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['batter_id']`
  - `model.group_shrinkage`: `None` → `200.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_batter_k200`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### pitcher_team_k200

- declared change: pitcher_team_id 잔차
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['pitcher_team_id']`
  - `model.group_shrinkage`: `None` → `200.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_pitcher_team_k200`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### batter_team_k200

- declared change: batter_team_id 잔차
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['batter_team_id']`
  - `model.group_shrinkage`: `None` → `200.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_batter_team_k200`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### count_k500

- declared change: ball-strike-out 조합 잔차
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['balls_before', 'strikes_before', 'outs_before']`
  - `model.group_shrinkage`: `None` → `500.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_count_k500`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### month_k1000

- declared change: game_month 잔차
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['game_month']`
  - `model.group_shrinkage`: `None` → `1000.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_month_k1000`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### pitcher_bteam_k200

- declared change: pitcher_id × batter_team_id 잔차
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `None` → `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.cat_scale`: `None` → `1.06`
  - `model.cat_shift`: `None` → `-0.008`
  - `model.family`: `catboost` → `catboost_group_calibrated`
  - `model.group_columns`: `None` → `['pitcher_id', 'batter_team_id']`
  - `model.group_shrinkage`: `None` → `200.0`
  - `model.name`: `catboost_top_d6_i400_lr040` → `groupcal_pitcher_bteam_k200`
  - `model.native_categorical`: `True` → `None`
  - `model.params`: `{'iterations': 400, 'depth': 6, 'learning_rate': 0.04, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
