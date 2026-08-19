# EXP_086 decision

- decision: `adopt`
- selected variant: `batter_exact`
- based on run: `RUN_001`
- comparison basis: `EXP_084`
- reference variant: `same_hand_pitchmix`
- decided at: `2026-08-18T06:15:39.351843+00:00`

## Ablation

Fix EXP_084 CPU features; replace approximate pitcher/batter current-season success and count with exact completed-season snapshots using official training labels only, individually and together.

## Result

- selected Brier: `0.247509462`
- delta Brier vs control: `-2.4046e-06`
- competition score: `919.6961758836`

## Reason

타자 exact snapshot만 Brier 0.2475118666→0.2475094620, BSS 918.73→919.70으로 개선했다. 투수 exact 및 동시 exact는 악화해 타자 쪽만 채택한다.
