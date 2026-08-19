# EXP_111 decision

- decision: `adopt`
- selected variant: `triple_cpu_sub08`
- based on run: `RUN_001`
- comparison basis: `EXP_101`
- reference variant: `catshift_m0095`
- decided at: `2026-08-18T11:15:27.544542+00:00`

## Ablation

Keep main72 features, GPU CatBoost, ExtraTrees, 45/40/15 weights, count residual correction k=500, scales, and shifts fixed; change only CPU CatBoost subsample from 0.7 to 0.8.

## Result

- selected Brier: `0.2474586792`
- delta Brier vs control: `-4.0236e-06`
- competition score: `940.0250056598`

## Reason

Replacing only CPU subsample 0.7 with 0.8 improved same-run corrected triple Brier by 4.024e-06 and set a new compliant best BSS 940.025.
