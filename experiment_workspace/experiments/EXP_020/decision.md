# EXP_020 decision

- decision: `adopt`
- selected variant: `scale106_shift008`
- based on run: `RUN_001`
- comparison basis: `EXP_019`
- reference variant: `batter_team_cat`
- decided at: `2026-08-17T17:04:05.540835+00:00`

## Ablation

batter-team categorical CatBoost와 피처를 고정하고 prediction_scale 및 prediction_shift만 변경

## Result

- selected Brier: `0.2478203209`
- delta Brier vs control: `-1.05214e-05`
- competition score: `795.2564988937`

## Reason

scale 1.06, shift -0.008이 Brier 0.2478203209, BSS 795.256으로 affine 후보 중 최고였고 control보다 0.000010521 개선했다.
