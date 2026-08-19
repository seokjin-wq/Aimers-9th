# EXP_006 decision

- decision: `keep_control`
- selected variant: `d6_i300_control`
- based on run: `RUN_001`
- comparison basis: `EXP_004`
- reference variant: `native_basic`
- decided at: `2026-08-17T15:54:17.092638+00:00`

## Ablation

main55와 native 기본 3개 범주를 고정하고 CatBoost depth와 iterations 조합만 변경

## Result

- selected Brier: `0.2480092675`
- delta Brier vs control: `0.0`
- competition score: `719.6194426463`

## Reason

모든 600~1000 tree 및 depth5~8 조합이 300-tree control보다 악화되어 현재 용량 유지
