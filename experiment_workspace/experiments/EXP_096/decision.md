# EXP_096 decision

- decision: `adopt`
- selected variant: `late_all_three`
- based on run: `RUN_001`
- comparison basis: `EXP_090`
- reference variant: `late_pitcher_history`
- decided at: `2026-08-18T08:05:01.769101+00:00`

## Ablation

Hold the EXP_090 same-hand pitch-mix control and model fixed; compare three late-inning pitcher-history interactions individually, in pairs, and together.

## Result

- selected Brier: `0.2475015773`
- delta Brier vs control: `-1.02894e-05`
- competition score: `922.8525101891`

## Reason

The complete late-history block was best at BSS 922.853 versus 918.734 control. The success+reverse pair improved to 920.914 but remained inferior, while every single interaction degraded; retain all three as a promotion candidate.
