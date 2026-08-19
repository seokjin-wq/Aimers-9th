# 029_positive_feature_combinations: EDA 양의 피처 조합

- 가설: 단독 개선된 scoring×LI, reverse shrinkage, log LI, batter missing 일부 조합이 상호 보완적으로 추가 개선한다
- control: `scoring_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `232e880d7a66`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| all_four | 상위 4개 전체 조합 | 0.247817134 | -0.000002167 | 1/1 | 796.532 |
| scoring_control | control: scoring_position_x_li 단독 | 0.247819301 | 0.000000000 | 0/1 | 795.665 |
| scoring_reverse | scoring×LI + reverse shrinkage | 0.247824703 | 0.000005402 | 0/1 | 793.502 |
| scoring_bmissing | scoring×LI + batter missing | 0.247826592 | 0.000007291 | 0/1 | 792.746 |
| scoring_logli | scoring×LI + log LI | 0.247833446 | 0.000014144 | 0/1 | 790.003 |
| scoring_reverse_logli | 상위 3개 조합 | 0.247834110 | 0.000014809 | 0/1 | 789.737 |
| reverse_logli | reverse shrinkage + log LI | 0.247843207 | 0.000023906 | 0/1 | 786.095 |

## 실제 변경 필드

- `scoring_control`: control
- `scoring_reverse`: features.custom, features.description, features.expected_count, features.name
- `scoring_logli`: features.custom, features.description, features.expected_count, features.name
- `scoring_bmissing`: features.custom, features.description, features.expected_count, features.name
- `reverse_logli`: features.custom, features.description, features.expected_count, features.name
- `scoring_reverse_logli`: features.custom, features.description, features.expected_count, features.name
- `all_four`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/029_positive_feature_combinations/20260817T180149673252Z_232e880d7a66`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_028`
- 기준 variant: `add_scoring_position_x_li`
- 검증할 변경: GPU 모델과 main60을 고정하고 단독 양의 피처 4개의 2-way 및 전체 조합만 비교

### scoring_control

- role: control

### scoring_reverse

- declared change: scoring×LI + reverse shrinkage
- added features: `pitcher_reverse_rate_shrunk`
- removed features: none
- model changes: none

### scoring_logli

- declared change: scoring×LI + log LI
- added features: `log1p_li`
- removed features: none
- model changes: none

### scoring_bmissing

- declared change: scoring×LI + batter missing
- added features: `batter_history_missing`
- removed features: none
- model changes: none

### reverse_logli

- declared change: reverse shrinkage + log LI
- added features: `pitcher_reverse_rate_shrunk`, `log1p_li`
- removed features: `scoring_position_x_li`
- model changes: none

### scoring_reverse_logli

- declared change: 상위 3개 조합
- added features: `pitcher_reverse_rate_shrunk`, `log1p_li`
- removed features: none
- model changes: none

### all_four

- declared change: 상위 4개 전체 조합
- added features: `pitcher_reverse_rate_shrunk`, `log1p_li`, `batter_history_missing`
- removed features: none
- model changes: none
