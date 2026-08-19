# EXP_126 decision

- decision: `keep_control`
- selected variant: `manual_weights_control`
- based on run: `RUN_001`
- comparison basis: `EXP_117`
- reference variant: `weights_50_35_15`
- decided at: `2026-08-18T13:46:10.677169+00:00`

## Ablation

Fix main78 features, all component models, shifts, and count correction; blend manual 50/35/15 weights toward 2023 OOT simplex-optimal weights by 25%, 50%, or 100%.

## Result

- selected Brier: `0.2474515836`
- delta Brier vs control: `0.0`
- competition score: `942.8654277736`

## Reason

2023 OOT simplex optimum was GPU-only (0/1/0), but every move toward it worsened 2024 Brier monotonically; retain manual 50/35/15 and reject this temporally unstable weighting axis.
