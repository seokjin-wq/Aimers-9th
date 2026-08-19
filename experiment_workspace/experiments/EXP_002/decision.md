# EXP_002 decision

- decision: `keep_control`
- selected variant: `main55_control`
- based on run: `RUN_001`
- comparison basis: `BASELINE_001_main55`
- reference variant: `main55_control`
- decided at: `2026-08-17T15:11:53.034315+00:00`

## Ablation

main55 대비 달력·상태·context 피처 묶음을 각각 제거해 기여도를 검증

## Result

- selected Brier: `0.2480234544`
- delta Brier vs control: `0.0`
- competition score: `713.9403046936`

## Reason

drop_state가 Brier를 0.000009858 개선했지만 실질적 동률 기준 0.00001 미만이고 단일 2024 홀드아웃 결과이므로 main55를 유지
