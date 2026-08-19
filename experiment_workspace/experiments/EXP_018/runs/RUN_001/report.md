# 018_catboost_low_capacity: CatBoost 저용량 정밀 탐색

- 가설: 현재 300-tree depth6는 2024에 과적합되어 더 얕거나 적은 tree가 Brier를 개선한다
- control: `d6_i300_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `2b4e946ed0c1`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| d6_i300_control | control: depth6, 300 trees | 0.247875492 | 0.000000000 | 0/1 | 773.171 |
| d6_i225 | depth6, 225 trees | 0.247910342 | 0.000034850 | 0/1 | 759.220 |
| d5_i400 | depth5, 400 trees | 0.247970933 | 0.000095441 | 0/1 | 734.965 |
| d4_i400 | depth4, 400 trees | 0.247972420 | 0.000096928 | 0/1 | 734.370 |
| d6_i150 | depth6, 150 trees | 0.248000910 | 0.000125418 | 0/1 | 722.965 |
| d5_i250 | depth5, 250 trees | 0.248008558 | 0.000133066 | 0/1 | 719.904 |
| d4_i250 | depth4, 250 trees | 0.248027477 | 0.000151985 | 0/1 | 712.330 |
| d5_i150 | depth5, 150 trees | 0.248067417 | 0.000191924 | 0/1 | 696.342 |
| d4_i150 | depth4, 150 trees | 0.248179875 | 0.000304383 | 0/1 | 651.324 |

## 실제 변경 필드

- `d6_i300_control`: control
- `d4_i150`: model.name, model.params.depth, model.params.iterations
- `d4_i250`: model.name, model.params.depth, model.params.iterations
- `d4_i400`: model.name, model.params.depth, model.params.iterations
- `d5_i150`: model.name, model.params.depth, model.params.iterations
- `d5_i250`: model.name, model.params.depth, model.params.iterations
- `d5_i400`: model.name, model.params.depth, model.params.iterations
- `d6_i150`: model.name, model.params.iterations
- `d6_i225`: model.name, model.params.iterations

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/018_catboost_low_capacity/20260817T164709074442Z_2b4e946ed0c1`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_017`
- 기준 variant: `all_count_numeric`
- 검증할 변경: main55+count와 -0.010 shift를 고정하고 depth 4~6, iterations 100~400만 변경

### d6_i300_control

- role: control

### d4_i150

- declared change: depth4, 150 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d4_i150_shift`
  - `model.params.depth`: `6` → `4`
  - `model.params.iterations`: `300` → `150`

### d4_i250

- declared change: depth4, 250 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d4_i250_shift`
  - `model.params.depth`: `6` → `4`
  - `model.params.iterations`: `300` → `250`

### d4_i400

- declared change: depth4, 400 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d4_i400_shift`
  - `model.params.depth`: `6` → `4`
  - `model.params.iterations`: `300` → `400`

### d5_i150

- declared change: depth5, 150 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d5_i150_shift`
  - `model.params.depth`: `6` → `5`
  - `model.params.iterations`: `300` → `150`

### d5_i250

- declared change: depth5, 250 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d5_i250_shift`
  - `model.params.depth`: `6` → `5`
  - `model.params.iterations`: `300` → `250`

### d5_i400

- declared change: depth5, 400 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d5_i400_shift`
  - `model.params.depth`: `6` → `5`
  - `model.params.iterations`: `300` → `400`

### d6_i150

- declared change: depth6, 150 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d6_i150_shift`
  - `model.params.iterations`: `300` → `150`

### d6_i225

- declared change: depth6, 225 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_d6_i225_shift`
  - `model.params.iterations`: `300` → `225`
