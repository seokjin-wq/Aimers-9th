# EXP_064 decision

- decision: `reject`
- selected variant: `main69_control`
- based on run: `RUN_001`
- comparison basis: `EXP_062`
- reference variant: `extra_w18`
- decided at: `2026-08-18T03:27:15.223979+00:00`

## Ablation

main69 decay85 대비 count×hands, count×out×base, inning/game+pressure, 전체 네 효과를 비교

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

상황 TE의 행별 LOO 미세차가 자기 정답 지문으로 작동해 극단 확률 과적합 발생; 모든 후보 기각하고 season-OOF 방식으로 재설계
