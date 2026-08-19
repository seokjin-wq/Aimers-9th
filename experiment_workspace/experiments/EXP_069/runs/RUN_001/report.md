# 069_season_state_gpu_capacity: 시즌 상태 GPU 고용량 CatBoost

- 가설: GPU의 더 많은 border와 450~900 trees가 현재 시즌 상태의 세밀한 비선형 잔차를 CPU depth8보다 잘 포착한다
- control: `cpu_d8`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b24ece403521`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| cpu_d8 | control: CPU depth8 300 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| gpu_d7_i600 | GPU depth7 600 lr0.025 border128 | 0.247539677 | 0.000001956 | 0/1 | 907.601 |
| gpu_d8_i450 | GPU depth8 450 lr0.025 border128 | 0.247569321 | 0.000031600 | 0/1 | 895.734 |
| gpu_d6_i900 | GPU depth6 900 lr0.02 border128 | 0.247590314 | 0.000052593 | 0/1 | 887.330 |

## 실제 변경 필드

- `cpu_d8`: control
- `gpu_d6_i900`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.iterations, model.params.learning_rate, model.params.subsample, model.params.task_type, model.params.thread_count
- `gpu_d7_i600`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.iterations, model.params.learning_rate, model.params.subsample, model.params.task_type, model.params.thread_count
- `gpu_d8_i450`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.devices, model.params.iterations, model.params.learning_rate, model.params.subsample, model.params.task_type, model.params.thread_count

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/069_season_state_gpu_capacity/20260818T034704624852Z_b24ece403521`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_062`
- 기준 variant: `extra_w18`
- 검증할 변경: main69와 decay0.85 고정, CPU d8-300 대비 GPU d6-900, d7-600, d8-450 비교

### cpu_d8

- role: control

### gpu_d6_i900

- declared change: GPU depth6 900 lr0.02 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_gpu_d6_i900_decay85`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.depth`: `8` → `6`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `300` → `900`
  - `model.params.learning_rate`: `0.035` → `0.02`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`

### gpu_d7_i600

- declared change: GPU depth7 600 lr0.025 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_gpu_d7_i600_decay85`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.depth`: `8` → `7`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `300` → `600`
  - `model.params.learning_rate`: `0.035` → `0.025`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`

### gpu_d8_i450

- declared change: GPU depth8 450 lr0.025 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_gpu_d8_i450_decay85`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `300` → `450`
  - `model.params.learning_rate`: `0.035` → `0.025`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`
