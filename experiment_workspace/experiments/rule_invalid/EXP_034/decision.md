# EXP_034 decision

- decision: `adopt`
- selected variant: `entity_recent_all`
- based on run: `RUN_001`
- comparison basis: `EXP_033`
- reference variant: `global_control`
- decided at: `2026-08-17T18:28:25.878750+00:00`

## Ablation

GPU CatBoost와 main60을 고정하고 pitcher/batter의 직전 및 최근 3·5·10투구 성공률 파생만 개별·조합 추가

## Result

- selected Brier: `0.247286548`
- delta Brier vs control: `-0.0005325165`
- competition score: `1008.9307075282`

## Reason

투수·타자 직전 및 최근 3·5·10투구 조합이 모든 개별 후보보다 우수하고 BSS를 약 796에서 1009로 개선
