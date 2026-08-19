# 020_affine_calibration: 확률 affine 미세 보정

- 가설: 새 최고 모델은 평균 보정 외에도 예측 확률의 분산이 약간 작아, 중심 0.5 기준 3~9% sharpening이 Brier를 개선한다
- control: `scale100_shift010_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `3ab02bcf36e5`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| scale106_shift008 | scale 1.06, shift -0.008 | 0.247820321 | -0.000010521 | 1/1 | 795.256 |
| scale106_shift010 | scale 1.06, shift -0.010 | 0.247822197 | -0.000008645 | 1/1 | 794.505 |
| scale109_shift010 | scale 1.09, shift -0.010 | 0.247822580 | -0.000008262 | 1/1 | 794.352 |
| scale103_shift008 | scale 1.03, shift -0.008 | 0.247823682 | -0.000007160 | 1/1 | 793.911 |
| scale103_shift010 | scale 1.03, shift -0.010 | 0.247824951 | -0.000005891 | 1/1 | 793.403 |
| scale112_shift010 | scale 1.12, shift -0.010 | 0.247826099 | -0.000004743 | 1/1 | 792.943 |
| scale100_shift010_control | control: scale 1.00, shift -0.010 | 0.247830842 | 0.000000000 | 0/1 | 791.045 |
| scale106_shift012 | scale 1.06, shift -0.012 | 0.247832074 | 0.000001231 | 0/1 | 790.552 |
| scale103_shift012 | scale 1.03, shift -0.012 | 0.247834221 | 0.000003378 | 0/1 | 789.692 |

## 실제 변경 필드

- `scale100_shift010_control`: control
- `scale103_shift008`: model.name, model.prediction_scale, model.prediction_shift
- `scale103_shift010`: model.name, model.prediction_scale
- `scale103_shift012`: model.name, model.prediction_scale, model.prediction_shift
- `scale106_shift008`: model.name, model.prediction_scale, model.prediction_shift
- `scale106_shift010`: model.name, model.prediction_scale
- `scale106_shift012`: model.name, model.prediction_scale, model.prediction_shift
- `scale109_shift010`: model.name, model.prediction_scale
- `scale112_shift010`: model.name, model.prediction_scale

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/020_affine_calibration/20260817T165832384134Z_3ab02bcf36e5`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_019`
- 기준 variant: `batter_team_cat`
- 검증할 변경: batter-team categorical CatBoost와 피처를 고정하고 prediction_scale 및 prediction_shift만 변경

### scale100_shift010_control

- role: control

### scale103_shift008

- declared change: scale 1.03, shift -0.008
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale103_shift_m008`
  - `model.prediction_scale`: `None` → `1.03`
  - `model.prediction_shift`: `-0.01` → `-0.008`

### scale103_shift010

- declared change: scale 1.03, shift -0.010
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale103_shift_m010`
  - `model.prediction_scale`: `None` → `1.03`

### scale103_shift012

- declared change: scale 1.03, shift -0.012
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale103_shift_m012`
  - `model.prediction_scale`: `None` → `1.03`
  - `model.prediction_shift`: `-0.01` → `-0.012`

### scale106_shift008

- declared change: scale 1.06, shift -0.008
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale106_shift_m008`
  - `model.prediction_scale`: `None` → `1.06`
  - `model.prediction_shift`: `-0.01` → `-0.008`

### scale106_shift010

- declared change: scale 1.06, shift -0.010
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale106_shift_m010`
  - `model.prediction_scale`: `None` → `1.06`

### scale106_shift012

- declared change: scale 1.06, shift -0.012
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale106_shift_m012`
  - `model.prediction_scale`: `None` → `1.06`
  - `model.prediction_shift`: `-0.01` → `-0.012`

### scale109_shift010

- declared change: scale 1.09, shift -0.010
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale109_shift_m010`
  - `model.prediction_scale`: `None` → `1.09`

### scale112_shift010

- declared change: scale 1.12, shift -0.010
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_shift_m010` → `catboost_native_scale112_shift_m010`
  - `model.prediction_scale`: `None` → `1.12`
