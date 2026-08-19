# EXP_092 decision

- decision: `adopt`
- selected variant: `full_count_history`
- based on run: `RUN_001`
- comparison basis: `EXP_090`
- reference variant: `late_pitcher_history`
- decided at: `2026-08-18T07:27:34.536427+00:00`

## Ablation

Fix EXP_084 CPU features; add exactly one pressure state by pitcher success/reverse/middle block, then all three blocks.

## Result

- selected Brier: `0.24750785`
- delta Brier vs control: `-4.0167e-06`
- competition score: `920.341485985`

## Reason

풀카운트×투수 성공·반대·가운데 3개만 Brier 0.2475118666→0.2475078500, BSS 918.73→920.34로 개선했다. 2스트라이크·3볼·전체 블록은 채택하지 않는다.
