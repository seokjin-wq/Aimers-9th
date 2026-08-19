# EXP_051 decision

- decision: `reject`
- selected variant: `control`
- based on run: `RUN_001`
- comparison basis: `EXP_050`
- reference variant: `d6_i600`
- decided at: `2026-08-17T20:30:57.420131+00:00`

## Ablation

EXP050의 main81·CPU d6 i600을 고정하고 global reverse rolling window 50·100·150·200·300만 하나씩 추가

## Result

- selected Brier: `0.2466476858`
- delta Brier vs control: `0.0`
- competition score: `1264.6730738206`

## Reason

global reverse rolling 50~300은 모두 control보다 Brier가 0.0000215 이상 악화되어 추가하지 않음
