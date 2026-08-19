# 093_late_full_factorial: 후반 이닝과 풀카운트 투수이력 교호항 factorial

- 가설: 두 개선 블록이 서로 다른 행을 겨냥해 결합 시 추가 개선된다.
- control: `same_hand_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `bdffb9d5d4a3`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| late_history | EXP_090 후반 이닝×투수이력 3개 | 0.247501577 | -0.000010289 | 1/1 | 922.853 |
| full_count_history | EXP_092 풀카운트×투수이력 3개 | 0.247507850 | -0.000004017 | 1/1 | 920.341 |
| same_hand_control | control: EXP_084 CPU same-hand pitchmix | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| late_plus_full | 후반 이닝과 풀카운트 교호항 6개 결합 | 0.247534206 | 0.000022339 | 0/1 | 909.791 |

## 실제 변경 필드

- `same_hand_control`: control
- `late_history`: features.custom, features.description, features.expected_count, features.name
- `full_count_history`: features.custom, features.description, features.expected_count, features.name
- `late_plus_full`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/093_late_full_factorial/20260818T072822283239Z_bdffb9d5d4a3`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_092`
- 기준 variant: `full_count_history`
- 검증할 변경: Fix same-hand CPU base; compare late-inning block, full-count block, and their six-feature union.

### same_hand_control

- role: control

### late_history

- declared change: EXP_090 후반 이닝×투수이력 3개
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none

### full_count_history

- declared change: EXP_092 풀카운트×투수이력 3개
- added features: `full_count_x_pitcher_success`, `full_count_x_pitcher_reverse`, `full_count_x_pitcher_middle`
- removed features: none
- model changes: none

### late_plus_full

- declared change: 후반 이닝과 풀카운트 교호항 6개 결합
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`, `full_count_x_pitcher_success`, `full_count_x_pitcher_reverse`, `full_count_x_pitcher_middle`
- removed features: none
- model changes: none
