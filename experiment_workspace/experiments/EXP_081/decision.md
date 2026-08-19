# EXP_081 decision

- decision: `keep_control`
- selected variant: `separate_count_hands_control`
- based on run: `RUN_001`
- comparison basis: `EXP_080`
- reference variant: `count_hands_promoted`
- decided at: `2026-08-18T05:38:55.710692+00:00`

## Ablation

Screen composite count×hands, count×same-hand, count×outs, and count×hands×outs categories, alone or alongside the EXP_078 separate categories.

## Result

- selected Brier: `0.2475158585`
- delta Brier vs control: `0.0`
- competition score: `917.135588661`

## Reason

모든 직접 복합 범주는 BSS 884~904로 separate count_state·pitcher_hand·batter_hand control 917.14보다 악화되어 원래 세 범주 표현을 유지한다.
