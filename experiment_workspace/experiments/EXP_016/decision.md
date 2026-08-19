# EXP_016 decision

- decision: `keep_control`
- selected variant: `single_seed_control`
- based on run: `RUN_001`
- comparison basis: `EXP_015`
- reference variant: `shift_m010`
- decided at: `2026-08-17T16:39:46.483126+00:00`

## Ablation

main55+count와 -0.010 shift를 고정하고 단일 seed 대비 3-seed, 5-seed 확률 평균만 비교

## Result

- selected Brier: `0.2478754923`
- delta Brier vs control: `0.0`
- competition score: `773.1709037273`

## Reason

3-seed와 5-seed 평균이 단일 seed42보다 악화되어 계산비용이 낮고 성능이 높은 단일 모델 유지
