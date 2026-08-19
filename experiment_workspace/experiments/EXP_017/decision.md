# EXP_017 decision

- decision: `adopt`
- selected variant: `all_count_numeric`
- based on run: `RUN_001`
- comparison basis: `EXP_016`
- reference variant: `single_seed_control`
- decided at: `2026-08-17T16:45:14.695770+00:00`

## Ablation

shifted native CatBoost와 main55를 고정하고 count_state, full count, 2-strike, 3-ball, 2-out을 각각 단독 추가하고 전체 count_state 범주화 비교

## Result

- selected Brier: `0.2478754923`
- delta Brier vs control: `-4.52048e-05`
- competition score: `773.1709037273`

## Reason

카운트 5개를 numeric으로 함께 추가한 구성이 control 대비 Brier를 0.000045205 낮춰 BSS 773.171로 최고였고, 단일 피처 및 count_state 범주형보다 우수했다.
