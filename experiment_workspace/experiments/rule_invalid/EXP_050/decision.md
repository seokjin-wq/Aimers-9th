# EXP_050 decision

- decision: `adopt`
- selected variant: `d6_i600`
- based on run: `RUN_001`
- comparison basis: `EXP_049`
- reference variant: `global200_control`
- decided at: `2026-08-17T20:20:57.696253+00:00`

## Ablation

main81 global200과 affine을 고정하고 CPU CatBoost depth5~8, iterations300~800, learning_rate0.02~0.04만 변경

## Result

- selected Brier: `0.2466476858`
- delta Brier vs control: `-4.95603e-05`
- competition score: `1264.6730738206`

## Reason

depth6 600 lr0.03이 Brier 0.2466476858, BSS 1264.67로 control 대비 개선
