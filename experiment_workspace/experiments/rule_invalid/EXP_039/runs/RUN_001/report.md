# 039_sequence_capacity: 순차 피처 CatBoost 용량 재탐색

- 가설: main85는 기존 모델보다 다른 깊이·학습 길이가 적합하다
- control: `d6_i600_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `80437725bcd9`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| d6_i900 | depth6 900 lr0.020 | 0.246899902 | -0.000030959 | 1/1 | 1163.709 |
| d7_i600 | depth7 600 lr0.025 | 0.246900546 | -0.000030315 | 1/1 | 1163.451 |
| d8_i450 | depth8 450 lr0.025 | 0.246906824 | -0.000024037 | 1/1 | 1160.938 |
| d6_i600_control | control: depth6 600 lr0.025 | 0.246930861 | 0.000000000 | 0/1 | 1151.315 |
| d5_i800 | depth5 800 lr0.025 | 0.246948590 | 0.000017729 | 0/1 | 1144.218 |

## 실제 변경 필드

- `d6_i600_control`: control
- `d5_i800`: model.name, model.params.depth, model.params.iterations
- `d6_i900`: model.name, model.params.iterations, model.params.learning_rate
- `d7_i600`: model.name, model.params.depth
- `d8_i450`: model.name, model.params.depth, model.params.iterations

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/039_sequence_capacity/20260817T184643509818Z_80437725bcd9`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_038`
- 기준 variant: `plate_context`
- 검증할 변경: main85와 affine 보정을 고정하고 GPU CatBoost depth 5~8, iterations 450~900, learning_rate 경로만 변경

### d6_i600_control

- role: control

### d5_i800

- declared change: depth5 800 lr0.025
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catboost_gpu_d5_i800_lr025_b128`
  - `model.params.depth`: `6` → `5`
  - `model.params.iterations`: `600` → `800`

### d6_i900

- declared change: depth6 900 lr0.020
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catboost_gpu_d6_i900_lr020_b128`
  - `model.params.iterations`: `600` → `900`
  - `model.params.learning_rate`: `0.025` → `0.02`

### d7_i600

- declared change: depth7 600 lr0.025
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catboost_gpu_d7_i600_lr025_b128`
  - `model.params.depth`: `6` → `7`

### d8_i450

- declared change: depth8 450 lr0.025
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catboost_gpu_d8_i450_lr025_b128`
  - `model.params.depth`: `6` → `8`
  - `model.params.iterations`: `600` → `450`
