# EXP_125 decision

- decision: `reject`
- selected variant: ``
- based on run: `RUN_001`
- comparison basis: `EXP_124`
- reference variant: `decay_085`
- decided at: `2026-08-18T13:29:38.494739+00:00`

## Ablation

Fix main78 features and full ExtraTrees leaf20/300-tree parameters; compare uniform season weights against decay=0.85 only.

## Result

## Reason

The 100-tree decay=0.85 screening gain did not reproduce at the ensemble-matching 300-tree capacity; uniform weighting was better by 5.199e-06, so reject ExtraTrees decay promotion.
