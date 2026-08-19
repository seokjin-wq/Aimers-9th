# EXP_076 decision

- decision: `keep_control`
- selected variant: `main69_control`
- based on run: `RUN_001`
- comparison basis: `EXP_072`
- reference variant: `main69_control`
- decided at: `2026-08-18T04:59:46.196661+00:00`

## Ablation

Fix main69 and CPU d8 decay0.85; add pitcher success/failure counts, pitcher event counts, batter event counts, or all counts.

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

명시적 당해 시즌 로그 사건 횟수는 투수 성공/실패 BSS 902.31, 투수 기타 사건 899.12, 타자 사건 900.82, 전체 889.18로 모두 control 908.38보다 악화됐다.
