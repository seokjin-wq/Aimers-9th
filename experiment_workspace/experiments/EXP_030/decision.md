# EXP_030 decision

- decision: `keep_control`
- selected variant: `main60_control`
- based on run: `RUN_001`
- comparison basis: `EXP_029`
- reference variant: `all_four`
- decided at: `2026-08-17T18:10:04.874551+00:00`

## Ablation

CPU depth6 400 lr0.04를 고정하고 scoring×LI, reverse shrinkage, log LI, batter missing, all-four를 다시 비교

## Result

- selected Brier: `0.247819028`
- delta Brier vs control: `0.0`
- competition score: `795.7740748752`

## Reason

GPU에서 양의 효과를 보인 네 피처가 결정론적 CPU에서는 모두 악화했다. GPU 변동에 의한 false positive로 판정하고 main60을 유지한다.
