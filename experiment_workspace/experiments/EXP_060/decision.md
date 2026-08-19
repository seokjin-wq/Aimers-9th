# EXP_060 decision

- decision: `adopt`
- selected variant: `decay085`
- based on run: `RUN_001`
- comparison basis: `EXP_059`
- reference variant: `d8_i300`
- decided at: `2026-08-18T03:00:36.440519+00:00`

## Ablation

main69 depth8을 고정하고 시즌당 sample weight decay 1.0, 0.95, 0.90, 0.85, 0.75만 변경

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `-3.00274e-05`
- competition score: `908.3839506927`

## Reason

main69 depth8에서 시즌당 0.85 가중이 균등 대비 Brier 0.000030027 개선해 BSS 908.384의 새 합법 최고를 기록
