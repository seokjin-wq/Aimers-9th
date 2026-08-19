# 025_catboost_learning_path: CatBoost 학습률-트리수 경로

- 가설: 총 boosting 강도를 비슷하게 유지하면서 작은 학습률과 많은 tree를 쓰면 기존 300x0.05보다 일반화 Brier가 개선된다
- control: `d6_i300_lr050_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `660d2bdf9b48`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| d6_i400_lr040 | depth6, 400, lr0.04 | 0.247819028 | -0.000001293 | 1/1 | 795.774 |
| d6_i300_lr050_control | control: depth6, 300, lr0.05 | 0.247820321 | 0.000000000 | 0/1 | 795.256 |
| d6_i600_lr025 | depth6, 600, lr0.025 | 0.247822360 | 0.000002039 | 0/1 | 794.440 |
| d7_i250_lr050 | depth7, 250, lr0.05 | 0.247840634 | 0.000020313 | 0/1 | 787.125 |
| d8_i200_lr050 | depth8, 200, lr0.05 | 0.247841458 | 0.000021137 | 0/1 | 786.795 |
| d6_i450_lr033 | depth6, 450, lr0.033 | 0.247848088 | 0.000027768 | 0/1 | 784.141 |
| d6_i250_lr060 | depth6, 250, lr0.06 | 0.247872211 | 0.000051890 | 0/1 | 774.484 |
| d6_i200_lr075 | depth6, 200, lr0.075 | 0.247885086 | 0.000064765 | 0/1 | 769.330 |
| d6_i150_lr100 | depth6, 150, lr0.10 | 0.247901399 | 0.000081078 | 0/1 | 762.800 |

## 실제 변경 필드

- `d6_i300_lr050_control`: control
- `d6_i600_lr025`: model.name, model.params.iterations, model.params.learning_rate
- `d6_i450_lr033`: model.name, model.params.iterations, model.params.learning_rate
- `d6_i400_lr040`: model.name, model.params.iterations, model.params.learning_rate
- `d6_i250_lr060`: model.name, model.params.iterations, model.params.learning_rate
- `d6_i200_lr075`: model.name, model.params.iterations, model.params.learning_rate
- `d6_i150_lr100`: model.name, model.params.iterations, model.params.learning_rate
- `d7_i250_lr050`: model.name, model.params.depth, model.params.iterations
- `d8_i200_lr050`: model.name, model.params.depth, model.params.iterations

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/025_catboost_learning_path/20260817T174132318399Z_660d2bdf9b48`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_024`
- 기준 variant: `extra_w24`
- 검증할 변경: main60과 categorical/affine을 고정하고 iterations와 learning_rate 조합 및 인접 depth만 변경

### d6_i300_lr050_control

- role: control

### d6_i600_lr025

- declared change: depth6, 600, lr0.025
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i600_lr025`
  - `model.params.iterations`: `300` → `600`
  - `model.params.learning_rate`: `0.05` → `0.025`

### d6_i450_lr033

- declared change: depth6, 450, lr0.033
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i450_lr033`
  - `model.params.iterations`: `300` → `450`
  - `model.params.learning_rate`: `0.05` → `0.033`

### d6_i400_lr040

- declared change: depth6, 400, lr0.04
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i400_lr040`
  - `model.params.iterations`: `300` → `400`
  - `model.params.learning_rate`: `0.05` → `0.04`

### d6_i250_lr060

- declared change: depth6, 250, lr0.06
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i250_lr060`
  - `model.params.iterations`: `300` → `250`
  - `model.params.learning_rate`: `0.05` → `0.06`

### d6_i200_lr075

- declared change: depth6, 200, lr0.075
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i200_lr075`
  - `model.params.iterations`: `300` → `200`
  - `model.params.learning_rate`: `0.05` → `0.075`

### d6_i150_lr100

- declared change: depth6, 150, lr0.10
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i150_lr100`
  - `model.params.iterations`: `300` → `150`
  - `model.params.learning_rate`: `0.05` → `0.1`

### d7_i250_lr050

- declared change: depth7, 250, lr0.05
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d7_i250_lr050`
  - `model.params.depth`: `6` → `7`
  - `model.params.iterations`: `300` → `250`

### d8_i200_lr050

- declared change: depth8, 200, lr0.05
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d8_i200_lr050`
  - `model.params.depth`: `6` → `8`
  - `model.params.iterations`: `300` → `200`
