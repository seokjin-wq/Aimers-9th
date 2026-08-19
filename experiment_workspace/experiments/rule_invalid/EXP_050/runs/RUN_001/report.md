# 050_global200_cpu_capacity: global200 CPU CatBoost 용량 탐색

- 가설: global200은 기존과 다른 트리 용량에서 잔여 신호를 더 학습한다
- control: `d6_i400_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `26cdd3d6dd16`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| d6_i600 | depth6 600 lr0.03 | 0.246647686 | -0.000049560 | 1/1 | 1264.673 |
| d7_i400 | depth7 400 lr0.035 | 0.246677982 | -0.000019264 | 1/1 | 1252.545 |
| d8_i300 | depth8 300 lr0.035 | 0.246691924 | -0.000005323 | 1/1 | 1246.964 |
| d6_i400_control | control: depth6 400 lr0.04 | 0.246697246 | 0.000000000 | 0/1 | 1244.834 |
| d5_i600 | depth5 600 lr0.035 | 0.246705183 | 0.000007936 | 0/1 | 1241.657 |
| d6_i800 | depth6 800 lr0.02 | 0.246709007 | 0.000011760 | 0/1 | 1240.126 |

## 실제 변경 필드

- `d6_i400_control`: control
- `d5_i600`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate
- `d6_i600`: model.name, model.params.iterations, model.params.learning_rate
- `d6_i800`: model.name, model.params.iterations, model.params.learning_rate
- `d7_i400`: model.name, model.params.depth, model.params.learning_rate
- `d8_i300`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/050_global200_cpu_capacity/20260817T201230714029Z_26cdd3d6dd16`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_049`
- 기준 variant: `global200_control`
- 검증할 변경: main81 global200과 affine을 고정하고 CPU CatBoost depth5~8, iterations300~800, learning_rate0.02~0.04만 변경

### d6_i400_control

- role: control

### d5_i600

- declared change: depth5 600 lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_cpu_d5_i600_lr035`
  - `model.params.depth`: `6` → `5`
  - `model.params.iterations`: `400` → `600`
  - `model.params.learning_rate`: `0.04` → `0.035`

### d6_i600

- declared change: depth6 600 lr0.03
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_cpu_d6_i600_lr030`
  - `model.params.iterations`: `400` → `600`
  - `model.params.learning_rate`: `0.04` → `0.03`

### d6_i800

- declared change: depth6 800 lr0.02
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_cpu_d6_i800_lr020`
  - `model.params.iterations`: `400` → `800`
  - `model.params.learning_rate`: `0.04` → `0.02`

### d7_i400

- declared change: depth7 400 lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_cpu_d7_i400_lr035`
  - `model.params.depth`: `6` → `7`
  - `model.params.learning_rate`: `0.04` → `0.035`

### d8_i300

- declared change: depth8 300 lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_cpu_d8_i300_lr035`
  - `model.params.depth`: `6` → `8`
  - `model.params.iterations`: `400` → `300`
  - `model.params.learning_rate`: `0.04` → `0.035`
