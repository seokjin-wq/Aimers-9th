# 114_reliability_k_refinement: History reliability shrinkage refinement

- 가설: The amount of history needed to trust as-of rates can be tuned around k=100; k=50 or k=200 may better generalize to the 2024 new-player mix.
- control: `reliability_k100_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `d31b109c4f9f`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| reliability_k100_control | control: EXP_112/113 winner reliability k=100 | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| reliability_k200 | change all six reliability denominators k=100 -> 200 only | 0.247528509 | 0.000040517 | 0/1 | 912.071 |
| reliability_k50 | change all six reliability denominators k=100 -> 50 only | 0.247533911 | 0.000045918 | 0/1 | 909.909 |

## 실제 변경 필드

- `reliability_k100_control`: control
- `reliability_k50`: features.custom, features.description, features.name
- `reliability_k200`: features.custom, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/114_reliability_k_refinement/20260818T112909861309Z_d31b109c4f9f`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_113`
- 기준 variant: `all_six_control`
- 검증할 변경: Fix all main72 features and CPU subsample=0.8; change only the denominator k used in the same six reliability features across 50, 100, and 200.

### reliability_k100_control

- role: control

### reliability_k50

- declared change: change all six reliability denominators k=100 -> 50 only
- added features: `pitcher_history_reliability_k50`, `batter_history_reliability_k50`, `pitcher_success_x_reliability_k50`, `batter_success_x_reliability_k50`, `pitcher_reverse_x_reliability_k50`, `pitcher_middle_x_reliability_k50`
- removed features: `pitcher_history_reliability_k100`, `batter_history_reliability_k100`, `pitcher_success_x_reliability`, `batter_success_x_reliability`, `pitcher_reverse_x_reliability`, `pitcher_middle_x_reliability`
- model changes: none

### reliability_k200

- declared change: change all six reliability denominators k=100 -> 200 only
- added features: `pitcher_history_reliability_k200`, `batter_history_reliability_k200`, `pitcher_success_x_reliability_k200`, `batter_success_x_reliability_k200`, `pitcher_reverse_x_reliability_k200`, `pitcher_middle_x_reliability_k200`
- removed features: `pitcher_history_reliability_k100`, `batter_history_reliability_k100`, `pitcher_success_x_reliability`, `batter_success_x_reliability`, `pitcher_reverse_x_reliability`, `pitcher_middle_x_reliability`
- model changes: none
