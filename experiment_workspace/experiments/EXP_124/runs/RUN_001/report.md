# 124_extratrees_season_decay_screen: ExtraTrees season-decay screening

- 가설: The ExtraTrees diversity component may improve by emphasizing recent official training seasons instead of fitting all 2019-2023 rows uniformly.
- control: `uniform_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `0af427c4235a`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| decay_085 | season sample-weight decay none -> 0.85 only | 0.248116480 | -0.000032407 | 1/1 | 676.701 |
| decay_070 | season sample-weight decay none -> 0.70 only | 0.248140082 | -0.000008805 | 1/1 | 667.253 |
| uniform_control | control: 100-tree ExtraTrees with uniform season weights | 0.248148887 | 0.000000000 | 0/1 | 663.728 |
| decay_050 | season sample-weight decay none -> 0.50 only | 0.248300318 | 0.000151431 | 0/1 | 603.109 |

## 실제 변경 필드

- `uniform_control`: control
- `decay_050`: model.name, model.season_decay
- `decay_070`: model.name, model.season_decay
- `decay_085`: model.name, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/124_extratrees_season_decay_screen/20260818T130848576007Z_0af427c4235a`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_121`
- 기준 variant: `hist_weight_0_control`
- 검증할 변경: Fix main78 features and a 100-tree ExtraTrees screen model; vary only per-season sample-weight decay among none, 0.50, 0.70, and 0.85.

### uniform_control

- role: control

### decay_050

- declared change: season sample-weight decay none -> 0.50 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `extratrees_leaf20_screen` → `extratrees_leaf20_screen_decay05`
  - `model.season_decay`: `None` → `0.5`

### decay_070

- declared change: season sample-weight decay none -> 0.70 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `extratrees_leaf20_screen` → `extratrees_leaf20_screen_decay07`
  - `model.season_decay`: `None` → `0.7`

### decay_085

- declared change: season sample-weight decay none -> 0.85 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `extratrees_leaf20_screen` → `extratrees_leaf20_screen_decay085`
  - `model.season_decay`: `None` → `0.85`
