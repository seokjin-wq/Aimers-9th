# EXP_089 decision

- decision: `reject`
- selected variant: `same_hand_control`
- based on run: `RUN_001`
- comparison basis: `EXP_087`
- reference variant: `same_hand_pitchmix_triple`
- decided at: `2026-08-18T06:59:33.188806+00:00`

## Ablation

Fix EXP_084 CPU base; add safe numeric season pitch index, coarse phase, or both. Training starts come from official train; validation start comes from the last official reference row; TEST suffix is used row-locally.

## Result

- selected Brier: `0.2475118666`
- delta Brier vs control: `0.0`
- competition score: `918.7335789118`

## Reason

안전한 시즌 index와 phase가 모두 control BSS 918.73보다 크게 낮았다. 일정·행밀도 차이로 연도 간 일반화되지 않아 사용하지 않는다.
