# EXP_038 decision

- decision: `adopt`
- selected variant: `plate_context`
- based on run: `RUN_001`
- comparison basis: `EXP_037`
- reference variant: `batter_middle`
- decided at: `2026-08-17T18:45:57.088548+00:00`

## Ablation

main81 최고 피처와 GPU CatBoost를 고정하고 pitcher/batter 행 간격, 바로 전 행 여부, 동일 타석, 타석 내 순번·최근 성공률만 개별·조합 추가

## Result

- selected Brier: `0.246925044`
- delta Brier vs control: `-1.67958e-05`
- competition score: `1153.6440649572`

## Reason

동일 타석 플래그·순번·최근 2·3투구 성공률이 행 간격 전체 조합보다 안정적으로 개선되어 BSS 1153.64 달성
