# 003_custom_features: 선택 제공 41개에 파생 14개를 추가하는 2024 holdout 효과

- 가설: 행 단위 파생 14개가 2024 홀드아웃 Brier를 개선한다.
- control: `selected41_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b35c50f2f176`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| add_custom14 | 행 단위 파생 피처 14개 추가 | 0.248023454 | -0.000113609 | 1/1 | 713.940 |
| selected41_control | control: 선택 제공 피처 41개 | 0.248137064 | 0.000000000 | 0/1 | 668.461 |

## 실제 변경 필드

- `selected41_control`: control
- `add_custom14`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/003_custom_features/20260817T144604284700Z_b35c50f2f176`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_002`
- 기준 variant: `selected41_control`
- 검증할 변경: EXP_002의 main55를 선택 제공 41개와 custom14로 분해해 custom14의 순수 추가 효과를 검증

### selected41_control

- role: control

### add_custom14

- declared change: 행 단위 파생 피처 14개 추가
- added features: `pitcher_gap_prev1_career`, `pitcher_gap_prev3_career`, `pitcher_gap_prev5_career`, `win_expectancy_dist50`, `count_diff`, `count_total`, `same_hand_matchup`, `pressure_x_recent_form`, `runners_x_li`, `batter_success_rate_shrunk`, `reverse_rate_x_li`, `middle_rate_x_count_diff`, `late_inning_x_recent_form`, `offspeed_x_li`
- removed features: none
- model changes: none
