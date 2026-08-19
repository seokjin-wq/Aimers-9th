# EXP_056 decision

- decision: `adopt`
- selected variant: `pitcher_batter_season_all`
- based on run: `RUN_001`
- comparison basis: `EXP_054`
- reference variant: `extra_w24_safe`
- decided at: `2026-08-18T02:37:00.068239+00:00`

## Ablation

main60 CatBoost 대비 투수 시즌 성공+n, 투수 시즌 전체 상태, 투수+타자 시즌 전체 상태를 단계적으로 추가

## Result

- selected Brier: `0.2475992681`
- delta Brier vs control: `-0.0002210528`
- competition score: `883.7459693801`

## Reason

공식 학습 종료 스냅샷+현재 한 행만으로 계산한 투수·타자 시즌 상태가 Brier를 0.000221053 개선해 BSS 883.746으로 새 CatBoost 최고를 기록
