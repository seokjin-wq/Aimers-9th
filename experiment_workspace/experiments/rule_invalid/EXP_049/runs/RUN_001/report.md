# 049_cpu_global_window_upper: CPU 전역 rolling 상단 탐색

- 가설: window200 주변 상단에 더 나은 단일 창이 있다
- control: `global200_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `e70e3f5c256f`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| global200_control | control: window200 | 0.246697246 | 0.000000000 | 0/1 | 1244.834 |
| global175 | window175 | 0.246702152 | 0.000004906 | 0/1 | 1242.870 |
| global225 | window225 | 0.246706459 | 0.000009213 | 0/1 | 1241.146 |
| global250 | window250 | 0.246708636 | 0.000011390 | 0/1 | 1240.274 |
| global300 | window300 | 0.246736199 | 0.000038953 | 0/1 | 1229.240 |
| global400 | window400 | 0.246806803 | 0.000109557 | 0/1 | 1200.977 |

## 실제 변경 필드

- `global200_control`: control
- `global175`: features.custom, features.description, features.name
- `global225`: features.custom, features.description, features.name
- `global250`: features.custom, features.description, features.name
- `global300`: features.custom, features.description, features.name
- `global400`: features.custom, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/049_cpu_global_window_upper/20260817T200544382254Z_e70e3f5c256f`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_048`
- 기준 variant: `global200`
- 검증할 변경: CPU main80과 전역 단일 rolling을 고정하고 window 175·200·225·250·300·400만 변경

### global200_control

- role: control

### global175

- declared change: window175
- added features: `global_recent175_success`
- removed features: `global_recent200_success`
- model changes: none

### global225

- declared change: window225
- added features: `global_recent225_success`
- removed features: `global_recent200_success`
- model changes: none

### global250

- declared change: window250
- added features: `global_recent250_success`
- removed features: `global_recent200_success`
- model changes: none

### global300

- declared change: window300
- added features: `global_recent300_success`
- removed features: `global_recent200_success`
- model changes: none

### global400

- declared change: window400
- added features: `global_recent400_success`
- removed features: `global_recent200_success`
- model changes: none
