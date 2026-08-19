# EXP_105 decision

- decision: `keep_control`
- selected variant: `same_pitchmix_control`
- based on run: `RUN_001`
- comparison basis: `EXP_095`
- reference variant: `all_three`
- decided at: `2026-08-18T09:55:59.318158+00:00`

## Ablation

Keep latest CPU CatBoost and main72 fixed; add one safe official-train context target-effect feature at a time and then all four together.

## Result

- selected Brier: `0.2475118666`
- delta Brier vs control: `0.0`
- competition score: `918.7335789118`

## Reason

All four safe season-OOF official-train context effects worsened Brier. The pressure effect was closest but still lost 0.000010039; retain main72 and reject this target-effect block.
