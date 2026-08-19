# 101_count_triple_mean_refinement: Count-calibrated triple mean refinement

- 가설: The current count-calibrated triple overpredicts 2024 by 0.00147; lowering the CatBoost component shift by about 0.0017 should remove this mean bias without changing ranking or row independence.
- control: `catshift_m008_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `1d0bb73296c7`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| catshift_m008_control | control: EXP_094 count-k500 triple with CatBoost shift -0.008 | 0.247473801 | 0.000000000 | 0/1 | 933.972 |
| catshift_m0095 | lower CatBoost component shift to -0.0095 | 0.247473801 | 0.000000000 | 0/1 | 933.972 |
| catshift_m010 | lower CatBoost component shift to -0.010 | 0.247473801 | 0.000000000 | 0/1 | 933.972 |

## 실제 변경 필드

- `catshift_m008_control`: control
- `catshift_m0095`: model.cat_shift, model.name
- `catshift_m010`: model.cat_shift, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/101_count_triple_mean_refinement/20260818T084235078868Z_1d0bb73296c7`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_094`
- 기준 variant: `count_k500_repro`
- 검증할 변경: Keep features, triple weights, component training, and train-only count calibration fixed; compare CatBoost component shifts -0.008, -0.0095, and -0.010.

### catshift_m008_control

- role: control

### catshift_m0095

- declared change: lower CatBoost component shift to -0.0095
- added features: none
- removed features: none
- model changes:
  - `model.cat_shift`: `-0.008` → `-0.0095`
  - `model.name`: `triple_group_count_k500` → `triple_group_count_k500_catshift_m0095`

### catshift_m010

- declared change: lower CatBoost component shift to -0.010
- added features: none
- removed features: none
- model changes:
  - `model.cat_shift`: `-0.008` → `-0.01`
  - `model.name`: `triple_group_count_k500` → `triple_group_count_k500_catshift_m010`
