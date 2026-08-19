# EXP_068 decision

- decision: `inconclusive`
- selected variant: `track_physics`
- based on run: `RUN_001`
- comparison basis: `EXP_062`
- reference variant: `extra_w18`
- decided at: `2026-08-18T03:46:26.345060+00:00`

## Ablation

main69 decay85 대비 Trackman 물리 6개, 구종비율 3개, 전체 9개를 season-OOF 방식으로 추가

## Result

- selected Brier: `0.247535912`
- delta Brier vs control: `-1.8087e-06`
- competition score: `909.1080086037`

## Reason

공식 Trackman 물리 통계는 Brier 0.000001809만 개선해 실질적 동률이고 구종 비율은 악화; 전체 최고에는 반영하지 않음
