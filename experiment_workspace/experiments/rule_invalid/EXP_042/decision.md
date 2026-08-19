# EXP_042 decision

- decision: `inconclusive`
- selected variant: `batter_lags`
- based on run: `RUN_001`
- comparison basis: `EXP_041`
- reference variant: `bag0`
- decided at: `2026-08-17T19:23:04.769274+00:00`

## Ablation

main85와 bag0 CatBoost를 고정하고 투수 lag2·3·5, 타자 lag2·3 및 최근 3개 이진 패턴만 개별·조합 추가

## Result

- selected Brier: `0.2468635714`
- delta Brier vs control: `-1.93809e-05`
- competition score: `1178.2521161039`

## Reason

타자 lag2·3이 같은 실행 최선이지만 개선폭 1.94e-5가 GPU 비결정성 범위와 비슷해 CPU 재검증 필요
