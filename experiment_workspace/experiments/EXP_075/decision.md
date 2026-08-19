# EXP_075 decision

- decision: `adopt`
- selected variant: `both_k50`
- based on run: `RUN_001`
- comparison basis: `EXP_073`
- reference variant: `success_k50`
- decided at: `2026-08-18T04:53:44.148299+00:00`

## Ablation

Fix all else and compare k20/k20, pitcher50/batter20, pitcher20/batter50, and k50/k50.

## Result

- selected Brier: `0.2475295876`
- delta Brier vs control: `-8.1331e-06`
- competition score: `911.6396980268`

## Reason

투수 또는 타자 단독 k50은 악화됐지만 두 성공률을 함께 k50으로 바꾸면 Brier가 0.00000813 개선됐다. 효과가 작으므로 앙상블 승격에서 재검증하는 조건부 후보로 채택한다.
