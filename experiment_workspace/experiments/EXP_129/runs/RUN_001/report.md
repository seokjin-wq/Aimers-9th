# 129_count_trend_shrinkage: Count trend shrinkage refinement

- 가설: The 12 count groups have enough official-train support that reducing trend shrinkage below 10000 will preserve useful relative season slopes and improve Brier.
- control: `shrinkage_10000_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a36def870636`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| shrinkage_0 | change only trend shrinkage from 10000 to 0 | 0.247445131 | -0.000000018 | 1/1 | 945.449 |
| shrinkage_2500 | change only trend shrinkage from 10000 to 2500 | 0.247445133 | -0.000000015 | 1/1 | 945.447 |
| shrinkage_5000 | change only trend shrinkage from 10000 to 5000 | 0.247445136 | -0.000000013 | 1/1 | 945.447 |
| shrinkage_10000_control | control: EXP_127 adopted trend shrinkage 10000 | 0.247445149 | 0.000000000 | 0/1 | 945.441 |

## 실제 변경 필드

- `shrinkage_10000_control`: control
- `shrinkage_0`: model.name, model.trend_shrinkage
- `shrinkage_2500`: model.name, model.trend_shrinkage
- `shrinkage_5000`: model.name, model.trend_shrinkage

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/129_count_trend_shrinkage/20260818T141952515243Z_a36def870636`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_127`
- 기준 variant: `count_trend_strength_100`
- 검증할 변경: Fix EXP_127 trend strength 1.00 and every model/calibration setting; vary only count-trend shrinkage across 0, 2500, 5000, and control 10000.

### shrinkage_10000_control

- role: control

### shrinkage_0

- declared change: change only trend shrinkage from 10000 to 0
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_s100` → `triple_count_trend_k0`
  - `model.trend_shrinkage`: `10000.0` → `0.0`

### shrinkage_2500

- declared change: change only trend shrinkage from 10000 to 2500
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_s100` → `triple_count_trend_k2500`
  - `model.trend_shrinkage`: `10000.0` → `2500.0`

### shrinkage_5000

- declared change: change only trend shrinkage from 10000 to 5000
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_s100` → `triple_count_trend_k5000`
  - `model.trend_shrinkage`: `10000.0` → `5000.0`
