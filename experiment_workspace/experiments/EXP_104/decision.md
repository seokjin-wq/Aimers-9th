# EXP_104 decision

- decision: `keep_control`
- selected variant: `count_control`
- based on run: `RUN_001`
- comparison basis: `EXP_103`
- reference variant: `residual_scale_1_control`
- decided at: `2026-08-18T09:48:30.890887+00:00`

## Ablation

Keep the corrected triple, weights, features, and calibration mechanics fixed; compare count control against train-only residual groups for hands, count+hands, inning, base_state, and count+base_state.

## Result

- selected Brier: `0.2474712105`
- delta Brier vs control: `0.0`
- competition score: `935.008612259`

## Reason

The count residual control remained best at BSS 935.009. Hand matchup, inning, base_state, and their count interactions all worsened Brier, so none of these 2023 OOT context residuals transfer reliably to 2024.
