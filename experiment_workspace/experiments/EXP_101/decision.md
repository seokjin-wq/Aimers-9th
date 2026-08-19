# EXP_101 decision

- decision: `adopt`
- selected variant: `catshift_m0095`
- based on run: `RUN_002`
- comparison basis: `EXP_094`
- reference variant: `count_k500_repro`
- decided at: `2026-08-18T09:08:49.019507+00:00`

## Ablation

Keep features, triple weights, component training, and train-only count calibration fixed; compare CatBoost component shifts -0.008, -0.0095, and -0.010.

## Result

- selected Brier: `0.2474629933`
- delta Brier vs control: `-2.1352e-06`
- competition score: `938.2980431539`

## Reason

RUN_001 exposed a blend-cache defect and is retained only as an audit artifact. After fixing raw-probability caching, RUN_002 correctly separated variants: CatBoost shift -0.0095 reduced Brier by 0.000002135 versus the fresh control and reached BSS 938.298, so adopt it as the new compliant best candidate.
