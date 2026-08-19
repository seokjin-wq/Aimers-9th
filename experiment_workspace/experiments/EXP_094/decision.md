# EXP_094 decision

- decision: `adopt`
- selected variant: `count_k500_repro`
- based on run: `RUN_001`
- comparison basis: `EXP_088`
- reference variant: `count_k500`
- decided at: `2026-08-18T07:45:43.363878+00:00`

## Ablation

Freshly rerun the identical triple control, count k500, and count k2000 settings; no feature or parameter search.

## Result

- selected Brier: `0.2474650303`
- delta Brier vs control: `-7.0662e-06`
- competition score: `937.482591475`

## Reason

fresh GPU run에서도 count k500이 Brier 0.2474720965→0.2474650303, BSS 934.65→937.48로 개선해 EXP_088의 +2.80 BSS를 재현했다. k500을 안정적인 현재 최고 보정으로 확정한다.
