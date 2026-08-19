# EXP_037 decision

- decision: `adopt`
- selected variant: `batter_middle`
- based on run: `RUN_001`
- comparison basis: `EXP_036`
- reference variant: `reverse_short`
- decided at: `2026-08-17T18:41:19.882145+00:00`

## Ablation

main77 reverse-short와 GPU CatBoost를 고정하고 투수 middle, 투수 ball, 타자 middle의 직전·3·5·10 창만 개별·조합 추가

## Result

- selected Brier: `0.2469277855`
- delta Brier vs control: `-9.259e-06`
- competition score: `1152.5465928537`

## Reason

타자 middle 단기 창만 Brier를 0.2469278로 소폭 개선했고 투수 middle·ball 및 전체 조합은 악화
