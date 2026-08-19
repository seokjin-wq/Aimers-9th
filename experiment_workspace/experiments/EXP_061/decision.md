# EXP_061 decision

- decision: `keep_control`
- selected variant: `common_k20`
- based on run: `RUN_001`
- comparison basis: `EXP_060`
- reference variant: `decay085`
- decided at: `2026-08-18T03:06:34.018526+00:00`

## Ablation

main69 k20 공통 기준 대비 ball k500, strike k200, batter-middle k200을 개별 및 동시 교체

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

단변량 상관 기준의 강한 metric별 스무딩은 tree 모델 Brier에서 모두 악화되어 공통 k20 유지
