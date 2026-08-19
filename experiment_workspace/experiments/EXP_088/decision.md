# EXP_088 decision

- decision: `adopt`
- selected variant: `count_k500`
- based on run: `RUN_001`
- comparison basis: `EXP_087`
- reference variant: `same_hand_pitchmix_triple`
- decided at: `2026-08-18T06:52:17.138163+00:00`

## Ablation

Fix EXP_087 features and triple components; fit group residual offsets only from 2019-2022→2023 predictions and vary group columns and shrinkage before applying to 2024.

## Result

- selected Brier: `0.2474647761`
- delta Brier vs control: `-7.0021e-06`
- competition score: `937.5843556071`

## Reason

2019-2022→2023 잔차의 ball×strike 보정 k500이 2024 Brier 0.2474717782→0.2474647761, BSS 934.78→937.58로 개선했다. count-out·month·team은 불안정해 단순 count 보정만 채택한다.
