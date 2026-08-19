# 059_season_state_catboost_capacity: 시즌 상태 CatBoost 용량 재탐색

- 가설: 새로운 현재 시즌 상태 신호는 기존 main60과 다른 최적 트리 깊이·반복 수를 가질 수 있다
- control: `d6_i300_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `2ba4c4563ad7`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| d8_i300 | depth8 300 lr0.035 | 0.247567748 | -0.000031520 | 1/1 | 896.364 |
| d6_i600 | depth6 600 lr0.025 | 0.247583950 | -0.000015318 | 1/1 | 889.878 |
| d6_i300_control | control: depth6 300 lr0.05 | 0.247599268 | 0.000000000 | 0/1 | 883.746 |
| d7_i400 | depth7 400 lr0.035 | 0.247599535 | 0.000000267 | 0/1 | 883.639 |
| d5_i600 | depth5 600 lr0.035 | 0.247607890 | 0.000008622 | 0/1 | 880.295 |
| d6_i400 | depth6 400 lr0.04 | 0.247613314 | 0.000014046 | 0/1 | 878.123 |

## 실제 변경 필드

- `d6_i300_control`: control
- `d6_i400`: model.name, model.params.iterations, model.params.learning_rate
- `d6_i600`: model.name, model.params.iterations, model.params.learning_rate
- `d5_i600`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate
- `d7_i400`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate
- `d8_i300`: model.name, model.params.depth, model.params.learning_rate

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/059_season_state_catboost_capacity/20260818T024859670939Z_2ba4c4563ad7`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_057`
- 기준 variant: `extra_w24`
- 검증할 변경: main69 고정 후 depth5~8, 300~600 trees의 기존 결정론적 CPU 후보만 재비교

### d6_i300_control

- role: control

### d6_i400

- declared change: depth6 400 lr0.04
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i400_lr040`
  - `model.params.iterations`: `300` → `400`
  - `model.params.learning_rate`: `0.05` → `0.04`

### d6_i600

- declared change: depth6 600 lr0.025
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_top_d6_i600_lr025`
  - `model.params.iterations`: `300` → `600`
  - `model.params.learning_rate`: `0.05` → `0.025`

### d5_i600

- declared change: depth5 600 lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_cpu_d5_i600_lr035`
  - `model.params.depth`: `6` → `5`
  - `model.params.iterations`: `300` → `600`
  - `model.params.learning_rate`: `0.05` → `0.035`

### d7_i400

- declared change: depth7 400 lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_cpu_d7_i400_lr035`
  - `model.params.depth`: `6` → `7`
  - `model.params.iterations`: `300` → `400`
  - `model.params.learning_rate`: `0.05` → `0.035`

### d8_i300

- declared change: depth8 300 lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_scale106_shift_m008` → `catboost_cpu_d8_i300_lr035`
  - `model.params.depth`: `6` → `8`
  - `model.params.learning_rate`: `0.05` → `0.035`
