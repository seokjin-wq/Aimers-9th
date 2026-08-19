# EXP_009 decision

- decision: `keep_control`
- selected variant: `count_control`
- based on run: `RUN_001`
- comparison basis: `EXP_008`
- reference variant: `add_count_state`
- decided at: `2026-08-17T16:07:27.376393+00:00`

## Ablation

main55+count를 기준으로 스무딩과 결측 플래그의 pairwise 및 전체 조합 효과를 비교

## Result

- selected Brier: `0.2479681399`
- delta Brier vs control: `0.0`
- competition score: `736.0832056721`

## Reason

개별 개선 피처를 조합한 모든 variant가 카운트 단일 묶음보다 악화되어 count_control 유지
