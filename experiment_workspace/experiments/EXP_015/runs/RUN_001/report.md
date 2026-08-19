# 015_forward_probability_shift: 과거 fold 기반 확률 shift

- 가설: 2022~2023의 과거 예측 편향으로 정한 음의 확률 shift가 2024 Brier를 개선한다
- control: `no_shift_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `3f45b96c6df1`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| shift_m010 | 모든 확률에 -0.010 | 0.247875492 | -0.000092648 | 1/1 | 773.171 |
| shift_forward | 2022~2023 과거 fold 편향으로 고정한 -0.0113955 | 0.247878466 | -0.000089674 | 1/1 | 771.981 |
| shift_m005 | 모든 확률에 -0.005 | 0.247896816 | -0.000071324 | 1/1 | 764.635 |
| shift_m015 | 모든 확률에 -0.015 | 0.247904168 | -0.000063971 | 1/1 | 761.692 |
| no_shift_control | control: shift 0 | 0.247968140 | 0.000000000 | 0/1 | 736.083 |

## 실제 변경 필드

- `no_shift_control`: control
- `shift_m005`: model.name, model.prediction_shift
- `shift_m010`: model.name, model.prediction_shift
- `shift_forward`: model.name, model.prediction_shift
- `shift_m015`: model.name, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/015_forward_probability_shift/20260817T163116472270Z_3f45b96c6df1`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_014`
- 기준 variant: `main60_control`
- 검증할 변경: main55+count CatBoost를 고정하고 prediction shift만 0, -0.005, -0.010, 과거-fold -0.0113955, -0.015로 변경

### no_shift_control

- role: control

### shift_m005

- declared change: 모든 확률에 -0.005
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_shift_m005`
  - `model.prediction_shift`: `None` → `-0.005`

### shift_m010

- declared change: 모든 확률에 -0.010
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_shift_m010`
  - `model.prediction_shift`: `None` → `-0.01`

### shift_forward

- declared change: 2022~2023 과거 fold 편향으로 고정한 -0.0113955
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_shift_forward`
  - `model.prediction_shift`: `None` → `-0.011395498281243616`

### shift_m015

- declared change: 모든 확률에 -0.015
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_shift_m015`
  - `model.prediction_shift`: `None` → `-0.015`
