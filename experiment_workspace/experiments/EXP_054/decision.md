# EXP_054 decision

- decision: `keep_control`
- selected variant: `extra_w24_safe`
- based on run: `RUN_001`
- comparison basis: `EXP_024`
- reference variant: `extra_w24`
- decided at: `2026-08-18T02:26:09.770564+00:00`

## Ablation

EXP_024 extra_w24를 규칙 준수 엔진에서 재실행하고 CatBoost 단독과 설정 차이를 보존

## Result

- selected Brier: `0.2477775942`
- delta Brier vs control: `0.0`
- competition score: `812.3603933826`

## Reason

규칙 준수 row-local 엔진에서 EXP_024와 Brier 0.2477775942, BSS 812.360393이 완전히 동일하게 재현되어 새 합법 기준선으로 확정
