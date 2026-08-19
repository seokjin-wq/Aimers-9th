# 054_rule_compliant_baseline_replay: 규칙 준수 베이스라인 재현

- 가설: 평가 행간 연산을 차단한 안전 피처 경로에서도 EXP_024 ExtraTrees 24% 혼합 점수가 동일하게 재현된다
- control: `extra_w24_safe`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `9ccc2e13b988`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| extra_w24_safe | control: EXP_024 extra_w24를 규칙 준수 row-local 엔진에서 재현 | 0.247777594 | 0.000000000 | 0/1 | 812.360 |

## 실제 변경 필드

- `extra_w24_safe`: control
- `catboost_only`: model.cat_params.allow_writing_files, model.cat_params.depth, model.cat_params.eval_metric, model.cat_params.iterations, model.cat_params.l2_leaf_reg, model.cat_params.learning_rate, model.cat_params.loss_function, model.cat_params.random_seed, model.cat_params.subsample, model.cat_params.task_type, model.cat_params.thread_count, model.cat_params.verbose, model.cat_scale, model.cat_shift, model.extra_params.max_features, model.extra_params.min_samples_leaf, model.extra_params.n_estimators, model.extra_params.n_jobs, model.extra_params.random_state, model.extra_params.verbose, model.extra_shift, model.extra_weight, model.family, model.name, model.native_categorical, model.params.allow_writing_files, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.l2_leaf_reg, model.params.learning_rate, model.params.loss_function, model.params.random_seed, model.params.subsample, model.params.task_type, model.params.thread_count, model.params.verbose, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/054_rule_compliant_baseline_replay/20260818T021221943888Z_9ccc2e13b988`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_024`
- 기준 variant: `extra_w24`
- 검증할 변경: EXP_024 extra_w24를 규칙 준수 엔진에서 재실행하고 CatBoost 단독과 설정 차이를 보존

### extra_w24_safe

- role: control

### catboost_only

- declared change: ExtraTrees 혼합만 제거한 CatBoost 단독 비교
- added features: none
- removed features: none
- model changes:
  - `model.cat_params`: `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}` → `None`
  - `model.cat_scale`: `1.06` → `None`
  - `model.cat_shift`: `-0.008` → `None`
  - `model.extra_params`: `{'n_estimators': 300, 'min_samples_leaf': 20, 'max_features': 0.7, 'n_jobs': 8, 'random_state': 42, 'verbose': 0}` → `None`
  - `model.extra_shift`: `-0.01` → `None`
  - `model.extra_weight`: `0.24` → `None`
  - `model.family`: `cat_extra_blend` → `catboost`
  - `model.name`: `cat_extra_blend_w24` → `catboost_native_scale106_shift_m008`
  - `model.native_categorical`: `None` → `True`
  - `model.params`: `None` → `{'iterations': 300, 'depth': 6, 'learning_rate': 0.05, 'l2_leaf_reg': 3.0, 'subsample': 0.7, 'random_seed': 42, 'thread_count': 8, 'task_type': 'CPU', 'loss_function': 'Logloss', 'eval_metric': 'BrierScore', 'allow_writing_files': False, 'verbose': False}`
  - `model.prediction_scale`: `None` → `1.06`
  - `model.prediction_shift`: `None` → `-0.008`
