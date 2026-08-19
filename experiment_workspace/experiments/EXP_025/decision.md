# EXP_025 decision

- decision: `adopt`
- selected variant: `d6_i400_lr040`
- based on run: `RUN_001`
- comparison basis: `EXP_024`
- reference variant: `extra_w24`
- decided at: `2026-08-17T17:47:15.830737+00:00`

## Ablation

main60과 categorical/affine을 고정하고 iterations와 learning_rate 조합 및 인접 depth만 변경

## Result

- selected Brier: `0.247819028`
- delta Brier vs control: `-1.2929e-06`
- competition score: `795.7740748752`

## Reason

depth6 400 trees lr0.04가 CatBoost 단독 Brier를 0.000001293 개선했으나 전체 최고는 여전히 EXP_024의 24% ExtraTrees 앙상블이다.
