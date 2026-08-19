# EXP_052 decision

- decision: `inconclusive`
- selected variant: `best_replay`
- based on run: `RUN_001`
- comparison basis: `EXP_050`
- reference variant: `d6_i600`
- decided at: `2026-08-17T20:34:07.132856+00:00`

## Ablation

EXP050 최고 설정을 그대로 1회 재현하고 2024 row별 예측을 저장하여 affine 보정 가능 범위를 진단

## Result

- selected Brier: `0.2466476858`
- delta Brier vs control: `0.0`
- competition score: `1264.6730738206`

## Reason

2024 직접 affine 최적화의 이론상 상한이 BSS 1267.43(+2.76)에 그치고 반기별 최적값도 불안정하여 단독 채택하지 않음
