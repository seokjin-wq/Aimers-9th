# EXP_010 decision

- decision: `keep_control`
- selected variant: `main55_control`
- based on run: `RUN_001`
- comparison basis: `EXP_009`
- reference variant: `main55_control`
- decided at: `2026-08-17T16:12:04.124968+00:00`

## Ablation

main55를 기준으로 누수 없는 시즌 전체 prior, 직전 시즌 투수, 투수·타자, 선수·팀 타깃 이력을 단계적으로 추가

## Result

- selected Brier: `0.2480092675`
- delta Brier vs control: `0.0`
- competition score: `719.6194426463`

## Reason

이전 시즌 선수·팀 타깃 집계와 시즌 prior가 모두 main55보다 크게 악화되어 제거
