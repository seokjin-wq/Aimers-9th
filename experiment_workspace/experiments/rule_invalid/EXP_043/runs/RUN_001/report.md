# 043_cpu_sequence_verification: 순차 피처 CPU 결정론 재검증

- 가설: GPU의 순차 피처 개선이 CPU 고정 모델에서도 재현된다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `be78ac5a51b9`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main77_reverse | success rolling + reverse short | 0.246938131 | -0.000880897 | 1/1 | 1148.405 |
| main87_batter_lags | main85 + 타자 lag2·3 추가 | 0.246953836 | -0.000865192 | 1/1 | 1142.118 |
| main85_plate | 타자 middle + 동일 타석 문맥까지 추가 | 0.246957546 | -0.000861482 | 1/1 | 1140.633 |
| main73_success | success rolling 전체 추가 | 0.247167164 | -0.000651864 | 1/1 | 1056.721 |
| main60_control | control: 순차 피처 없음 | 0.247819028 | 0.000000000 | 0/1 | 795.774 |

## 실제 변경 필드

- `main60_control`: control
- `main73_success`: features.custom, features.description, features.expected_count, features.name
- `main77_reverse`: features.custom, features.description, features.expected_count, features.name
- `main85_plate`: features.custom, features.description, features.expected_count, features.name
- `main87_batter_lags`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/043_cpu_sequence_verification/20260817T192324678699Z_be78ac5a51b9`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_042`
- 기준 variant: `batter_lags`
- 검증할 변경: CPU depth6 400 lr0.04를 고정하고 main60→main73→main77→main85→main87 핵심 누적 피처 단계만 비교

### main60_control

- role: control

### main73_success

- declared change: success rolling 전체 추가
- added features: `pitcher_previous_pitch_success`, `pitcher_recent3_pitch_success`, `pitcher_recent5_pitch_success`, `pitcher_recent10_pitch_success`, `batter_previous_pitch_success`, `batter_recent3_pitch_success`, `batter_recent5_pitch_success`, `batter_recent10_pitch_success`, `pitcher_recent20_pitch_success`, `pitcher_recent30_pitch_success`, `pitcher_recent50_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`
- removed features: none
- model changes: none

### main77_reverse

- declared change: success rolling + reverse short
- added features: `pitcher_previous_pitch_success`, `pitcher_recent3_pitch_success`, `pitcher_recent5_pitch_success`, `pitcher_recent10_pitch_success`, `batter_previous_pitch_success`, `batter_recent3_pitch_success`, `batter_recent5_pitch_success`, `batter_recent10_pitch_success`, `pitcher_recent20_pitch_success`, `pitcher_recent30_pitch_success`, `pitcher_recent50_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`, `pitcher_previous_pitch_reverse`, `pitcher_recent3_pitch_reverse`, `pitcher_recent5_pitch_reverse`, `pitcher_recent10_pitch_reverse`
- removed features: none
- model changes: none

### main85_plate

- declared change: 타자 middle + 동일 타석 문맥까지 추가
- added features: `pitcher_previous_pitch_success`, `pitcher_recent3_pitch_success`, `pitcher_recent5_pitch_success`, `pitcher_recent10_pitch_success`, `batter_previous_pitch_success`, `batter_recent3_pitch_success`, `batter_recent5_pitch_success`, `batter_recent10_pitch_success`, `pitcher_recent20_pitch_success`, `pitcher_recent30_pitch_success`, `pitcher_recent50_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`, `pitcher_previous_pitch_reverse`, `pitcher_recent3_pitch_reverse`, `pitcher_recent5_pitch_reverse`, `pitcher_recent10_pitch_reverse`, `batter_previous_pitch_middle`, `batter_recent3_pitch_middle`, `batter_recent5_pitch_middle`, `batter_recent10_pitch_middle`, `same_matchup_previous`, `plate_appearance_pitch_index`, `plate_appearance_recent2_success`, `plate_appearance_recent3_success`
- removed features: none
- model changes: none

### main87_batter_lags

- declared change: main85 + 타자 lag2·3 추가
- added features: `pitcher_previous_pitch_success`, `pitcher_recent3_pitch_success`, `pitcher_recent5_pitch_success`, `pitcher_recent10_pitch_success`, `batter_previous_pitch_success`, `batter_recent3_pitch_success`, `batter_recent5_pitch_success`, `batter_recent10_pitch_success`, `pitcher_recent20_pitch_success`, `pitcher_recent30_pitch_success`, `pitcher_recent50_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`, `pitcher_previous_pitch_reverse`, `pitcher_recent3_pitch_reverse`, `pitcher_recent5_pitch_reverse`, `pitcher_recent10_pitch_reverse`, `batter_previous_pitch_middle`, `batter_recent3_pitch_middle`, `batter_recent5_pitch_middle`, `batter_recent10_pitch_middle`, `same_matchup_previous`, `plate_appearance_pitch_index`, `plate_appearance_recent2_success`, `plate_appearance_recent3_success`, `batter_lag2_pitch_success`, `batter_lag3_pitch_success`
- removed features: none
- model changes: none
