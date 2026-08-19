# EXP_098 decision

- decision: `keep_control`
- selected variant: `depth8_300_control`
- based on run: `RUN_001`
- comparison basis: `EXP_095`
- reference variant: `all_three`
- decided at: `2026-08-18T08:29:35.957194+00:00`

## Ablation

Keep main72 features, season decay 0.85, probability scale/shift, sampling, and seed fixed; compare depth/iteration/learning-rate schedules from depth 5 through 8.

## Result

- selected Brier: `0.2475118666`
- delta Brier vs control: `0.0`
- competition score: `918.7335789118`

## Reason

The current depth8/300-tree CPU CatBoost remained best at BSS 918.734. All shallower longer schedules worsened Brier, so retain current capacity.
