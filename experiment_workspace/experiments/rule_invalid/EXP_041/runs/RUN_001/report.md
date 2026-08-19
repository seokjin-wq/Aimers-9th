# 041_catboost_generalization: 순차 피처 CatBoost 일반화 설정

- 가설: 시간 순서와 랜덤성 조정이 순차 피처 학습을 안정화한다
- control: `default_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `2cf4b79b6e47`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| bag0 | bagging_temperature 0 | 0.246866253 | -0.000034514 | 1/1 | 1177.179 |
| default_control | control: 기본 랜덤성 | 0.246900767 | 0.000000000 | 0/1 | 1163.363 |
| random2 | random_strength 2 | 0.246928968 | 0.000028201 | 0/1 | 1152.073 |
| random02 | random_strength 0.2 | 0.246929522 | 0.000028756 | 0/1 | 1151.851 |
| random0 | random_strength 0 | 0.246931442 | 0.000030676 | 0/1 | 1151.083 |
| has_time | 입력 시간 순서 보존 | 0.246939840 | 0.000039073 | 0/1 | 1147.721 |

## 실제 변경 필드

- `default_control`: control
- `has_time`: model.name, model.params.has_time
- `random0`: model.name, model.params.random_strength
- `random02`: model.name, model.params.random_strength
- `random2`: model.name, model.params.random_strength
- `bag0`: model.name, model.params.bagging_temperature

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/041_catboost_generalization/20260817T191142151900Z_2cf4b79b6e47`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_040`
- 기준 variant: `cat_single_control`
- 검증할 변경: main85와 depth6 900 lr0.020을 고정하고 has_time, random_strength 0·0.2·2, bagging_temperature 0만 개별 변경

### default_control

- role: control

### has_time

- declared change: 입력 시간 순서 보존
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `catboost_gpu_d6_i900_has_time`
  - `model.params.has_time`: `None` → `True`

### random0

- declared change: random_strength 0
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `catboost_gpu_d6_i900_random0`
  - `model.params.random_strength`: `None` → `0.0`

### random02

- declared change: random_strength 0.2
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `catboost_gpu_d6_i900_random02`
  - `model.params.random_strength`: `None` → `0.2`

### random2

- declared change: random_strength 2
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `catboost_gpu_d6_i900_random2`
  - `model.params.random_strength`: `None` → `2.0`

### bag0

- declared change: bagging_temperature 0
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i900_lr020_b128` → `catboost_gpu_d6_i900_bag0`
  - `model.params.bagging_temperature`: `1.0` → `0.0`
