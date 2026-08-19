# EXP_107 decision

- decision: `keep_control`
- selected variant: `current_corrected_triple`
- based on run: `RUN_001`
- comparison basis: `EXP_106`
- reference variant: `track_velocity`
- decided at: `2026-08-18T10:27:10.159309+00:00`

## Ablation

Keep EXP_103 corrected count-calibrated triple fixed; compare current main72 against main72 plus only Trackman relative-speed and zone-speed context.

## Result

- selected Brier: `0.2474634382`
- delta Brier vs control: `0.0`
- competition score: `938.1199198277`

## Reason

The Trackman velocity pair improved the CPU model but did not transfer to the corrected triple: Brier worsened by 0.000000850 and BSS fell 938.120 to 937.780. Keep the current main72 corrected triple.
