# EXP_040 decision

- decision: `keep_control`
- selected variant: `cat_single_control`
- based on run: `RUN_002`
- comparison basis: `EXP_039`
- reference variant: `d6_i900`
- decided at: `2026-08-17T19:11:03.196790+00:00`

## Ablation

main85를 고정하고 CatBoost 3-seed 평균과 ExtraTrees min_samples_leaf 5·10·20·50만 비교

## Result

- selected Brier: `0.2468992433`
- delta Brier vs control: `0.0`
- competition score: `1163.9722907547`

## Reason

3-seed와 ExtraTrees 단독이 모두 악화했고 저장 예측의 최적 혼합 상한도 BSS 약 1168로 목표에 부족해 단일 CatBoost 유지
