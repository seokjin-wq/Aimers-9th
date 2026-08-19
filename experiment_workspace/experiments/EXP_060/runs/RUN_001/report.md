# 060_season_state_recency_weight: 시즌 상태 최근성 가중 재검증

- 가설: 현재 시즌 상태 피처가 연도별 구조 변화를 설명하므로 완만한 최근성 가중이 과거 시즌 잡음을 줄일 수 있다
- control: `uniform`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `27fd2ed60ecb`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| decay085 | 과거 1년당 가중치 0.85배 | 0.247537721 | -0.000030027 | 1/1 | 908.384 |
| decay095 | 과거 1년당 가중치 0.95배 | 0.247563085 | -0.000004663 | 1/1 | 898.230 |
| decay090 | 과거 1년당 가중치 0.90배 | 0.247567731 | -0.000000017 | 1/1 | 896.371 |
| uniform | control: 모든 2019~2023 행 동일 가중 | 0.247567748 | 0.000000000 | 0/1 | 896.364 |
| decay075 | 과거 1년당 가중치 0.75배 | 0.247577726 | 0.000009978 | 0/1 | 892.369 |

## 실제 변경 필드

- `uniform`: control
- `decay095`: model.name, model.season_decay
- `decay090`: model.name, model.season_decay
- `decay085`: model.name, model.season_decay
- `decay075`: model.name, model.season_decay

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/060_season_state_recency_weight/20260818T025551893979Z_27fd2ed60ecb`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_059`
- 기준 variant: `d8_i300`
- 검증할 변경: main69 depth8을 고정하고 시즌당 sample weight decay 1.0, 0.95, 0.90, 0.85, 0.75만 변경

### uniform

- role: control

### decay095

- declared change: 과거 1년당 가중치 0.95배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_cpu_d8_i300_lr035` → `catboost_d8_decay095`
  - `model.season_decay`: `None` → `0.95`

### decay090

- declared change: 과거 1년당 가중치 0.90배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_cpu_d8_i300_lr035` → `catboost_d8_decay090`
  - `model.season_decay`: `None` → `0.9`

### decay085

- declared change: 과거 1년당 가중치 0.85배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_cpu_d8_i300_lr035` → `catboost_d8_decay085`
  - `model.season_decay`: `None` → `0.85`

### decay075

- declared change: 과거 1년당 가중치 0.75배
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_cpu_d8_i300_lr035` → `catboost_d8_decay075`
  - `model.season_decay`: `None` → `0.75`
