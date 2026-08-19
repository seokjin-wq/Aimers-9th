# 042_lag_patterns: 최근 투구 lag 순서 패턴

- 가설: rolling 평균에 가려진 lag 순서가 다음 제구를 추가 설명한다
- control: `main85_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `c811c618fe78`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| batter_lags | 타자 lag2·3 추가 | 0.246863571 | -0.000019381 | 1/1 | 1178.252 |
| pitcher_lags | 투수 lag2·3·5 추가 | 0.246866700 | -0.000016252 | 1/1 | 1177.000 |
| lags_patterns_cat | 모든 lag + 최근 3개 패턴 categorical 추가 | 0.246871876 | -0.000011076 | 1/1 | 1174.928 |
| entity_lags | 투수·타자 lag 모두 추가 | 0.246880185 | -0.000002767 | 1/1 | 1171.601 |
| main85_control | control: main85 bag0 | 0.246882952 | 0.000000000 | 0/1 | 1170.494 |
| patterns_numeric | 투수·타자 최근 3개 패턴 numeric 추가 | 0.246890944 | 0.000007992 | 0/1 | 1167.295 |

## 실제 변경 필드

- `main85_control`: control
- `pitcher_lags`: features.custom, features.description, features.expected_count, features.name
- `batter_lags`: features.custom, features.description, features.expected_count, features.name
- `entity_lags`: features.custom, features.description, features.expected_count, features.name
- `patterns_numeric`: features.custom, features.description, features.expected_count, features.name
- `lags_patterns_cat`: features.categorical, features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/042_lag_patterns/20260817T191807787250Z_c811c618fe78`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_041`
- 기준 variant: `bag0`
- 검증할 변경: main85와 bag0 CatBoost를 고정하고 투수 lag2·3·5, 타자 lag2·3 및 최근 3개 이진 패턴만 개별·조합 추가

### main85_control

- role: control

### pitcher_lags

- declared change: 투수 lag2·3·5 추가
- added features: `pitcher_lag2_pitch_success`, `pitcher_lag3_pitch_success`, `pitcher_lag5_pitch_success`
- removed features: none
- model changes: none

### batter_lags

- declared change: 타자 lag2·3 추가
- added features: `batter_lag2_pitch_success`, `batter_lag3_pitch_success`
- removed features: none
- model changes: none

### entity_lags

- declared change: 투수·타자 lag 모두 추가
- added features: `pitcher_lag2_pitch_success`, `pitcher_lag3_pitch_success`, `pitcher_lag5_pitch_success`, `batter_lag2_pitch_success`, `batter_lag3_pitch_success`
- removed features: none
- model changes: none

### patterns_numeric

- declared change: 투수·타자 최근 3개 패턴 numeric 추가
- added features: `pitcher_last3_success_pattern`, `batter_last3_success_pattern`
- removed features: none
- model changes: none

### lags_patterns_cat

- declared change: 모든 lag + 최근 3개 패턴 categorical 추가
- added features: `pitcher_lag2_pitch_success`, `pitcher_lag3_pitch_success`, `pitcher_lag5_pitch_success`, `batter_lag2_pitch_success`, `batter_lag3_pitch_success`, `pitcher_last3_success_pattern`, `batter_last3_success_pattern`
- removed features: none
- model changes: none
