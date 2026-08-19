# EXP_084 decision

- decision: `adopt`
- selected variant: `same_hand_pitchmix`
- based on run: `RUN_001`
- comparison basis: `EXP_080`
- reference variant: `count_hands_promoted`
- decided at: `2026-08-18T06:03:49.135547+00:00`

## Ablation

Fix EXP_080 CPU base and add pure hand-matchup, same-hand×pitchmix, separate-hand×pitchmix, or full four-matchup×pitchmix interactions using only each row's asof values.

## Result

- selected Brier: `0.2475118666`
- delta Brier vs control: `-3.9919e-06`
- competition score: `918.7335789118`

## Reason

EDA 가설 중 동일손×과거 구종비율 3개만 Brier 0.2475158585→0.2475118666, BSS 917.14→918.73으로 개선했다. 더 복잡한 손 조합은 악화해 단순 3개만 채택한다.
