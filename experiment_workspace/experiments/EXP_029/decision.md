# EXP_029 decision

- decision: `inconclusive`
- selected variant: `all_four`
- based on run: `RUN_001`
- comparison basis: `EXP_028`
- reference variant: `add_scoring_position_x_li`
- decided at: `2026-08-17T18:04:53.031588+00:00`

## Ablation

GPU 모델과 main60을 고정하고 단독 양의 피처 4개의 2-way 및 전체 조합만 비교

## Result

- selected Brier: `0.2478171344`
- delta Brier vs control: `-2.1668e-06`
- competition score: `796.5320853391`

## Reason

all_four가 동일 RUN control보다 0.000002167 개선했지만 GPU 반복 실행 변동보다 작아 결론이 불충분하다. EXP_030 CPU 재검증이 필요하다.
