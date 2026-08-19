# EXP_079 decision

- decision: `keep_control`
- selected variant: `count_both_hands_control`
- based on run: `RUN_001`
- comparison basis: `EXP_078`
- reference variant: `count_hands_cat`
- decided at: `2026-08-18T05:17:22.081106+00:00`

## Ablation

Use count+both-hands as control; remove one hand at a time, replace hands by same_hand, or add same_hand to all three.

## Result

- selected Brier: `0.2475158585`
- delta Brier vs control: `0.0`
- competition score: `917.135588661`

## Reason

count와 양손 세 categorical의 동시 상호작용이 필요했다. 한 손 제거, same_hand 대체 또는 추가는 모두 BSS 883~904로 악화되어 EXP_078 조합을 그대로 유지한다.
