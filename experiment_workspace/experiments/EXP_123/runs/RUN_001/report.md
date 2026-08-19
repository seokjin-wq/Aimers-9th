# 123_eda_monotonic_constraints: EDA-guided monotonic constraints

- 가설: Enforcing known directional relationships for prior success, reverse, and middle rates may reduce temporal overfitting and improve 2024 Brier.
- control: `unconstrained_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `cf3e83d3f0d5`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| unconstrained_control | control: latest CPU without monotonic constraints | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| monotone_success | force pitcher and batter career success rates monotone positive only | 0.247553740 | 0.000065747 | 0/1 | 901.971 |
| monotone_all | apply all four success/failure directional constraints | 0.247554813 | 0.000066821 | 0/1 | 901.542 |
| monotone_failure | force pitcher reverse and middle rates monotone negative only | 0.247575099 | 0.000087106 | 0/1 | 893.421 |

## 실제 변경 필드

- `unconstrained_control`: control
- `monotone_success`: model.name, model.params.monotone_constraints.asof_batter_success_rate, model.params.monotone_constraints.asof_pitcher_success_rate
- `monotone_failure`: model.name, model.params.monotone_constraints.asof_pitcher_middle_rate, model.params.monotone_constraints.asof_pitcher_reverse_rate
- `monotone_all`: model.name, model.params.monotone_constraints.asof_batter_success_rate, model.params.monotone_constraints.asof_pitcher_middle_rate, model.params.monotone_constraints.asof_pitcher_reverse_rate, model.params.monotone_constraints.asof_pitcher_success_rate

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/123_eda_monotonic_constraints/20260818T130316436094Z_cf3e83d3f0d5`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_118`
- 기준 variant: `d8_i300_control`
- 검증할 변경: Fix main78 features and winning CPU parameters; add monotonic constraints only for success rates, only reverse/middle failure rates, or all four directional constraints.

### unconstrained_control

- role: control

### monotone_success

- declared change: force pitcher and batter career success rates monotone positive only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_sub08_monotone_success`
  - `model.params.monotone_constraints`: `None` → `{'asof_pitcher_success_rate': 1, 'asof_batter_success_rate': 1}`

### monotone_failure

- declared change: force pitcher reverse and middle rates monotone negative only
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_sub08_monotone_failure`
  - `model.params.monotone_constraints`: `None` → `{'asof_pitcher_reverse_rate': -1, 'asof_pitcher_middle_rate': -1}`

### monotone_all

- declared change: apply all four success/failure directional constraints
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_d8_decay085_sub08` → `catboost_d8_sub08_monotone_all`
  - `model.params.monotone_constraints`: `None` → `{'asof_pitcher_success_rate': 1, 'asof_batter_success_rate': 1, 'asof_pitcher_reverse_rate': -1, 'asof_pitcher_middle_rate': -1}`
