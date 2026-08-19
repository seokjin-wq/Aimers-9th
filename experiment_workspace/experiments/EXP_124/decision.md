# EXP_124 decision

- decision: `adopt`
- selected variant: `decay_085`
- based on run: `RUN_001`
- comparison basis: `EXP_121`
- reference variant: `hist_weight_0_control`
- decided at: `2026-08-18T13:17:20.592106+00:00`

## Ablation

Fix main78 features and a 100-tree ExtraTrees screen model; vary only per-season sample-weight decay among none, 0.50, 0.70, and 0.85.

## Result

- selected Brier: `0.2481164796`
- delta Brier vs control: `-3.24074e-05`
- competition score: `676.7014604508`

## Reason

ExtraTrees season decay 0.85 improved the 100-tree screening Brier by 3.241e-05; promote to a full 300-tree confirmation before ensemble use.
