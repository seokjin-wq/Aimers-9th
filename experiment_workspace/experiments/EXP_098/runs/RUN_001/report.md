# 098_latest_cpu_capacity: Latest-feature CPU CatBoost capacity sweep

- 가설: The optimal CatBoost depth and boosting duration changed after adding season-state, categorical-hand, and same-hand pitch-mix features.
- control: `depth8_300_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `e5f01222e20a`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| depth8_300_control | control: current depth8 300 trees lr0.035 | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| depth6_800 | depth6, 800 trees, lr0.020 | 0.247523225 | 0.000011358 | 0/1 | 914.187 |
| depth6_600 | depth6, 600 trees, lr0.030 | 0.247536588 | 0.000024721 | 0/1 | 908.838 |
| depth7_400 | depth7, 400 trees, lr0.035 | 0.247542745 | 0.000030878 | 0/1 | 906.373 |
| depth5_600 | depth5, 600 trees, lr0.035 | 0.247569279 | 0.000057413 | 0/1 | 895.751 |

## 실제 변경 필드

- `depth8_300_control`: control
- `depth7_400`: model.name, model.params.depth, model.params.iterations
- `depth6_600`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate
- `depth6_800`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate
- `depth5_600`: model.name, model.params.depth, model.params.iterations

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/098_latest_cpu_capacity/20260818T082256870094Z_e5f01222e20a`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_095`
- 기준 variant: `all_three`
- 검증할 변경: Keep main72 features, season decay 0.85, probability scale/shift, sampling, and seed fixed; compare depth/iteration/learning-rate schedules from depth 5 through 8.

### depth8_300_control

- role: control

### depth7_400

- declared change: depth7, 400 trees, lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_cpu_d7_i400_lr035_decay85`
  - `model.params.depth`: `8` → `7`
  - `model.params.iterations`: `300` → `400`

### depth6_600

- declared change: depth6, 600 trees, lr0.030
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_cpu_d6_i600_lr030_decay85`
  - `model.params.depth`: `8` → `6`
  - `model.params.iterations`: `300` → `600`
  - `model.params.learning_rate`: `0.035` → `0.03`

### depth6_800

- declared change: depth6, 800 trees, lr0.020
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_cpu_d6_i800_lr020_decay85`
  - `model.params.depth`: `8` → `6`
  - `model.params.iterations`: `300` → `800`
  - `model.params.learning_rate`: `0.035` → `0.02`

### depth5_600

- declared change: depth5, 600 trees, lr0.035
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_cpu_d5_i600_lr035_decay85`
  - `model.params.depth`: `8` → `5`
  - `model.params.iterations`: `300` → `600`
