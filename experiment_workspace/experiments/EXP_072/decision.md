# EXP_072 decision

- decision: `keep_control`
- selected variant: `main69_control`
- based on run: `RUN_001`
- comparison basis: `EXP_070`
- reference variant: `cpu45_gpu40_extra15`
- decided at: `2026-08-18T04:34:28.735664+00:00`

## Ablation

Keep EXP_070 model family fixed conceptually and compare main69 against dropping pitcher career, batter career, or both career state blocks.

## Result

- selected Brier: `0.2474960845`
- delta Brier vs control: `0.0`
- competition score: `925.0513192731`

## Reason

투수 통산 제거(BSS 901.85), 타자 통산 제거(919.76), 전체 제거(915.13)가 모두 control(925.05)보다 악화되어 통산 상태와 당해 시즌 상태를 함께 유지한다.
