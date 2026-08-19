# 104_eda_context_residuals: EDA context OOT residual calibration

- 가설: Residual biases by hand matchup, inning, or base state remain after the model and can be corrected using only 2023 official-training OOT residual tables and each row's own context.
- control: `count_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `46a25a5d127b`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_control | control: EXP_103 count residual groups | 0.247471210 | 0.000000000 | 0/1 | 935.009 |
| base_k500 | 2023 OOT residual by current-row base_state, shrinkage 500 | 0.247480517 | 0.000009307 | 0/1 | 931.283 |
| inning_k1000 | 2023 OOT residual by current-row inning, shrinkage 1000 | 0.247481003 | 0.000009792 | 0/1 | 931.089 |
| count_base_k1000 | 2023 OOT residual by count x base_state, shrinkage 1000 | 0.247521788 | 0.000050578 | 0/1 | 914.762 |
| hands_k500 | 2023 OOT residual by pitcher_hand x batter_hand, shrinkage 500 | 0.247544666 | 0.000073456 | 0/1 | 905.604 |
| count_hands_k1000 | 2023 OOT residual by count x both hands, shrinkage 1000 | 0.247549874 | 0.000078663 | 0/1 | 903.519 |

## 실제 변경 필드

- `count_control`: control
- `hands_k500`: model.group_columns, model.name
- `count_hands_k1000`: model.group_columns, model.group_shrinkage, model.name
- `inning_k1000`: model.group_columns, model.group_shrinkage, model.name
- `base_k500`: model.group_columns, model.name
- `count_base_k1000`: model.group_columns, model.group_shrinkage, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/104_eda_context_residuals/20260818T093626554440Z_46a25a5d127b`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_103`
- 기준 variant: `residual_scale_1_control`
- 검증할 변경: Keep the corrected triple, weights, features, and calibration mechanics fixed; compare count control against train-only residual groups for hands, count+hands, inning, base_state, and count+base_state.

### count_control

- role: control

### hands_k500

- declared change: 2023 OOT residual by pitcher_hand x batter_hand, shrinkage 500
- added features: none
- removed features: none
- model changes:
  - `model.group_columns`: `['balls_before', 'strikes_before']` → `['pitcher_hand', 'batter_hand']`
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_hands_k500_shift_m0095_w50_35_15`

### count_hands_k1000

- declared change: 2023 OOT residual by count x both hands, shrinkage 1000
- added features: none
- removed features: none
- model changes:
  - `model.group_columns`: `['balls_before', 'strikes_before']` → `['balls_before', 'strikes_before', 'pitcher_hand', 'batter_hand']`
  - `model.group_shrinkage`: `500.0` → `1000.0`
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_count_hands_k1000_shift_m0095_w50_35_15`

### inning_k1000

- declared change: 2023 OOT residual by current-row inning, shrinkage 1000
- added features: none
- removed features: none
- model changes:
  - `model.group_columns`: `['balls_before', 'strikes_before']` → `['inning']`
  - `model.group_shrinkage`: `500.0` → `1000.0`
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_inning_k1000_shift_m0095_w50_35_15`

### base_k500

- declared change: 2023 OOT residual by current-row base_state, shrinkage 500
- added features: none
- removed features: none
- model changes:
  - `model.group_columns`: `['balls_before', 'strikes_before']` → `['base_state']`
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_base_k500_shift_m0095_w50_35_15`

### count_base_k1000

- declared change: 2023 OOT residual by count x base_state, shrinkage 1000
- added features: none
- removed features: none
- model changes:
  - `model.group_columns`: `['balls_before', 'strikes_before']` → `['balls_before', 'strikes_before', 'base_state']`
  - `model.group_shrinkage`: `500.0` → `1000.0`
  - `model.name`: `triple_group_count_k500_shift_m0095_w50_35_15` → `triple_group_count_base_k1000_shift_m0095_w50_35_15`
