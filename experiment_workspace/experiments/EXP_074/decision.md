# EXP_074 decision

- decision: `keep_control`
- selected variant: `success_k50_control`
- based on run: `RUN_001`
- comparison basis: `EXP_073`
- reference variant: `success_k50`
- decided at: `2026-08-18T04:49:36.964318+00:00`

## Ablation

Diagnose reference-only entity linkage, then compare main69 against linked historical Trackman pitcher aggregates without using any validation-row aggregate.

## Result

- selected Brier: `0.2475295876`
- delta Brier vs control: `0.0`
- competition score: `911.6396980268`

## Reason

익명 투수 연결은 2023 가림 검증에서 불안정해 폐기했고, 안전한 Trackman 상황 집계도 physics BSS 892.48, pitchmix 899.32, all 902.32로 control 911.64보다 모두 악화됐다.
