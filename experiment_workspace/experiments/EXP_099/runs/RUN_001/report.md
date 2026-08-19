# 099_latest_season_decay: Latest-feature season-decay refinement

- 가설: The broad EXP_060 optimum near 0.85 can be refined on the latest 72-feature set to improve temporal generalization.
- control: `decay085_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a63da8bfc5aa`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| decay085_control | control: current season decay 0.85 | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| decay0875 | season decay 0.875 | 0.247529193 | 0.000017326 | 0/1 | 911.798 |
| decay0825 | season decay 0.825 | 0.247534786 | 0.000022919 | 0/1 | 909.559 |
| decay090 | season decay 0.90 | 0.247536144 | 0.000024277 | 0/1 | 909.015 |
| decay080 | season decay 0.80 | 0.247544632 | 0.000032766 | 0/1 | 905.617 |

## 실제 변경 필드

- `decay085_control`: control
- `decay080`: model.name, model.season_decay
- `decay0825`: model.name, model.season_decay
- `decay0875`: model.name, model.season_decay
- `decay090`: model.name, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/099_latest_season_decay/20260818T083012351130Z_a63da8bfc5aa`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_098`
- 기준 variant: `depth8_300_control`
- 검증할 변경: Keep latest features and all CatBoost parameters fixed; compare season-decay values 0.80, 0.825, 0.85, 0.875, and 0.90.

### decay085_control

- role: control

### decay080

- declared change: season decay 0.80
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay080`
  - `model.season_decay`: `0.85` → `0.8`

### decay0825

- declared change: season decay 0.825
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay0825`
  - `model.season_decay`: `0.85` → `0.825`

### decay0875

- declared change: season decay 0.875
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay0875`
  - `model.season_decay`: `0.85` → `0.875`

### decay090

- declared change: season decay 0.90
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085` → `catboost_d8_decay090`
  - `model.season_decay`: `0.85` → `0.9`
