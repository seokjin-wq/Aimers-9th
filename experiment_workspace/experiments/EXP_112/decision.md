# EXP_112 decision

- decision: `adopt`
- selected variant: `history_reliability`
- based on run: `RUN_001`
- comparison basis: `EXP_109`
- reference variant: `subsample_08`
- decided at: `2026-08-18T11:23:10.339834+00:00`

## Ablation

Fix CPU CatBoost subsample=0.8 and main72; add only two categorical history-size buckets, only six numeric reliability features, or both blocks.

## Result

- selected Brier: `0.2474879926`
- delta Brier vs control: `-1.61789e-05`
- competition score: `928.2905828931`

## Reason

Six continuous row-local reliability features improved Brier by 1.618e-05 and BSS by 6.48, while categorical history buckets harmed performance; adopt numeric reliability only.
