# EXP_090 decision

- decision: `adopt`
- selected variant: `late_pitcher_history`
- based on run: `RUN_001`
- comparison basis: `EXP_087`
- reference variant: `same_hand_pitchmix_triple`
- decided at: `2026-08-18T07:06:23.705343+00:00`

## Ablation

Fix EXP_084 CPU features; add inning phase category, phase×LI slopes, late-inning×pitcher history slopes, or all blocks.

## Result

- selected Brier: `0.2475015773`
- delta Brier vs control: `-1.02894e-05`
- competition score: `922.8525101891`

## Reason

후반 이닝×투수 통산 성공·반대·가운데 3개만 Brier 0.2475118666→0.2475015773, BSS 918.73→922.85로 개선했다. phase와 LI 블록은 악화해 제외한다.
