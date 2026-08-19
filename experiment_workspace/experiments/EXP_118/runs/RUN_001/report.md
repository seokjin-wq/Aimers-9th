# 118_reliability_capacity_refresh: Reliability-feature CatBoost capacity refresh

- 가설: Adding six reliability features changes model complexity needs; a deeper or longer schedule may capture the new interactions better than the old depth8/300 setting.
- control: `d8_i300_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `29b3fc0f7105`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| d8_i300_control | control: reliability CPU depth8, 300 trees, lr0.035 | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| d8_i450_lr025 | depth8/300/lr.035 -> depth8/450/lr.025 schedule | 0.247504197 | 0.000016204 | 0/1 | 921.804 |
| d9_i220_lr03 | depth8/300/lr.035 -> depth9/220/lr.03 schedule | 0.247536362 | 0.000048369 | 0/1 | 908.928 |
| d7_i450_lr03 | depth8/300/lr.035 -> depth7/450/lr.03 schedule | 0.247541222 | 0.000053230 | 0/1 | 906.982 |

## 실제 변경 필드

- `d8_i300_control`: control
- `d7_i450_lr03`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate
- `d8_i450_lr025`: model.name, model.params.iterations, model.params.learning_rate
- `d9_i220_lr03`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/118_reliability_capacity_refresh/20260818T121725664124Z_29b3fc0f7105`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_117`
- 기준 variant: `weights_50_35_15`
- 검증할 변경: Use main78 reliability features and CPU screening with season decay, subsample, affine postprocess, seed, and all other parameters fixed; compare depth8/300 to depth7/450, depth8/450 low-lr, and depth9/220.

### d8_i300_control

- role: control

### d7_i450_lr03

- declared change: depth8/300/lr.035 -> depth7/450/lr.03 schedule
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d7_i450_lr03_decay085_sub08`
  - `model.params.depth`: `8` → `7`
  - `model.params.iterations`: `300` → `450`
  - `model.params.learning_rate`: `0.035` → `0.03`

### d8_i450_lr025

- declared change: depth8/300/lr.035 -> depth8/450/lr.025 schedule
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_i450_lr025_decay085_sub08`
  - `model.params.iterations`: `300` → `450`
  - `model.params.learning_rate`: `0.035` → `0.025`

### d9_i220_lr03

- declared change: depth8/300/lr.035 -> depth9/220/lr.03 schedule
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d9_i220_lr03_decay085_sub08`
  - `model.params.depth`: `8` → `9`
  - `model.params.iterations`: `300` → `220`
  - `model.params.learning_rate`: `0.035` → `0.03`
