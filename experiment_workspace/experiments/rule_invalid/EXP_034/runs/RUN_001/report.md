# 034_asof_pitch_sequence: 누적 asof 직전 투구 복원

- 가설: 누적 asof 차분으로 복원한 직전·최근 투구 결과가 단기 제구 흐름을 제공한다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `bc79e003275a`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| entity_recent_all | 투수·타자 직전 및 최근 3·5·10투구 모두 추가 | 0.247286548 | -0.000532517 | 1/1 | 1008.931 |
| pitcher_recent | 투수 직전 및 최근 3·5·10투구 추가 | 0.247353722 | -0.000465342 | 1/1 | 982.040 |
| batter_recent | 타자 직전 및 최근 3·5·10투구 추가 | 0.247493558 | -0.000325506 | 1/1 | 926.063 |
| both_previous | 투수·타자 직전 투구 성공 추가 | 0.247633372 | -0.000185693 | 1/1 | 870.094 |
| pitcher_previous | 투수 직전 투구 성공만 추가 | 0.247650241 | -0.000168824 | 1/1 | 863.341 |
| batter_previous | 타자 직전 상대 투구 성공만 추가 | 0.247656140 | -0.000162924 | 1/1 | 860.980 |
| main60_control | control: 기존 main60 | 0.247819064 | 0.000000000 | 0/1 | 795.759 |

## 실제 변경 필드

- `main60_control`: control
- `pitcher_previous`: features.custom, features.description, features.expected_count, features.name
- `batter_previous`: features.custom, features.description, features.expected_count, features.name
- `both_previous`: features.custom, features.description, features.expected_count, features.name
- `pitcher_recent`: features.custom, features.description, features.expected_count, features.name
- `batter_recent`: features.custom, features.description, features.expected_count, features.name
- `entity_recent_all`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/034_asof_pitch_sequence/20260817T182514538345Z_bc79e003275a`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_033`
- 기준 variant: `global_control`
- 검증할 변경: GPU CatBoost와 main60을 고정하고 pitcher/batter의 직전 및 최근 3·5·10투구 성공률 파생만 개별·조합 추가

### main60_control

- role: control

### pitcher_previous

- declared change: 투수 직전 투구 성공만 추가
- added features: `pitcher_previous_pitch_success`
- removed features: none
- model changes: none

### batter_previous

- declared change: 타자 직전 상대 투구 성공만 추가
- added features: `batter_previous_pitch_success`
- removed features: none
- model changes: none

### both_previous

- declared change: 투수·타자 직전 투구 성공 추가
- added features: `pitcher_previous_pitch_success`, `batter_previous_pitch_success`
- removed features: none
- model changes: none

### pitcher_recent

- declared change: 투수 직전 및 최근 3·5·10투구 추가
- added features: `pitcher_previous_pitch_success`, `pitcher_recent3_pitch_success`, `pitcher_recent5_pitch_success`, `pitcher_recent10_pitch_success`
- removed features: none
- model changes: none

### batter_recent

- declared change: 타자 직전 및 최근 3·5·10투구 추가
- added features: `batter_previous_pitch_success`, `batter_recent3_pitch_success`, `batter_recent5_pitch_success`, `batter_recent10_pitch_success`
- removed features: none
- model changes: none

### entity_recent_all

- declared change: 투수·타자 직전 및 최근 3·5·10투구 모두 추가
- added features: `pitcher_previous_pitch_success`, `pitcher_recent3_pitch_success`, `pitcher_recent5_pitch_success`, `pitcher_recent10_pitch_success`, `batter_previous_pitch_success`, `batter_recent3_pitch_success`, `batter_recent5_pitch_success`, `batter_recent10_pitch_success`
- removed features: none
- model changes: none
