# EXP_115 decision

- decision: `keep_control`
- selected variant: `reliability_control`
- based on run: `RUN_001`
- comparison basis: `EXP_114`
- reference variant: `reliability_k100_control`
- decided at: `2026-08-18T11:37:28.946271+00:00`

## Ablation

Fix the EXP_114 CPU model and six reliability features; add only late-inning history, only full-count history, or both three-feature blocks.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `0.0`
- competition score: `928.2905828931`

## Reason

Late-inning, full-count, and combined history interactions all worsened the reliability-feature control; keep the six reliability features without situational additions.
