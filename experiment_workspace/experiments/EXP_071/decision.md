# EXP_071 decision

- decision: `keep_control`
- selected variant: `batter_team_control`
- based on run: `RUN_001`
- comparison basis: `EXP_070`
- reference variant: `cpu45_gpu40_extra15`
- decided at: `2026-08-18T04:05:41.011706+00:00`

## Ablation

main69 decay85에서 pitcher, batter, 둘 다, pitcher+양팀 categorical만 변경

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

현재 시즌 상태 이후에도 pitcher/batter ID native categorical은 모두 악화되어 고카디널리티 ID 범주화를 사용하지 않음
