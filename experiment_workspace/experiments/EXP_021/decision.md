# EXP_021 decision

- decision: `keep_control`
- selected variant: `main60_control`
- based on run: `RUN_001`
- comparison basis: `EXP_020`
- reference variant: `scale106_shift008`
- decided at: `2026-08-17T17:08:08.450163+00:00`

## Ablation

최고 모델을 고정하고 row_id 숫자부로 계산한 시즌 내 투구 순번, 정규화 진행도, 구간 피처만 추가

## Result

- selected Brier: `0.2478203209`
- delta Brier vs control: `0.0`
- competition score: `795.2564988937`

## Reason

시즌 내 투구 순번, 진행도, 구간 표현이 모두 control보다 악화했다. row-order 피처는 채택하지 않고 BSS 795.256 기준을 유지한다.
