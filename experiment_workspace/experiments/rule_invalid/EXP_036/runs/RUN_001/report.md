# 036_reverse_sequence: 투수 reverse 최근 투구 복원

- 가설: 최근 reverse 상태가 성공 rolling과 독립적인 단기 위험 신호를 제공한다
- control: `main73_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `d9c7f52abef9`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| reverse_short | 투수 reverse 직전·3·5·10 추가 | 0.246938002 | -0.000231899 | 1/1 | 1148.457 |
| reverse_all | 투수 reverse 직전·3·5·10·20·50 모두 추가 | 0.246960934 | -0.000208968 | 1/1 | 1139.277 |
| reverse_long | 투수 reverse 직전·10·20·50 추가 | 0.246983938 | -0.000185963 | 1/1 | 1130.068 |
| reverse_previous | 투수 직전 reverse만 추가 | 0.247046510 | -0.000123391 | 1/1 | 1105.020 |
| main73_control | control: 성공 rolling 최고 조합 | 0.247169901 | 0.000000000 | 0/1 | 1055.625 |

## 실제 변경 필드

- `main73_control`: control
- `reverse_previous`: features.custom, features.description, features.expected_count, features.name
- `reverse_short`: features.custom, features.description, features.expected_count, features.name
- `reverse_long`: features.custom, features.description, features.expected_count, features.name
- `reverse_all`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/036_reverse_sequence/20260817T183420750887Z_d9c7f52abef9`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_035`
- 기준 variant: `add_all_extensions`
- 검증할 변경: main73과 GPU CatBoost를 고정하고 투수 reverse 직전·3·5·10·20·50투구 창의 포함 조합만 변경

### main73_control

- role: control

### reverse_previous

- declared change: 투수 직전 reverse만 추가
- added features: `pitcher_previous_pitch_reverse`
- removed features: none
- model changes: none

### reverse_short

- declared change: 투수 reverse 직전·3·5·10 추가
- added features: `pitcher_previous_pitch_reverse`, `pitcher_recent3_pitch_reverse`, `pitcher_recent5_pitch_reverse`, `pitcher_recent10_pitch_reverse`
- removed features: none
- model changes: none

### reverse_long

- declared change: 투수 reverse 직전·10·20·50 추가
- added features: `pitcher_previous_pitch_reverse`, `pitcher_recent10_pitch_reverse`, `pitcher_recent20_pitch_reverse`, `pitcher_recent50_pitch_reverse`
- removed features: none
- model changes: none

### reverse_all

- declared change: 투수 reverse 직전·3·5·10·20·50 모두 추가
- added features: `pitcher_previous_pitch_reverse`, `pitcher_recent3_pitch_reverse`, `pitcher_recent5_pitch_reverse`, `pitcher_recent10_pitch_reverse`, `pitcher_recent20_pitch_reverse`, `pitcher_recent50_pitch_reverse`
- removed features: none
- model changes: none
