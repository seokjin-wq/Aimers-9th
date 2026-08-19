# 011_season_recency_weight: 시즌 최근성 학습 가중치

- 가설: 오래된 시즌의 가중치를 낮추면 2023과 유사한 2024 분포에 적응해 Brier가 개선된다
- control: `uniform_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `808434d403de`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| uniform_control | control: 모든 2019~2023 행 weight 1.0 | 0.247968140 | 0.000000000 | 0/1 | 736.083 |
| decay_085 | 과거 한 시즌마다 weight 0.85배 | 0.248007538 | 0.000039398 | 0/1 | 720.312 |
| decay_070 | 과거 한 시즌마다 weight 0.70배 | 0.248090693 | 0.000122553 | 0/1 | 687.024 |
| decay_050 | 과거 한 시즌마다 weight 0.50배 | 0.248130402 | 0.000162262 | 0/1 | 671.128 |
| decay_025 | 과거 한 시즌마다 weight 0.25배 | 0.248135435 | 0.000167295 | 0/1 | 669.114 |

## 실제 변경 필드

- `uniform_control`: control
- `decay_085`: model.name, model.season_decay
- `decay_070`: model.name, model.season_decay
- `decay_050`: model.name, model.season_decay
- `decay_025`: model.name, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/011_season_recency_weight/20260817T161226009870Z_808434d403de`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_009`
- 기준 variant: `count_control`
- 검증할 변경: main55+count와 CatBoost 구조를 고정하고 시즌이 한 해 과거로 갈 때의 sample weight decay만 1.0, 0.85, 0.70, 0.50, 0.25로 변경

### uniform_control

- role: control

### decay_085

- declared change: 과거 한 시즌마다 weight 0.85배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_decay085`
  - `model.season_decay`: `None` → `0.85`

### decay_070

- declared change: 과거 한 시즌마다 weight 0.70배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_decay070`
  - `model.season_decay`: `None` → `0.7`

### decay_050

- declared change: 과거 한 시즌마다 weight 0.50배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_decay050`
  - `model.season_decay`: `None` → `0.5`

### decay_025

- declared change: 과거 한 시즌마다 weight 0.25배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_native_300` → `catboost_native_decay025`
  - `model.season_decay`: `None` → `0.25`
