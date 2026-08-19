# 038_sequence_context: 연속 투구·동일 타석 문맥

- 가설: 행 간격과 동일 타석 여부가 직전 결과의 시간적 의미를 구분한다
- control: `main81_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `0ccd98d8b895`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| plate_context | 동일 타석·타석 내 순번·최근 2·3투구 추가 | 0.246925044 | -0.000016796 | 1/1 | 1153.644 |
| entity_gaps | 투수·타자 행 간격과 연속 플래그 추가 | 0.246931809 | -0.000010030 | 1/1 | 1150.936 |
| full_sequence | 행 간격·전역 직전 결과·동일 타석 문맥 모두 추가 | 0.246934026 | -0.000007814 | 1/1 | 1150.048 |
| main81_control | control: 현재 최고 main81 | 0.246941840 | 0.000000000 | 0/1 | 1146.921 |

## 실제 변경 필드

- `main81_control`: control
- `entity_gaps`: features.custom, features.description, features.expected_count, features.name
- `plate_context`: features.custom, features.description, features.expected_count, features.name
- `full_sequence`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/038_sequence_context/20260817T184310929165Z_0ccd98d8b895`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_037`
- 기준 variant: `batter_middle`
- 검증할 변경: main81 최고 피처와 GPU CatBoost를 고정하고 pitcher/batter 행 간격, 바로 전 행 여부, 동일 타석, 타석 내 순번·최근 성공률만 개별·조합 추가

### main81_control

- role: control

### entity_gaps

- declared change: 투수·타자 행 간격과 연속 플래그 추가
- added features: `pitcher_row_gap`, `batter_row_gap`, `pitcher_is_immediate`, `batter_is_immediate`, `same_matchup_previous`
- removed features: none
- model changes: none

### plate_context

- declared change: 동일 타석·타석 내 순번·최근 2·3투구 추가
- added features: `same_matchup_previous`, `plate_appearance_pitch_index`, `plate_appearance_recent2_success`, `plate_appearance_recent3_success`
- removed features: none
- model changes: none

### full_sequence

- declared change: 행 간격·전역 직전 결과·동일 타석 문맥 모두 추가
- added features: `pitcher_row_gap`, `batter_row_gap`, `pitcher_is_immediate`, `batter_is_immediate`, `same_matchup_previous`, `previous_global_success`, `previous_global_reverse`, `plate_appearance_pitch_index`, `plate_appearance_recent2_success`, `plate_appearance_recent3_success`
- removed features: none
- model changes: none
