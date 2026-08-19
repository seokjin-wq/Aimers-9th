# 119_reliability_triple_shift: Reliability triple CatBoost shift refinement

- 가설: The reliability features and 50/35/15 weights slightly change ensemble calibration, so neighboring CatBoost shifts around -0.0095 may improve Brier.
- control: `catshift_m0095_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `e9f0abc64a29`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| catshift_m0095_control | control: EXP_117 winner cat_shift=-0.0095 | 0.247451658 | 0.000000000 | 0/1 | 942.836 |
| catshift_m010 | cat_shift -0.0095 -> -0.0100 only | 0.247451735 | 0.000000077 | 0/1 | 942.805 |
| catshift_m009 | cat_shift -0.0095 -> -0.0090 only | 0.247451942 | 0.000000284 | 0/1 | 942.722 |

## 실제 변경 필드

- `catshift_m0095_control`: control
- `catshift_m009`: model.cat_shift, model.name
- `catshift_m010`: model.cat_shift, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/119_reliability_triple_shift/20260818T122310990900Z_e9f0abc64a29`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_117`
- 기준 variant: `weights_50_35_15`
- 검증할 변경: Fix main78 features, component models, 50/35/15 weights, ExtraTrees shift, count correction, and scales; vary only CatBoost component shift among -0.0090, -0.0095, and -0.0100.

### catshift_m0095_control

- role: control

### catshift_m009

- declared change: cat_shift -0.0095 -> -0.0090 only
- added features: none
- removed features: none
- model changes:
  - `model.cat_shift`: `-0.0095` → `-0.009`
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_count_sub08_w50_35_15_shift_m009`

### catshift_m010

- declared change: cat_shift -0.0095 -> -0.0100 only
- added features: none
- removed features: none
- model changes:
  - `model.cat_shift`: `-0.0095` → `-0.01`
  - `model.name`: `triple_count_m0095_sub08_w50_35_15` → `triple_count_sub08_w50_35_15_shift_m010`
