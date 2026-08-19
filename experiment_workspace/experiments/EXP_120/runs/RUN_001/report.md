# 120_reliability_categorical_processing: Reliability CatBoost categorical processing

- 가설: The expanded categorical and reliability representation may benefit from richer CatBoost CTR combinations or different one-hot thresholds even though tree-capacity changes failed.
- control: `categorical_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `df6d062dddb9`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| categorical_control | control: latest CPU default categorical processing | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| one_hot_max_size_5 | one_hot_max_size default 2 -> 5 only | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| one_hot_max_size_16 | one_hot_max_size default 2 -> 16 only | 0.247518014 | 0.000030021 | 0/1 | 916.273 |
| max_ctr_complexity_2 | max_ctr_complexity default 1 -> 2 only | 0.247532253 | 0.000044260 | 0/1 | 910.573 |

## 실제 변경 필드

- `categorical_control`: control
- `max_ctr_complexity_2`: model.name, model.params.max_ctr_complexity
- `one_hot_max_size_5`: model.name, model.params.one_hot_max_size
- `one_hot_max_size_16`: model.name, model.params.one_hot_max_size

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/120_reliability_categorical_processing/20260818T123802598273Z_df6d062dddb9`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_118`
- 기준 variant: `d8_i300_control`
- 검증할 변경: Fix main78 features and all winning CPU parameters; change exactly one categorical-processing parameter per candidate: max_ctr_complexity=2, one_hot_max_size=5, or one_hot_max_size=16.

### categorical_control

- role: control

### max_ctr_complexity_2

- declared change: max_ctr_complexity default 1 -> 2 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_decay085_sub08_ctr2`
  - `model.params.max_ctr_complexity`: `None` → `2`

### one_hot_max_size_5

- declared change: one_hot_max_size default 2 -> 5 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_decay085_sub08_onehot5`
  - `model.params.one_hot_max_size`: `None` → `5`

### one_hot_max_size_16

- declared change: one_hot_max_size default 2 -> 16 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_decay085_sub08_onehot16`
  - `model.params.one_hot_max_size`: `None` → `16`
