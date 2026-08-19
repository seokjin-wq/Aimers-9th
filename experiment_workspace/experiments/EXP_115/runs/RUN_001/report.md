# 115_reliability_situation_factorial: Reliability with situational history interactions

- 가설: The new reliability representation may stabilize previously useful late-inning and full-count pitcher-history interactions, allowing a complementary gain.
- control: `reliability_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `e21d3ee09289`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| reliability_control | control: EXP_112-114 six-feature reliability winner | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| add_both_blocks | add both late-inning and full-count history blocks | 0.247519867 | 0.000031874 | 0/1 | 915.531 |
| add_late_history | add late-inning x pitcher success/reverse/middle only | 0.247538154 | 0.000050162 | 0/1 | 908.210 |
| add_full_count_history | add full-count x pitcher success/reverse/middle only | 0.247572012 | 0.000084019 | 0/1 | 894.657 |

## 실제 변경 필드

- `reliability_control`: control
- `add_late_history`: features.custom, features.description, features.expected_count, features.name
- `add_full_count_history`: features.custom, features.description, features.expected_count, features.name
- `add_both_blocks`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/115_reliability_situation_factorial/20260818T113314095778Z_e21d3ee09289`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_114`
- 기준 variant: `reliability_k100_control`
- 검증할 변경: Fix the EXP_114 CPU model and six reliability features; add only late-inning history, only full-count history, or both three-feature blocks.

### reliability_control

- role: control

### add_late_history

- declared change: add late-inning x pitcher success/reverse/middle only
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none

### add_full_count_history

- declared change: add full-count x pitcher success/reverse/middle only
- added features: `full_count_x_pitcher_success`, `full_count_x_pitcher_reverse`, `full_count_x_pitcher_middle`
- removed features: none
- model changes: none

### add_both_blocks

- declared change: add both late-inning and full-count history blocks
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`, `full_count_x_pitcher_success`, `full_count_x_pitcher_reverse`, `full_count_x_pitcher_middle`
- removed features: none
- model changes: none
