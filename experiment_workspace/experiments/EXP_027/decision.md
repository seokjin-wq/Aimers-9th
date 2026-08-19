# EXP_027 decision

- decision: `adopt`
- selected variant: `gpu_d6_i600`
- based on run: `RUN_001`
- comparison basis: `EXP_026`
- reference variant: `count_k500`
- decided at: `2026-08-17T17:54:57.071831+00:00`

## Ablation

main60과 affine을 고정하고 GPU depth 6~8, iterations 300~600, learning rate 0.025~0.05를 비교

## Result

- selected Brier: `0.2478158368`
- delta Brier vs control: `-3.1912e-06`
- competition score: `797.0515383172`

## Reason

GPU depth6 600 lr0.025가 Brier 0.2478158368로 CPU component보다 0.000003191 개선했고, 저장된 예측을 다음 앙상블 진단에 사용한다.
