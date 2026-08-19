# 125_extratrees_decay_full: Full ExtraTrees decay 0.85 confirmation

- 가설: The strong 100-tree ExtraTrees decay=0.85 gain will persist at the full 300-tree capacity used by the winning ensemble.
- control: `uniform_300_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `e97f695804f5`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| uniform_300_control | control: full 300-tree ExtraTrees with uniform season weights | 0.247918611 | 0.000000000 | 0/1 | 755.910 |
| decay085_300 | season sample-weight decay none -> 0.85 only | 0.247923810 | 0.000005199 | 0/1 | 753.829 |

## 실제 변경 필드

- `uniform_300_control`: control
- `decay085_300`: model.name, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/125_extratrees_decay_full/20260818T131740682094Z_e97f695804f5`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_124`
- 기준 variant: `decay_085`
- 검증할 변경: Fix main78 features and full ExtraTrees leaf20/300-tree parameters; compare uniform season weights against decay=0.85 only.

### uniform_300_control

- role: control

### decay085_300

- declared change: season sample-weight decay none -> 0.85 only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `extratrees_leaf20` → `extratrees_leaf20_decay085`
  - `model.season_decay`: `None` → `0.85`
