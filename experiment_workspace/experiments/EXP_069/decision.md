# EXP_069 decision

- decision: `keep_control`
- selected variant: `cpu_d8`
- based on run: `RUN_001`
- comparison basis: `EXP_062`
- reference variant: `extra_w18`
- decided at: `2026-08-18T03:50:08.063879+00:00`

## Ablation

main69와 decay0.85 고정, CPU d8-300 대비 GPU d6-900, d7-600, d8-450 비교

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

GPU 후보 단독은 모두 CPU depth8보다 악화; 다만 GPU d7은 CPU와 오차 다양성이 있어 후속 3모델 앙상블 후보로 보존
