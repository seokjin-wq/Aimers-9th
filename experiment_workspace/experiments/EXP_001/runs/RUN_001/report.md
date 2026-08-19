# 001_model_family: 동일한 제공 47개 피처에서 모델군만 비교

- 가설: CatBoost가 RandomForest보다 2024 고정 홀드아웃 Brier를 개선한다.
- control: `random_forest_raw47`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `d951333c26e6`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| catboost_raw47 | 모델군만 RandomForest에서 CatBoost로 변경 | 0.248072725 | -0.000696070 | 1/1 | 694.217 |
| random_forest_raw47 | control: 제공 RandomForest 계열 기준 | 0.248768795 | 0.000000000 | 0/1 | 415.574 |

## 실제 변경 필드

- `random_forest_raw47`: control
- `catboost_raw47`: model.family, model.name, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.max_depth, model.params.min_samples_leaf, model.params.n_estimators, model.params.n_jobs, model.params.random_seed, model.params.random_state, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/001_model_family/20260817T144355696321Z_d951333c26e6`

## 실험 계보와 정확한 ablation

- 비교 기준: `BASELINE_001_main55`
- 기준 variant: `random_forest_raw47`
- 검증할 변경: 제공 raw47을 고정하고 RandomForest 대비 CatBoost 모델군 변경 효과를 검증

### random_forest_raw47

- role: control

### catboost_raw47

- declared change: 모델군만 RandomForest에서 CatBoost로 변경
- added features: none
- removed features: none
- model changes:
  - `model.family`: `random_forest` → `catboost`
  - `model.name`: `random_forest_default` → `catboost_default`
  - `model.params.allow_writing_files`: `None` → `False`
  - `model.params.depth`: `None` → `6`
  - `model.params.eval_metric`: `None` → `BrierScore`
  - `model.params.iterations`: `None` → `300`
  - `model.params.l2_leaf_reg`: `None` → `3.0`
  - `model.params.learning_rate`: `None` → `0.05`
  - `model.params.loss_function`: `None` → `Logloss`
  - `model.params.max_depth`: `10` → `None`
  - `model.params.min_samples_leaf`: `200` → `None`
  - `model.params.n_estimators`: `100` → `None`
  - `model.params.n_jobs`: `8` → `None`
  - `model.params.random_seed`: `None` → `42`
  - `model.params.random_state`: `42` → `None`
  - `model.params.subsample`: `None` → `0.7`
  - `model.params.task_type`: `None` → `CPU`
  - `model.params.thread_count`: `None` → `8`
  - `model.params.verbose`: `None` → `False`
