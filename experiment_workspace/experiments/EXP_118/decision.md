# EXP_118 decision

- decision: `keep_control`
- selected variant: `d8_i300_control`
- based on run: `RUN_001`
- comparison basis: `EXP_117`
- reference variant: `weights_50_35_15`
- decided at: `2026-08-18T12:22:24.226012+00:00`

## Ablation

Use main78 reliability features and CPU screening with season decay, subsample, affine postprocess, seed, and all other parameters fixed; compare depth8/300 to depth7/450, depth8/450 low-lr, and depth9/220.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `0.0`
- competition score: `928.2905828931`

## Reason

The original depth8/300/lr0.035 schedule remained best on main78 reliability features; all longer, shallower, or deeper schedules worsened Brier.
