# EXP_005 decision

- decision: `keep_control`
- selected variant: `basic3_control`
- based on run: `RUN_001`
- comparison basis: `EXP_004`
- reference variant: `native_basic`
- decided at: `2026-08-17T15:43:24.215623+00:00`

## Ablation

CatBoost native 모델을 고정하고 범주로 지정하는 컬럼 범위만 basic3, 선수 ID, 선수·팀·손, 전체 이산으로 확대

## Result

- selected Brier: `0.2480092675`
- delta Brier vs control: `0.0`
- competition score: `719.6194426463`

## Reason

선수·팀·이산값을 범주로 확장한 모든 variant가 악화되어 문자열 기본 3개 범주만 유지
