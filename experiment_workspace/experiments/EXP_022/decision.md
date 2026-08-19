# EXP_022 decision

- decision: `keep_control`
- selected variant: `default_control`
- based on run: `RUN_002`
- comparison basis: `EXP_021`
- reference variant: `main60_control`
- decided at: `2026-08-17T17:19:52.896946+00:00`

## Ablation

최고 피처와 affine 보정을 고정하고 bootstrap_type, boosting_type, grow_policy, leaf estimation만 한 종류씩 변경

## Result

- selected Brier: `0.2478203209`
- delta Brier vs control: `0.0`
- competition score: `795.2564988937`

## Reason

Ordered boosting은 장시간 정체로 제외하고 RUN_002에서 나머지 8개를 재검증했다. no-bootstrap이 근접했지만 모든 후보가 control보다 나빠 BSS 795.256 기준을 유지한다.
