# EXP_063 decision

- decision: `inconclusive`
- selected variant: `season_pitchmix`
- based on run: `RUN_001`
- comparison basis: `EXP_062`
- reference variant: `extra_w18`
- decided at: `2026-08-18T03:20:37.793559+00:00`

## Ablation

main69 decay85 CatBoost 대비 시즌 pitchmix 3개, prev5 재추가, strike+fastball 재추가, 전체 조합 비교

## Result

- selected Brier: `0.2475347024`
- delta Brier vs control: `-3.0183e-06`
- competition score: `909.592210271`

## Reason

현재 시즌 pitchmix가 Brier 0.000003018만 개선해 실행 변동 수준의 미세 효과이며 원시 제외 피처 재추가는 악화; 전체 최고에는 반영하지 않음
