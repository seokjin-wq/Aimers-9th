# EXP_099 decision

- decision: `keep_control`
- selected variant: `decay085_control`
- based on run: `RUN_001`
- comparison basis: `EXP_098`
- reference variant: `depth8_300_control`
- decided at: `2026-08-18T08:35:03.738403+00:00`

## Ablation

Keep latest features and all CatBoost parameters fixed; compare season-decay values 0.80, 0.825, 0.85, 0.875, and 0.90.

## Result

- selected Brier: `0.2475118666`
- delta Brier vs control: `0.0`
- competition score: `918.7335789118`

## Reason

Season decay 0.85 remained best at BSS 918.734 on the latest feature set; all nearby 0.80, 0.825, 0.875, and 0.90 values worsened Brier.
