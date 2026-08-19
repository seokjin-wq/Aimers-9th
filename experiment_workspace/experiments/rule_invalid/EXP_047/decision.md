# EXP_047 decision

- decision: `adopt`
- selected variant: `global100`
- based on run: `RUN_001`
- comparison basis: `EXP_046`
- reference variant: `cat_control`
- decided at: `2026-08-17T19:58:19.553954+00:00`

## Ablation

CPU main80을 고정하고 복원 가능한 과거 전역 성공의 recent5·10·20·50·100 rolling만 개별·조합 추가

## Result

- selected Brier: `0.2467254968`
- delta Brier vs control: `-0.0002048483`
- competition score: `1233.5246181931`

## Reason

전역 recent100 단독이 Brier 0.2467255, BSS 1233.52로 큰 폭 개선했고 다중 창 조합보다 우수
