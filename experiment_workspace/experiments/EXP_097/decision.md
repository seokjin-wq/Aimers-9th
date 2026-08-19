# EXP_097 decision

- decision: `keep_control`
- selected variant: `current_triple`
- based on run: `RUN_001`
- comparison basis: `EXP_096`
- reference variant: `late_all_three`
- decided at: `2026-08-18T08:20:35.281494+00:00`

## Ablation

Rerun the fixed triple ensemble with current versus complete late-history features only; defer count calibration to a separate experiment.

## Result

- selected Brier: `0.2474719423`
- delta Brier vs control: `0.0`
- competition score: `934.715664474`

## Reason

Fresh triple rerun reversed the small EXP_091 gain: late-history features worsened Brier by 0.000006598 and BSS 934.716 to 932.074. Keep the current same-hand triple and do not spend another experiment combining late history with calibration.
