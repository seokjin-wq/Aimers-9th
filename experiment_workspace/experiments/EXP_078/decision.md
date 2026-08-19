# EXP_078 decision

- decision: `adopt`
- selected variant: `count_hands_cat`
- based on run: `RUN_001`
- comparison basis: `EXP_072`
- reference variant: `main69_control`
- decided at: `2026-08-18T05:12:01.066867+00:00`

## Ablation

Fix main69 and d8 decay0.85; separately add count_state, hands, calendar, pitcher_team, or count plus hands to the native categorical list.

## Result

- selected Brier: `0.2475158585`
- delta Brier vs control: `-2.18622e-05`
- competition score: `917.135588661`

## Reason

count_state 또는 hands 단독 categorical은 악화됐지만 세 변수를 함께 categorical로 처리하면 Brier가 0.00002186 감소하고 BSS가 908.38→917.14로 개선됐다.
