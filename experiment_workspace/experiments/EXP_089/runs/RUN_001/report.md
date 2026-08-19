# 089_safe_season_progress: 공식 학습 경계와 현재 행 ID만 쓰는 시즌 진행도

- 가설: 월보다 세밀한 시즌 내 진행도가 시간 드리프트를 포착한다.
- control: `same_hand_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a03bd5c4b34f`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| same_hand_control | control: EXP_084 CPU same-hand pitchmix | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| phase_numeric | 12,500행 단위 시즌 phase를 numeric으로 추가 | 0.247546315 | 0.000034449 | 0/1 | 904.943 |
| phase_categorical | 동일 시즌 phase를 categorical로 추가 | 0.247608549 | 0.000096683 | 0/1 | 880.031 |
| progress_index | 현재 행의 안전한 시즌 내 투구 index 추가 | 0.247631092 | 0.000119225 | 0/1 | 871.007 |
| index_plus_phase | 안전한 numeric index와 categorical phase 동시 추가 | 0.247643218 | 0.000131351 | 0/1 | 866.153 |

## 실제 변경 필드

- `same_hand_control`: control
- `progress_index`: features.custom, features.description, features.expected_count, features.name
- `phase_numeric`: features.custom, features.description, features.expected_count, features.name
- `phase_categorical`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `index_plus_phase`: features.categorical, features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/089_safe_season_progress/20260818T065422590470Z_a03bd5c4b34f`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_087`
- 기준 variant: `same_hand_pitchmix_triple`
- 검증할 변경: Fix EXP_084 CPU base; add safe numeric season pitch index, coarse phase, or both. Training starts come from official train; validation start comes from the last official reference row; TEST suffix is used row-locally.

### same_hand_control

- role: control

### progress_index

- declared change: 현재 행의 안전한 시즌 내 투구 index 추가
- added features: `season_pitch_index_safe`
- removed features: none
- model changes: none

### phase_numeric

- declared change: 12,500행 단위 시즌 phase를 numeric으로 추가
- added features: `season_phase_20_safe`
- removed features: none
- model changes: none

### phase_categorical

- declared change: 동일 시즌 phase를 categorical로 추가
- added features: `season_phase_20_safe`
- removed features: none
- model changes: none

### index_plus_phase

- declared change: 안전한 numeric index와 categorical phase 동시 추가
- added features: `season_pitch_index_safe`, `season_phase_20_safe`
- removed features: none
- model changes: none
