# 030_cpu_feature_confirmation: EDA 상위 피처 CPU 재검증

- 가설: GPU 스크리닝에서 양의 효과를 보인 피처가 결정론적 CPU CatBoost에서도 control보다 개선한다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `6f2547f215d2`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main60_control | control: CPU main60 | 0.247819028 | 0.000000000 | 0/1 | 795.774 |
| log_li | log1p_li 단독 | 0.247823958 | 0.000004930 | 0/1 | 793.800 |
| reverse_shrunk | pitcher_reverse_rate_shrunk 단독 | 0.247828816 | 0.000009788 | 0/1 | 791.856 |
| scoring_x_li | scoring_position_x_li 단독 | 0.247831941 | 0.000012913 | 0/1 | 790.605 |
| batter_missing | batter_history_missing 단독 | 0.247852493 | 0.000033465 | 0/1 | 782.378 |
| all_four | 상위 4개 전체 | 0.247866464 | 0.000047436 | 0/1 | 776.785 |

## 실제 변경 필드

- `main60_control`: control
- `scoring_x_li`: features.custom, features.description, features.expected_count, features.name
- `reverse_shrunk`: features.custom, features.description, features.expected_count, features.name
- `log_li`: features.custom, features.description, features.expected_count, features.name
- `batter_missing`: features.custom, features.description, features.expected_count, features.name
- `all_four`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/030_cpu_feature_confirmation/20260817T180511794213Z_6f2547f215d2`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_029`
- 기준 variant: `all_four`
- 검증할 변경: CPU depth6 400 lr0.04를 고정하고 scoring×LI, reverse shrinkage, log LI, batter missing, all-four를 다시 비교

### main60_control

- role: control

### scoring_x_li

- declared change: scoring_position_x_li 단독
- added features: `scoring_position_x_li`
- removed features: none
- model changes: none

### reverse_shrunk

- declared change: pitcher_reverse_rate_shrunk 단독
- added features: `pitcher_reverse_rate_shrunk`
- removed features: none
- model changes: none

### log_li

- declared change: log1p_li 단독
- added features: `log1p_li`
- removed features: none
- model changes: none

### batter_missing

- declared change: batter_history_missing 단독
- added features: `batter_history_missing`
- removed features: none
- model changes: none

### all_four

- declared change: 상위 4개 전체
- added features: `scoring_position_x_li`, `pitcher_reverse_rate_shrunk`, `log1p_li`, `batter_history_missing`
- removed features: none
- model changes: none
