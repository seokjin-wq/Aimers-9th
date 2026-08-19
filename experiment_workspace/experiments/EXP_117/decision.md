# EXP_117 decision

- decision: `adopt`
- selected variant: `weights_50_35_15`
- based on run: `RUN_001`
- comparison basis: `EXP_116`
- reference variant: `triple_history_reliability`
- decided at: `2026-08-18T12:16:13.991944+00:00`

## Ablation

Fix main78 reliability features, all component parameters, shifts, count correction, and ExtraTrees weight where applicable; vary only CPU/GPU/Extra blend weights around 45/40/15.

## Result

- selected Brier: `0.2474515794`
- delta Brier vs control: `-4.505e-07`
- competition score: `942.8671007335`

## Reason

With identical cached component predictions, shifting 5% from GPU to the improved CPU component gave the lowest Brier by 4.505e-07; adopt 50/35/15 as a small deterministic blend-weight gain.
