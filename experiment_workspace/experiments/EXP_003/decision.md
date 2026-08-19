# EXP_003 decision

- decision: `adopt`
- selected variant: `add_custom14`
- based on run: `RUN_001`
- comparison basis: `EXP_002`
- reference variant: `selected41_control`
- decided at: `2026-08-17T15:11:53.756554+00:00`

## Ablation

EXP_002의 main55를 선택 제공 41개와 custom14로 분해해 custom14의 순수 추가 효과를 검증

## Result

- selected Brier: `0.2480234544`
- delta Brier vs control: `-0.0001136094`
- competition score: `713.9403046936`

## Reason

custom14 추가가 selected41 대비 2024 홀드아웃 Brier를 0.000113609 개선해 채택
