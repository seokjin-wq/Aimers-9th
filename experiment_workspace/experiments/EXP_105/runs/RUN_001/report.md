# 105_official_train_context_effects: Official-train context target effects

- 가설: Season-OOF context target effects fitted only on official training seasons provide stable nonlinear priors that CatBoost cannot recover efficiently from raw count, hand, inning, and base-state columns alone.
- control: `same_pitchmix_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `5076f16b3fe5`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| same_pitchmix_control | control: current CPU main72 | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| pressure_effect | add season-OOF official-train inning x count x outs x runners target effect | 0.247521906 | 0.000010039 | 0/1 | 914.715 |
| count_hands_effect | add season-OOF official-train count x hands target effect | 0.247530101 | 0.000018235 | 0/1 | 911.434 |
| count_out_base_effect | add season-OOF official-train count x outs x base target effect | 0.247549855 | 0.000037989 | 0/1 | 903.526 |
| all_context_effects | add all four season-OOF official-train context target effects | 0.247892507 | 0.000380640 | 0/1 | 766.360 |
| inning_game_effect | add season-OOF official-train inning x half x game-type target effect | 0.247911566 | 0.000399700 | 0/1 | 758.730 |

## 실제 변경 필드

- `same_pitchmix_control`: control
- `count_hands_effect`: features.custom, features.description, features.expected_count, features.name
- `count_out_base_effect`: features.custom, features.description, features.expected_count, features.name
- `inning_game_effect`: features.custom, features.description, features.expected_count, features.name
- `pressure_effect`: features.custom, features.description, features.expected_count, features.name
- `all_context_effects`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/105_official_train_context_effects/20260818T095006783374Z_5076f16b3fe5`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_095`
- 기준 variant: `all_three`
- 검증할 변경: Keep latest CPU CatBoost and main72 fixed; add one safe official-train context target-effect feature at a time and then all four together.

### same_pitchmix_control

- role: control

### count_hands_effect

- declared change: add season-OOF official-train count x hands target effect
- added features: `count_hands_target_effect`
- removed features: none
- model changes: none

### count_out_base_effect

- declared change: add season-OOF official-train count x outs x base target effect
- added features: `count_out_base_target_effect`
- removed features: none
- model changes: none

### inning_game_effect

- declared change: add season-OOF official-train inning x half x game-type target effect
- added features: `inning_game_target_effect`
- removed features: none
- model changes: none

### pressure_effect

- declared change: add season-OOF official-train inning x count x outs x runners target effect
- added features: `pressure_state_target_effect`
- removed features: none
- model changes: none

### all_context_effects

- declared change: add all four season-OOF official-train context target effects
- added features: `count_hands_target_effect`, `count_out_base_target_effect`, `inning_game_target_effect`, `pressure_state_target_effect`
- removed features: none
- model changes: none
