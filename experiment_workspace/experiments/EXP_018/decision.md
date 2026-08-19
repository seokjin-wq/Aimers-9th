# EXP_018 decision

- decision: `keep_control`
- selected variant: `d6_i300_control`
- based on run: `RUN_001`
- comparison basis: `EXP_017`
- reference variant: `all_count_numeric`
- decided at: `2026-08-17T16:50:51.080359+00:00`

## Ablation

main55+count와 -0.010 shift를 고정하고 depth 4~6, iterations 100~400만 변경

## Result

- selected Brier: `0.2478754923`
- delta Brier vs control: `0.0`
- competition score: `773.1709037273`

## Reason

모든 저용량 후보가 control보다 나빴다. depth6 300 trees가 Brier 0.2478754923, BSS 773.171로 계속 최고다.
