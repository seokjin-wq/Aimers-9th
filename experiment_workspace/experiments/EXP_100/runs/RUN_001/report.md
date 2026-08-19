# 100_latest_affine_refinement: Latest-feature affine probability refinement

- 가설: The latest 72-feature CatBoost has a different optimal probability spread and mean than the earlier main60 model, so small scale or shift changes can reduce Brier.
- control: `scale106_shift008_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `23fd5b1c1eb9`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| scale106_shift010 | scale fixed 1.06, shift -0.010 | 0.247510335 | -0.000001531 | 1/1 | 919.347 |
| scale106_shift008_control | control: current scale 1.06, shift -0.008 | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| scale104_shift008 | scale 1.04, shift fixed -0.008 | 0.247512571 | 0.000000705 | 0/1 | 918.451 |
| scale108_shift008 | scale 1.08, shift fixed -0.008 | 0.247512825 | 0.000000959 | 0/1 | 918.350 |
| scale106_shift006 | scale fixed 1.06, shift -0.006 | 0.247521398 | 0.000009531 | 0/1 | 914.918 |

## 실제 변경 필드

- `scale106_shift008_control`: control
- `scale104_shift008`: model.name, model.prediction_scale
- `scale108_shift008`: model.name, model.prediction_scale
- `scale106_shift006`: model.name, model.prediction_shift
- `scale106_shift010`: model.name, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/100_latest_affine_refinement/20260818T083637969520Z_23fd5b1c1eb9`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_099`
- 기준 variant: `decay085_control`
- 검증할 변경: Keep model training fixed at depth8/300 and decay0.85; vary only post-prediction scale around 1.06 or shift around -0.008, one coordinate at a time.

### scale106_shift008_control

- role: control

### scale104_shift008

- declared change: scale 1.04, shift fixed -0.008
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_scale104_shift008`
  - `model.prediction_scale`: `1.06` → `1.04`

### scale108_shift008

- declared change: scale 1.08, shift fixed -0.008
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_scale108_shift008`
  - `model.prediction_scale`: `1.06` → `1.08`

### scale106_shift006

- declared change: scale fixed 1.06, shift -0.006
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_scale106_shift006`
  - `model.prediction_shift`: `-0.008` → `-0.006`

### scale106_shift010

- declared change: scale fixed 1.06, shift -0.010
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay085_scale106_shift010`
  - `model.prediction_shift`: `-0.008` → `-0.01`
