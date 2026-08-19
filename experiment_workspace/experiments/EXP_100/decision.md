# EXP_100 decision

- decision: `adopt`
- selected variant: `scale106_shift010`
- based on run: `RUN_001`
- comparison basis: `EXP_099`
- reference variant: `decay085_control`
- decided at: `2026-08-18T08:41:34.735146+00:00`

## Ablation

Keep model training fixed at depth8/300 and decay0.85; vary only post-prediction scale around 1.06 or shift around -0.008, one coordinate at a time.

## Result

- selected Brier: `0.2475103351`
- delta Brier vs control: `-1.5315e-06`
- competition score: `919.3466500919`

## Reason

With training fixed, shift -0.010 reduced Brier by 0.000001531 and raised CPU BSS 918.734 to 919.347; adopt as the latest CPU post-processing candidate, pending ensemble-level validation.
