# EXP_109 decision

- decision: `adopt`
- selected variant: `subsample_08`
- based on run: `RUN_001`
- comparison basis: `EXP_108`
- reference variant: `main72_control`
- decided at: `2026-08-18T10:46:15.976000+00:00`

## Ablation

Hold main72 features, 2019-2023 training, 2024 validation, depth, iterations, learning rate, decay, and seed fixed; change exactly one of l2_leaf_reg, random_strength, subsample, or rsm per candidate.

## Result

- selected Brier: `0.2475041715`
- delta Brier vs control: `-7.6951e-06`
- competition score: `921.8140127173`

## Reason

Subsample 0.8 was the only single-axis regularization change improving the fixed 2024 holdout, reducing Brier by 7.695e-06; adopt for a narrow follow-up sweep.
