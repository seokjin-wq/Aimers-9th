# EXP_041 decision

- decision: `adopt`
- selected variant: `bag0`
- based on run: `RUN_001`
- comparison basis: `EXP_040`
- reference variant: `cat_single_control`
- decided at: `2026-08-17T19:16:39.345318+00:00`

## Ablation

main85와 depth6 900 lr0.020을 고정하고 has_time, random_strength 0·0.2·2, bagging_temperature 0만 개별 변경

## Result

- selected Brier: `0.2468662526`
- delta Brier vs control: `-3.4514e-05`
- competition score: `1177.1787912617`

## Reason

bagging_temperature 0만 Brier를 0.2468663, BSS 1177.18로 개선했고 has_time과 random_strength 변경은 모두 악화
