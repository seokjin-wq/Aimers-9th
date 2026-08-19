# EXP_039 decision

- decision: `adopt`
- selected variant: `d6_i900`
- based on run: `RUN_001`
- comparison basis: `EXP_038`
- reference variant: `plate_context`
- decided at: `2026-08-17T18:50:17.555600+00:00`

## Ablation

main85와 affine 보정을 고정하고 GPU CatBoost depth 5~8, iterations 450~900, learning_rate 경로만 변경

## Result

- selected Brier: `0.2468999017`
- delta Brier vs control: `-3.09593e-05`
- competition score: `1163.7087429419`

## Reason

main85에서 depth6 900 lr0.020이 Brier 0.2468999, BSS 1163.71로 깊이 5·7·8 후보보다 우수
