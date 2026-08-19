# EXP_057 decision

- decision: `adopt`
- selected variant: `extra_w24`
- based on run: `RUN_001`
- comparison basis: `EXP_056`
- reference variant: `pitcher_batter_season_all`
- decided at: `2026-08-18T02:44:16.618588+00:00`

## Ablation

main69 피처를 고정하고 CatBoost 단독 대비 ExtraTrees 가중치 15,20,24,28,32%만 변경

## Result

- selected Brier: `0.2475567595`
- delta Brier vs control: `-4.25086e-05`
- competition score: `900.7625488221`

## Reason

main69 시즌 상태 피처에서도 ExtraTrees 24% 혼합이 CatBoost 대비 Brier 0.000042509 개선해 BSS 900.763의 새 합법 최고를 기록
