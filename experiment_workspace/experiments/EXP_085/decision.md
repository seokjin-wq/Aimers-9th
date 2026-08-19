# EXP_085 decision

- decision: `reject`
- selected variant: `count_hands_control`
- based on run: `RUN_001`
- comparison basis: `EXP_080`
- reference variant: `count_hands_promoted`
- decided at: `2026-08-18T06:08:38.621843+00:00`

## Ablation

Fix EXP_080 CPU base; add recent, pitcher, batter, or all three history-missing flags one block at a time.

## Result

- selected Brier: `0.2475158585`
- delta Brier vs control: `0.0`
- competition score: `917.135588661`

## Reason

세 결측 플래그 모두 control BSS 917.14보다 악화했다. 원시 결측·월·누적량으로 이미 표현된 중복 신호라 채택하지 않는다.
