# EXP_062 decision

- decision: `adopt`
- selected variant: `extra_w18`
- based on run: `RUN_001`
- comparison basis: `EXP_060`
- reference variant: `decay085`
- decided at: `2026-08-18T03:14:37.413078+00:00`

## Ablation

main69 고정, depth8 decay0.85 CatBoost 단독 대비 ExtraTrees 18,24,30% 혼합

## Result

- selected Brier: `0.247515025`
- delta Brier vs control: `-2.26958e-05`
- competition score: `917.469272769`

## Reason

depth8 decay0.85 CatBoost에 ExtraTrees 18% 혼합이 Brier를 0.000022696 추가 개선해 BSS 917.469의 새 합법 최고를 기록
