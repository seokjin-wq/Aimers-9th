# EXP_070 decision

- decision: `adopt`
- selected variant: `cpu45_gpu40_extra15`
- based on run: `RUN_001`
- comparison basis: `EXP_062`
- reference variant: `extra_w18`
- decided at: `2026-08-18T03:59:19.653970+00:00`

## Ablation

main69 고정 후 CPU/GPU/Extra 비중 40/45/15,45/40/15,40/40/20 비교

## Result

- selected Brier: `0.2474965564`
- delta Brier vs control: `-4.11643e-05`
- competition score: `924.8623884554`

## Reason

CPU45 GPU40 Extra15 3모델 혼합이 CPU 단독 대비 Brier 0.000041164 개선해 BSS 924.862의 새 합법 최고를 기록
