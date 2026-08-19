# 110_latest_catboost_subsample: Latest CatBoost subsample refinement

- 가설: The local optimum lies near subsample 0.8 and a narrow sweep can improve on EXP_109 without changing features or validation protocol.
- control: `subsample_08_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `d6efb3d20e77`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| subsample_08_control | control: EXP_109 winner subsample=0.80 | 0.247504172 | 0.000000000 | 0/1 | 921.814 |
| subsample_085 | subsample 0.80 -> 0.85 only | 0.247530188 | 0.000026016 | 0/1 | 911.399 |
| subsample_09 | subsample 0.80 -> 0.90 only | 0.247538306 | 0.000034135 | 0/1 | 908.150 |
| subsample_075 | subsample 0.80 -> 0.75 only | 0.247539106 | 0.000034935 | 0/1 | 907.829 |

## 실제 변경 필드

- `subsample_08_control`: control
- `subsample_075`: model.name, model.params.subsample
- `subsample_085`: model.name, model.params.subsample
- `subsample_09`: model.name, model.params.subsample

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/110_latest_catboost_subsample/20260818T104643936326Z_d6efb3d20e77`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_109`
- 기준 variant: `subsample_08`
- 검증할 변경: Fix the EXP_109 winning model and main72 features; vary only subsample across 0.75, 0.80, 0.85, and 0.90.

### subsample_08_control

- role: control

### subsample_075

- declared change: subsample 0.80 -> 0.75 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_decay085_sub075`
  - `model.params.subsample`: `0.8` → `0.75`

### subsample_085

- declared change: subsample 0.80 -> 0.85 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_decay085_sub085`
  - `model.params.subsample`: `0.8` → `0.85`

### subsample_09

- declared change: subsample 0.80 -> 0.90 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_decay085_sub09`
  - `model.params.subsample`: `0.8` → `0.9`
