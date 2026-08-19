# 006_catboost_capacity: CatBoost 깊이와 반복 수 탐색

- 가설: 현재 300-tree depth6 모델은 과소학습 상태이며 더 많은 tree 또는 다른 depth가 2024 Brier를 개선한다
- control: `d6_i300_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `f25afffb7b77`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| d6_i300_control | control: depth6, 300 trees | 0.248009268 | 0.000000000 | 0/1 | 719.619 |
| d5_i600 | depth5, 600 trees | 0.248059457 | 0.000050190 | 0/1 | 699.528 |
| d6_i600 | depth6, 600 trees | 0.248080892 | 0.000071625 | 0/1 | 690.947 |
| d7_i1000_lr03 | depth7, 1000 trees, learning_rate 0.03 | 0.248115930 | 0.000106662 | 0/1 | 676.922 |
| d6_i1000 | depth6, 1000 trees | 0.248198476 | 0.000189209 | 0/1 | 643.878 |
| d7_i600 | depth7, 600 trees | 0.248223702 | 0.000214435 | 0/1 | 633.779 |
| d8_i600 | depth8, 600 trees | 0.248251296 | 0.000242029 | 0/1 | 622.733 |

## 실제 변경 필드

- `d6_i300_control`: control
- `d5_i600`: model.name, model.params.depth, model.params.iterations
- `d6_i600`: model.name, model.params.iterations
- `d6_i1000`: model.name, model.params.iterations
- `d7_i600`: model.name, model.params.depth, model.params.iterations
- `d8_i600`: model.name, model.params.depth, model.params.iterations
- `d7_i1000_lr03`: model.name, model.params.depth, model.params.iterations, model.params.learning_rate

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/006_catboost_capacity/20260817T154432280023Z_f25afffb7b77`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_004`
- 기준 variant: `native_basic`
- 검증할 변경: main55와 native 기본 3개 범주를 고정하고 CatBoost depth와 iterations 조합만 변경

### d6_i300_control

- role: control

### d5_i600

- declared change: depth5, 600 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_d5_i600`
  - `model.params.depth`: `6` → `5`
  - `model.params.iterations`: `300` → `600`

### d6_i600

- declared change: depth6, 600 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_d6_i600`
  - `model.params.iterations`: `300` → `600`

### d6_i1000

- declared change: depth6, 1000 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_d6_i1000`
  - `model.params.iterations`: `300` → `1000`

### d7_i600

- declared change: depth7, 600 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_d7_i600`
  - `model.params.depth`: `6` → `7`
  - `model.params.iterations`: `300` → `600`

### d8_i600

- declared change: depth8, 600 trees
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_d8_i600`
  - `model.params.depth`: `6` → `8`
  - `model.params.iterations`: `300` → `600`

### d7_i1000_lr03

- declared change: depth7, 1000 trees, learning_rate 0.03
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_d7_i1000_lr03`
  - `model.params.depth`: `6` → `7`
  - `model.params.iterations`: `300` → `1000`
  - `model.params.learning_rate`: `0.05` → `0.03`
