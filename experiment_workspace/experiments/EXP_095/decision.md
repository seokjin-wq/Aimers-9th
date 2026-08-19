# EXP_095 decision

- decision: `adopt`
- selected variant: `all_three`
- based on run: `RUN_001`
- comparison basis: `EXP_084`
- reference variant: `same_hand_pitchmix`
- decided at: `2026-08-18T07:56:00.951731+00:00`

## Ablation

Keep the EXP_084 count+hands control fixed and compare each same-hand pitch-mix interaction alone, all three pairs, and the existing all-three variant.

## Result

- selected Brier: `0.2475118666`
- delta Brier vs control: `-3.9919e-06`
- competition score: `918.7335789118`

## Reason

The existing all-three interaction set remained best at BSS 918.734 versus 917.136 control; every one- and two-feature subset degraded Brier, so retain the complete same-hand pitch-mix block and reject all smaller subsets.
