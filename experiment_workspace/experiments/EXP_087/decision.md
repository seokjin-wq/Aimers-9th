# EXP_087 decision

- decision: `adopt`
- selected variant: `same_hand_pitchmix_triple`
- based on run: `RUN_001`
- comparison basis: `EXP_086`
- reference variant: `batter_exact`
- decided at: `2026-08-18T06:36:18.312164+00:00`

## Ablation

Fix EXP_080 triple model; compare original count+hands, same-hand pitchmix, and same-hand pitchmix plus exact batter snapshot feature sets.

## Result

- selected Brier: `0.2474714314`
- delta Brier vs control: `-2.22942e-05`
- competition score: `934.9201608984`

## Reason

동일손×과거 구종군 3개가 triple Brier 0.2474937256→0.2474714314, BSS 925.996→934.920으로 명확히 개선했다. exact batter 추가는 930.04로 덜 좋아 same-hand pitchmix만 채택한다.
