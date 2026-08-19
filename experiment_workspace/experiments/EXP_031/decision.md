# EXP_031 decision

- decision: `adopt`
- selected variant: `ensemble_3seed`
- based on run: `RUN_001`
- comparison basis: `EXP_030`
- reference variant: `main60_control`
- decided at: `2026-08-17T18:14:09.348173+00:00`

## Ablation

GPU depth6 600 lr0.025와 main60을 고정하고 3-seed 및 5-seed 확률 평균만 비교

## Result

- selected Brier: `0.2478039438`
- delta Brier vs control: `-1.3604e-05`
- competition score: `801.8123999129`

## Reason

3-seed GPU 평균이 동일 실행 single seed보다 Brier를 0.000013604 개선했고 5-seed보다도 우수했다.
