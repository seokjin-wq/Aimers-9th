# EXP_113 decision

- decision: `keep_control`
- selected variant: `all_six_control`
- based on run: `RUN_001`
- comparison basis: `EXP_112`
- reference variant: `history_reliability`
- decided at: `2026-08-18T11:28:24.665768+00:00`

## Ablation

Use the six-feature EXP_112 winner as control; remove exactly one two-feature block at a time: reliability levels, success-weighted rates, or reverse/middle-weighted rates.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `0.0`
- competition score: `928.2905828931`

## Reason

All six reliability features are complementary: removing any two-feature block worsened Brier, with reverse/middle weighting most important; keep the complete EXP_112 block.
