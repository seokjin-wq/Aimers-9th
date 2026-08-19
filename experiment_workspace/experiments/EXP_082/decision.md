# EXP_082 decision

- decision: `keep_control`
- selected variant: `count_hands_control`
- based on run: `RUN_001`
- comparison basis: `EXP_080`
- reference variant: `count_hands_promoted`
- decided at: `2026-08-18T05:47:34.475230+00:00`

## Ablation

Fix EXP_078 count+hands categories; add exactly one adjacent low-cardinality categorical block at a time.

## Result

- selected Brier: `0.2475158585`
- delta Brier vs control: `0.0`
- competition score: `917.135588661`

## Reason

모든 추가 범주가 control Brier 0.2475158585를 악화했다. 평가는 행 독립이며 추가 범주는 채택하지 않는다.
