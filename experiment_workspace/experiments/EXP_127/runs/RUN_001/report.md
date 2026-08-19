# 127_count_relative_season_trend: Count-relative season trend correction

- 가설: A row-local balls/strikes correction learned from 2019-2023 centered target-rate trends will improve 2024 Brier beyond the existing global shift and 2023 OOT count residual.
- control: `count_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `5373baac01c7`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_trend_strength_100 | add 100% of official-train centered count season trend | 0.247445141 | -0.000006376 | 1/1 | 945.444 |
| count_trend_strength_050 | add 50% of official-train centered count season trend | 0.247446806 | -0.000004712 | 1/1 | 944.778 |
| count_trend_strength_025 | add 25% of official-train centered count season trend | 0.247448781 | -0.000002737 | 1/1 | 943.987 |
| count_control | control: fixed EXP_117 triple with 2023 OOT count residual | 0.247451518 | 0.000000000 | 0/1 | 942.892 |

## 실제 변경 필드

- `count_control`: control
- `count_trend_strength_025`: model.name, model.trend_group_columns, model.trend_shrinkage, model.trend_strength
- `count_trend_strength_050`: model.name, model.trend_group_columns, model.trend_shrinkage, model.trend_strength
- `count_trend_strength_100`: model.name, model.trend_group_columns, model.trend_shrinkage, model.trend_strength

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/127_count_relative_season_trend/20260818T135109701732Z_5373baac01c7`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_117`
- 기준 variant: `weights_50_35_15`
- 검증할 변경: Fix main78, all three component models, 50/35/15 weights, affine shifts, and OOT count residual; add only an official-train-only centered count trend offset at strengths 0.25, 0.50, or 1.00.

### count_control

- role: control

### count_trend_strength_025

- declared change: add 25% of official-train centered count season trend
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_count_trend_s025`
  - `model.trend_group_columns`: `None` → `['balls_before', 'strikes_before']`
  - `model.trend_shrinkage`: `None` → `10000.0`
  - `model.trend_strength`: `None` → `0.25`

### count_trend_strength_050

- declared change: add 50% of official-train centered count season trend
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_count_trend_s050`
  - `model.trend_group_columns`: `None` → `['balls_before', 'strikes_before']`
  - `model.trend_shrinkage`: `None` → `10000.0`
  - `model.trend_strength`: `None` → `0.5`

### count_trend_strength_100

- declared change: add 100% of official-train centered count season trend
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_count_trend_s100`
  - `model.trend_group_columns`: `None` → `['balls_before', 'strikes_before']`
  - `model.trend_shrinkage`: `None` → `10000.0`
  - `model.trend_strength`: `None` → `1.0`
