# EXP_106 decision

- decision: `adopt`
- selected variant: `track_velocity`
- based on run: `RUN_001`
- comparison basis: `EXP_068`
- reference variant: `track_physics`
- decided at: `2026-08-18T10:02:36.792416+00:00`

## Ablation

Keep latest CPU main72 fixed; compare official pre-validation Trackman velocity pair, movement triple, extension alone, and all six physics context aggregates.

## Result

- selected Brier: `0.2475086986`
- delta Brier vs control: `-3.168e-06`
- competition score: `920.0017699469`

## Reason

Official Trackman relative-speed and zone-speed context reduced CPU Brier by 0.000003168 and raised BSS 918.734 to 920.002. Movement, extension, and all-physics blocks worsened, so promote only the two velocity features.
