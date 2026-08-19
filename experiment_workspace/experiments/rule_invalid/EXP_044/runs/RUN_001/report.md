# 044_cpu_window_pruning: CPU 투수 장기·타자 단기 창 정리

- 가설: 타자 2·8 창 제거와 투수 장기 창 선별이 main77을 개선한다
- control: `main77_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `43c40ba4a582`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main77_control | control: 투수 20·30·50 + 타자 2·8 포함 | 0.246938131 | 0.000000000 | 0/1 | 1148.405 |
| pitcher20_50 | 타자 2·8 및 투수 30 제거 | 0.246947982 | 0.000009851 | 0/1 | 1144.462 |
| pitcher50 | 투수 50만 유지 | 0.246967598 | 0.000029468 | 0/1 | 1136.609 |
| pitcher20_30_50 | 타자 2·8 제거 | 0.246979461 | 0.000041330 | 0/1 | 1131.861 |
| pitcher20 | 투수 20만 유지 | 0.246994679 | 0.000056549 | 0/1 | 1125.768 |

## 실제 변경 필드

- `main77_control`: control
- `pitcher20_30_50`: features.custom, features.description, features.expected_count, features.name
- `pitcher20_50`: features.custom, features.description, features.expected_count, features.name
- `pitcher20`: features.custom, features.description, features.expected_count, features.name
- `pitcher50`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/044_cpu_window_pruning/20260817T192932935882Z_43c40ba4a582`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_043`
- 기준 variant: `main77_reverse`
- 검증할 변경: CPU depth6 400 lr0.04와 reverse short를 고정하고 투수 recent20·30·50 및 타자 recent2·8 포함 여부만 변경

### main77_control

- role: control

### pitcher20_30_50

- declared change: 타자 2·8 제거
- added features: none
- removed features: `batter_recent2_pitch_success`, `batter_recent8_pitch_success`
- model changes: none

### pitcher20_50

- declared change: 타자 2·8 및 투수 30 제거
- added features: none
- removed features: `pitcher_recent30_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`
- model changes: none

### pitcher20

- declared change: 투수 20만 유지
- added features: none
- removed features: `pitcher_recent30_pitch_success`, `pitcher_recent50_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`
- model changes: none

### pitcher50

- declared change: 투수 50만 유지
- added features: none
- removed features: `pitcher_recent20_pitch_success`, `pitcher_recent30_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`
- model changes: none
