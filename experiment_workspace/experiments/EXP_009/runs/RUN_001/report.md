# 009_positive_feature_combinations: EDA 개선 피처 조합

- 가설: 개별 개선된 카운트·스무딩·결측 피처를 조합하면 개선 폭이 누적된다
- control: `count_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a77a0180d059`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_control | control: EXP_008 최선 카운트 피처 | 0.247968140 | 0.000000000 | 0/1 | 736.083 |
| count_plus_smoothing | 카운트 기준에 스무딩 묶음 추가 | 0.247987123 | 0.000018983 | 0/1 | 728.484 |
| all_positive_groups | 카운트·스무딩·결측 세 묶음 전체 조합 | 0.248007918 | 0.000039778 | 0/1 | 720.160 |
| count_plus_missing | 카운트 기준에 결측 플래그 추가 | 0.248011145 | 0.000043005 | 0/1 | 718.868 |
| smoothing_plus_missing | 스무딩과 결측 플래그 조합 | 0.248026236 | 0.000058096 | 0/1 | 712.827 |

## 실제 변경 필드

- `count_control`: control
- `count_plus_smoothing`: features.custom, features.description, features.expected_count, features.name
- `count_plus_missing`: features.custom, features.description, features.expected_count, features.name
- `smoothing_plus_missing`: features.custom, features.description, features.expected_count, features.name
- `all_positive_groups`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/009_positive_feature_combinations/20260817T160157273725Z_a77a0180d059`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_008`
- 기준 variant: `add_count_state`
- 검증할 변경: main55+count를 기준으로 스무딩과 결측 플래그의 pairwise 및 전체 조합 효과를 비교

### count_control

- role: control

### count_plus_smoothing

- declared change: 카운트 기준에 스무딩 묶음 추가
- added features: `pitcher_success_rate_shrunk`, `pitcher_reverse_rate_shrunk`, `success_minus_reverse`, `log1p_pitcher_n`, `log1p_batter_n`
- removed features: none
- model changes: none

### count_plus_missing

- declared change: 카운트 기준에 결측 플래그 추가
- added features: `recent_history_missing`, `pitcher_history_missing`, `batter_history_missing`
- removed features: none
- model changes: none

### smoothing_plus_missing

- declared change: 스무딩과 결측 플래그 조합
- added features: `pitcher_success_rate_shrunk`, `pitcher_reverse_rate_shrunk`, `success_minus_reverse`, `log1p_pitcher_n`, `log1p_batter_n`, `recent_history_missing`, `pitcher_history_missing`, `batter_history_missing`
- removed features: `count_state`, `is_full_count`, `has_two_strikes`, `has_three_balls`, `has_two_outs`
- model changes: none

### all_positive_groups

- declared change: 카운트·스무딩·결측 세 묶음 전체 조합
- added features: `pitcher_success_rate_shrunk`, `pitcher_reverse_rate_shrunk`, `success_minus_reverse`, `log1p_pitcher_n`, `log1p_batter_n`, `recent_history_missing`, `pitcher_history_missing`, `batter_history_missing`
- removed features: none
- model changes: none
