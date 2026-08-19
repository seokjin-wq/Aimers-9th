# EXP_080 decision

- decision: `adopt`
- selected variant: `count_hands_promoted`
- based on run: `RUN_001`
- comparison basis: `EXP_072`
- reference variant: `main69_control`
- decided at: `2026-08-18T05:30:46.016512+00:00`

## Ablation

Fix triple CPU45/GPU40/Extra15; compare old main69 against only the count+both-hands categorical treatment.

## Result

- selected Brier: `0.2474938057`
- delta Brier vs control: `-2.9411e-06`
- competition score: `925.9635540971`

## Reason

3모델 앙상블에서도 count+양손 categorical이 Brier를 0.00000294 낮춰 BSS 924.79→925.96으로 개선되어 새로운 전체 최고로 채택한다.
