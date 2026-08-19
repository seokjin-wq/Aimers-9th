# EXP_028 decision

- decision: `adopt`
- selected variant: `add_scoring_position_x_li`
- based on run: `RUN_001`
- comparison basis: `EXP_027`
- reference variant: `gpu_d6_i600`
- decided at: `2026-08-17T18:01:17.403104+00:00`

## Ablation

GPU 모델을 고정하고 missing, shrinkage, log-count, context 파생 12개를 각각 하나씩만 추가

## Result

- selected Brier: `0.2478023881`
- delta Brier vs control: `-1.65933e-05`
- competition score: `802.4351751974`

## Reason

scoring_position_x_li 단독 추가가 동일 실행 control 대비 Brier를 0.000016593 낮춰 BSS 802.435로 가장 좋았다. reverse shrinkage와 log LI도 후속 조합 후보로 남긴다.
