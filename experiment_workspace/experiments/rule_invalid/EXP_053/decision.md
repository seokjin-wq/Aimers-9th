# EXP_053 decision

- decision: `adopt`
- selected variant: `batter_team_middle200`
- based on run: `RUN_001`
- comparison basis: `EXP_050`
- reference variant: `d6_i600`
- decided at: `2026-08-17T20:47:13.114476+00:00`

## Ablation

EXP050 최고 설정을 고정하고 game·pitcher_team·batter_team 기준 recent200 success 또는 middle 한 개만 추가

## Result

- selected Brier: `0.2465509643`
- delta Brier vs control: `-9.67216e-05`
- competition score: `1303.3915964086`

## Reason

batter team recent200 middle 추가가 Brier 0.2465509643, BSS 1303.39로 목표 1300을 최초 달성
