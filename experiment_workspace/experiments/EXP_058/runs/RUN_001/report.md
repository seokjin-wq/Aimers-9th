# 058_season_form_deltas: 시즌·커리어·최근 폼 차이

- 가설: 현재 시즌 수준과 커리어·최근 1/3/5경기 수준의 차이를 명시하면 CatBoost가 폼 변화 방향을 더 안정적으로 학습한다
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `84ebcda9ab49`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main69_control | control: EXP_056 최고 CatBoost 피처 | 0.247599268 | 0.000000000 | 0/1 | 883.746 |
| recent_form_deltas | 직전1-3, 직전3-5, 직전3-현재시즌 성공률 delta 추가 | 0.247600592 | 0.000001324 | 0/1 | 883.216 |
| season_career_deltas | 투수 5종·타자 2종 현재 시즌 minus 커리어 delta 추가 | 0.247632524 | 0.000033256 | 0/1 | 870.433 |
| all_deltas | 시즌-커리어 7개와 최근폼 3개 delta를 모두 추가 | 0.247655909 | 0.000056641 | 0/1 | 861.072 |

## 실제 변경 필드

- `main69_control`: control
- `season_career_deltas`: features.custom, features.description, features.expected_count, features.name
- `recent_form_deltas`: features.custom, features.description, features.expected_count, features.name
- `all_deltas`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/058_season_form_deltas/20260818T024542508158Z_84ebcda9ab49`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_057`
- 기준 variant: `extra_w24`
- 검증할 변경: main69 CatBoost 대비 시즌-커리어 delta 7개, 최근폼 delta 3개, 전체 10개를 비교

### main69_control

- role: control

### season_career_deltas

- declared change: 투수 5종·타자 2종 현재 시즌 minus 커리어 delta 추가
- added features: `pitcher_season_success_delta_career`, `pitcher_season_reverse_delta_career`, `pitcher_season_middle_delta_career`, `pitcher_season_ball_delta_career`, `pitcher_season_strike_delta_career`, `batter_season_success_delta_career`, `batter_season_middle_delta_career`
- removed features: none
- model changes: none

### recent_form_deltas

- declared change: 직전1-3, 직전3-5, 직전3-현재시즌 성공률 delta 추가
- added features: `pitcher_prev1_minus_prev3`, `pitcher_prev3_minus_prev5`, `pitcher_prev3_minus_season_success`
- removed features: none
- model changes: none

### all_deltas

- declared change: 시즌-커리어 7개와 최근폼 3개 delta를 모두 추가
- added features: `pitcher_season_success_delta_career`, `pitcher_season_reverse_delta_career`, `pitcher_season_middle_delta_career`, `pitcher_season_ball_delta_career`, `pitcher_season_strike_delta_career`, `batter_season_success_delta_career`, `batter_season_middle_delta_career`, `pitcher_prev1_minus_prev3`, `pitcher_prev3_minus_prev5`, `pitcher_prev3_minus_season_success`
- removed features: none
- model changes: none
