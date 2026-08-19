# EXP_012 decision

- decision: `keep_control`
- selected variant: `default_control`
- based on run: `RUN_001`
- comparison basis: `EXP_011`
- reference variant: `uniform_control`
- decided at: `2026-08-17T16:22:50.948392+00:00`

## Ablation

main55+count, depth6, 300 trees를 고정하고 l2, random_strength, rsm, subsample, border_count를 각각 단일축으로 변경

## Result

- selected Brier: `0.2479681399`
- delta Brier vs control: `0.0`
- competition score: `736.0832056721`

## Reason

l2, random_strength, rsm, subsample, border_count 모든 단일축 규제 변경이 기본 설정보다 악화되어 유지
