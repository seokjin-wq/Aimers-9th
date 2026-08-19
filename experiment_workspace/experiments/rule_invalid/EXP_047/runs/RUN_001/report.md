# 047_cpu_global_rolling: CPU 전역 시간축 rolling

- 가설: 최근 전체 투구 흐름이 경기·당일 공통 제구 환경을 포착한다
- control: `main80_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `50636193b185`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| global100 | 전역 recent100 추가 | 0.246725497 | -0.000204848 | 1/1 | 1233.525 |
| global_all | 전역 recent5·10·20·50·100 모두 추가 | 0.246772587 | -0.000157758 | 1/1 | 1214.674 |
| global50 | 전역 recent50 추가 | 0.246846983 | -0.000083362 | 1/1 | 1184.893 |
| global20 | 전역 recent20 추가 | 0.246919353 | -0.000010992 | 1/1 | 1155.922 |
| main80_control | control: entity sequence only | 0.246930345 | 0.000000000 | 0/1 | 1151.522 |

## 실제 변경 필드

- `main80_control`: control
- `global20`: features.custom, features.description, features.expected_count, features.name
- `global50`: features.custom, features.description, features.expected_count, features.name
- `global100`: features.custom, features.description, features.expected_count, features.name
- `global_all`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/047_cpu_global_rolling/20260817T195308500101Z_50636193b185`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_046`
- 기준 variant: `cat_control`
- 검증할 변경: CPU main80을 고정하고 복원 가능한 과거 전역 성공의 recent5·10·20·50·100 rolling만 개별·조합 추가

### main80_control

- role: control

### global20

- declared change: 전역 recent20 추가
- added features: `global_recent20_success`
- removed features: none
- model changes: none

### global50

- declared change: 전역 recent50 추가
- added features: `global_recent50_success`
- removed features: none
- model changes: none

### global100

- declared change: 전역 recent100 추가
- added features: `global_recent100_success`
- removed features: none
- model changes: none

### global_all

- declared change: 전역 recent5·10·20·50·100 모두 추가
- added features: `global_recent5_success`, `global_recent10_success`, `global_recent20_success`, `global_recent50_success`, `global_recent100_success`
- removed features: none
- model changes: none
