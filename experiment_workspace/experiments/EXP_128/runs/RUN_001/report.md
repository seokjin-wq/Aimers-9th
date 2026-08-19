# 128_count_trend_strength_refinement: Count trend strength refinement

- 가설: The EXP_127 count-relative trend gain has a local optimum near full strength; testing 0.75, 1.25, and 1.50 will improve or confirm strength 1.00.
- control: `strength_100_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `d4ccedc513a4`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| strength_100_control | control: EXP_127 adopted trend strength 1.00 | 0.247450216 | 0.000000000 | 0/1 | 943.413 |
| strength_125 | change only trend strength from 1.00 to 1.25 | 0.247450578 | 0.000000363 | 0/1 | 943.268 |
| strength_075 | change only trend strength from 1.00 to 0.75 | 0.247450615 | 0.000000399 | 0/1 | 943.253 |
| strength_150 | change only trend strength from 1.00 to 1.50 | 0.247451703 | 0.000001487 | 0/1 | 942.818 |

## 실제 변경 필드

- `strength_100_control`: control
- `strength_075`: model.name, model.trend_strength
- `strength_125`: model.name, model.trend_strength
- `strength_150`: model.name, model.trend_strength

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/128_count_trend_strength_refinement/20260818T140505588953Z_d4ccedc513a4`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_127`
- 기준 variant: `count_trend_strength_100`
- 검증할 변경: Fix EXP_127 model, features, count trend groups, trend shrinkage, and all calibration; vary only trend_strength around 1.00 using 0.75, 1.00, 1.25, and 1.50.

### strength_100_control

- role: control

### strength_075

- declared change: change only trend strength from 1.00 to 0.75
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_s100` → `triple_count_trend_s075`
  - `model.trend_strength`: `1.0` → `0.75`

### strength_125

- declared change: change only trend strength from 1.00 to 1.25
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_s100` → `triple_count_trend_s125`
  - `model.trend_strength`: `1.0` → `1.25`

### strength_150

- declared change: change only trend strength from 1.00 to 1.50
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_s100` → `triple_count_trend_s150`
  - `model.trend_strength`: `1.0` → `1.5`
