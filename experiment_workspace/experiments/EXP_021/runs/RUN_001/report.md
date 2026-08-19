# 021_season_row_position: 시즌 내 투구 순번 피처

- 가설: 월보다 세밀한 시즌 진행 위치가 시즌 중 제구율 변화를 포착해 Brier를 개선한다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `cd9a0b31cd0c`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main60_control | control: 현재 최고 main60 | 0.247820321 | 0.000000000 | 0/1 | 795.256 |
| phase_numeric | 시즌 20단계 구간을 numeric 추가 | 0.247902080 | 0.000081759 | 0/1 | 762.527 |
| phase_categorical | 시즌 20단계 구간을 categorical 추가 | 0.247910884 | 0.000090563 | 0/1 | 759.003 |
| pitch_index | 시즌 내 투구 순번 추가 | 0.248037720 | 0.000217399 | 0/1 | 708.230 |
| progress_proxy | 시즌 진행도 proxy 추가 | 0.248068353 | 0.000248033 | 0/1 | 695.967 |

## 실제 변경 필드

- `main60_control`: control
- `pitch_index`: features.custom, features.description, features.expected_count, features.name
- `progress_proxy`: features.custom, features.description, features.expected_count, features.name
- `phase_numeric`: features.custom, features.description, features.expected_count, features.name
- `phase_categorical`: features.categorical, features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/021_season_row_position/20260817T170458290591Z_cd9a0b31cd0c`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_020`
- 기준 variant: `scale106_shift008`
- 검증할 변경: 최고 모델을 고정하고 row_id 숫자부로 계산한 시즌 내 투구 순번, 정규화 진행도, 구간 피처만 추가

### main60_control

- role: control

### pitch_index

- declared change: 시즌 내 투구 순번 추가
- added features: `season_pitch_index`
- removed features: none
- model changes: none

### progress_proxy

- declared change: 시즌 진행도 proxy 추가
- added features: `season_progress_proxy`
- removed features: none
- model changes: none

### phase_numeric

- declared change: 시즌 20단계 구간을 numeric 추가
- added features: `season_phase_20`
- removed features: none
- model changes: none

### phase_categorical

- declared change: 시즌 20단계 구간을 categorical 추가
- added features: `season_phase_20`
- removed features: none
- model changes: none
