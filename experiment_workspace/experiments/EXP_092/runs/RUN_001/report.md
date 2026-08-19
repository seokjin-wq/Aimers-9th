# 092_count_pressure_history: 카운트 압박 상태와 투수 과거 제구 이력 교호항

- 가설: 카운트별 잔차는 투수 이력의 효과 기울기가 압박 상태마다 달라서 남는다.
- control: `same_hand_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `206feb626d5e`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| full_count_history | 풀카운트×투수 성공·반대·가운데 이력 3개 | 0.247507850 | -0.000004017 | 1/1 | 920.341 |
| same_hand_control | control: EXP_084 CPU same-hand pitchmix | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| two_strike_history | 2스트라이크×투수 성공·반대·가운데 이력 3개 | 0.247511927 | 0.000000060 | 0/1 | 918.710 |
| all_pressure_history | 세 압박 상태의 9개 교호항 모두 추가 | 0.247530038 | 0.000018172 | 0/1 | 911.459 |
| three_ball_history | 3볼×투수 성공·반대·가운데 이력 3개 | 0.247542136 | 0.000030269 | 0/1 | 906.617 |

## 실제 변경 필드

- `same_hand_control`: control
- `two_strike_history`: features.custom, features.description, features.expected_count, features.name
- `three_ball_history`: features.custom, features.description, features.expected_count, features.name
- `full_count_history`: features.custom, features.description, features.expected_count, features.name
- `all_pressure_history`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/092_count_pressure_history/20260818T072240969039Z_206feb626d5e`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_090`
- 기준 variant: `late_pitcher_history`
- 검증할 변경: Fix EXP_084 CPU features; add exactly one pressure state by pitcher success/reverse/middle block, then all three blocks.

### same_hand_control

- role: control

### two_strike_history

- declared change: 2스트라이크×투수 성공·반대·가운데 이력 3개
- added features: `two_strike_x_pitcher_success`, `two_strike_x_pitcher_reverse`, `two_strike_x_pitcher_middle`
- removed features: none
- model changes: none

### three_ball_history

- declared change: 3볼×투수 성공·반대·가운데 이력 3개
- added features: `three_ball_x_pitcher_success`, `three_ball_x_pitcher_reverse`, `three_ball_x_pitcher_middle`
- removed features: none
- model changes: none

### full_count_history

- declared change: 풀카운트×투수 성공·반대·가운데 이력 3개
- added features: `full_count_x_pitcher_success`, `full_count_x_pitcher_reverse`, `full_count_x_pitcher_middle`
- removed features: none
- model changes: none

### all_pressure_history

- declared change: 세 압박 상태의 9개 교호항 모두 추가
- added features: `two_strike_x_pitcher_success`, `two_strike_x_pitcher_reverse`, `two_strike_x_pitcher_middle`, `three_ball_x_pitcher_success`, `three_ball_x_pitcher_reverse`, `three_ball_x_pitcher_middle`, `full_count_x_pitcher_success`, `full_count_x_pitcher_reverse`, `full_count_x_pitcher_middle`
- removed features: none
- model changes: none
