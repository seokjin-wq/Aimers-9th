# EXP_091 decision

- decision: `inconclusive`
- selected variant: `late_history_triple`
- based on run: `RUN_001`
- comparison basis: `EXP_090`
- reference variant: `late_pitcher_history`
- decided at: `2026-08-18T07:21:26.057842+00:00`

## Ablation

Fix the EXP_087 triple model and compare only the original same-hand features against the EXP_090 late-history feature addition.

## Result

- selected Brier: `0.247478778`
- delta Brier vs control: `-1.8981e-06`
- competition score: `931.9792796746`

## Reason

같은 RUN에서는 late-history triple이 Brier를 0.00000190 개선했지만 GPU 비결정성 변동보다 작고 절대 BSS 931.98은 EXP_088 최고 937.58보다 낮다. CPU 신호는 보존하되 최종 승격은 유보한다.
