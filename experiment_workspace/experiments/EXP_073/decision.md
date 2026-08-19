# EXP_073 decision

- decision: `adopt`
- selected variant: `success_k50`
- based on run: `RUN_001`
- comparison basis: `EXP_072`
- reference variant: `main69_control`
- decided at: `2026-08-18T04:39:26.461346+00:00`

## Ablation

Fix main69 and CPU CatBoost d8 decay0.85; replace only pitcher/batter current-season success smoothing k among 5,10,20,50,100.

## Result

- selected Brier: `0.2475295876`
- delta Brier vs control: `-8.1331e-06`
- competition score: `911.6396980268`

## Reason

k=50이 CPU CatBoost Brier를 0.00000813 낮춰 BSS 908.38→911.64로 개선했다. 이후 앙상블 승격 검증 전까지 유망 component로 채택한다.
