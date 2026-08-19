# EXP_077 decision

- decision: `keep_control`
- selected variant: `logloss_d8_control`
- based on run: `RUN_001`
- comparison basis: `EXP_072`
- reference variant: `main69_control`
- decided at: `2026-08-18T05:05:32.701692+00:00`

## Ablation

Fix main69; compare Logloss d8 against RMSE d7/d8 and affine-scaled RMSE d8, all with season decay 0.85.

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

RMSE 회귀는 affine 보정한 depth8도 BSS 897.45로 Logloss 908.38보다 낮았고, 나머지 RMSE 후보는 857~864로 더 악화됐다.
