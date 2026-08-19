# EXP_044 decision

- decision: `keep_control`
- selected variant: `main77_control`
- based on run: `RUN_001`
- comparison basis: `EXP_043`
- reference variant: `main77_reverse`
- decided at: `2026-08-17T19:34:40.137915+00:00`

## Ablation

CPU depth6 400 lr0.04와 reverse short를 고정하고 투수 recent20·30·50 및 타자 recent2·8 포함 여부만 변경

## Result

- selected Brier: `0.2469381307`
- delta Brier vs control: `0.0`
- competition score: `1148.405347731`

## Reason

타자 2·8 또는 투수 20·30·50 일부를 제거한 모든 CPU 후보가 악화되어 main77 전체 창 유지
