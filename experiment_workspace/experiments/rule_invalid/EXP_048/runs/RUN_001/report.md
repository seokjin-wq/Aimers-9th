# 048_cpu_global_window_fine: CPU 전역 rolling 100 주변 탐색

- 가설: 전역 rolling 최적 길이는 100 부근이다
- control: `global100_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `446dccc82008`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| global200 | window200 | 0.246697246 | -0.000028251 | 1/1 | 1244.834 |
| global150 | window150 | 0.246706150 | -0.000019347 | 1/1 | 1241.269 |
| global125 | window125 | 0.246719352 | -0.000006145 | 1/1 | 1235.984 |
| global100_control | control: window100 | 0.246725497 | 0.000000000 | 0/1 | 1233.525 |
| global75 | window75 | 0.246786726 | 0.000061230 | 0/1 | 1209.014 |

## 실제 변경 필드

- `global100_control`: control
- `global75`: features.custom, features.description, features.name
- `global125`: features.custom, features.description, features.name
- `global150`: features.custom, features.description, features.name
- `global200`: features.custom, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/048_cpu_global_window_fine/20260817T195917325175Z_446dccc82008`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_047`
- 기준 variant: `global100`
- 검증할 변경: CPU main80과 전역 단일 rolling 구조를 고정하고 window 75·100·125·150·200만 변경

### global100_control

- role: control

### global75

- declared change: window75
- added features: `global_recent75_success`
- removed features: `global_recent100_success`
- model changes: none

### global125

- declared change: window125
- added features: `global_recent125_success`
- removed features: `global_recent100_success`
- model changes: none

### global150

- declared change: window150
- added features: `global_recent150_success`
- removed features: `global_recent100_success`
- model changes: none

### global200

- declared change: window200
- added features: `global_recent200_success`
- removed features: `global_recent100_success`
- model changes: none
