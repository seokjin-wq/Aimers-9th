# EXP_055 decision

- decision: `reject`
- selected variant: `main60_control`
- based on run: `RUN_001`
- comparison basis: `EXP_054`
- reference variant: `extra_w24_safe`
- decided at: `2026-08-18T02:32:01.527199+00:00`

## Ablation

main60 CatBoost를 고정하고 official-train-only 투수 TE, 투수+타자 TE, 투수+타자+팀 TE만 단계적으로 추가

## Result

- selected Brier: `0.2478203209`
- delta Brier vs control: `0.0`
- competition score: `795.2564988937`

## Reason

공식 학습 전용 구현과 불변성은 충족했지만 투수 효과의 train 상관 0.0916이 2024에서 0.0283으로 붕괴해 과적합했고 모든 TE 후보가 크게 악화; 후속 기준에 사용하지 않음
