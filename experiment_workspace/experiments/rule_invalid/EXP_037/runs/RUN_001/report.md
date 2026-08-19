# 037_middle_ball_sequence: middle·ball 최근 투구 복원

- 가설: 최근 middle·ball 상태가 success·reverse에 남은 신호를 보완한다
- control: `main77_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a0401826110b`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| batter_middle | 타자 middle 단기 창 추가 | 0.246927786 | -0.000009259 | 1/1 | 1152.547 |
| main77_control | control: success+reverse 최고 조합 | 0.246937045 | 0.000000000 | 0/1 | 1148.840 |
| all_state | 투수 middle·ball 및 타자 middle 단기 창 모두 추가 | 0.246938306 | 0.000001262 | 0/1 | 1148.335 |
| pitcher_ball | 투수 ball 단기 창 추가 | 0.246960091 | 0.000023046 | 0/1 | 1139.614 |
| pitcher_middle | 투수 middle 단기 창 추가 | 0.246961791 | 0.000024747 | 0/1 | 1138.934 |
| pitcher_middle_ball | 투수 middle·ball 단기 창 추가 | 0.246962085 | 0.000025041 | 0/1 | 1138.816 |

## 실제 변경 필드

- `main77_control`: control
- `pitcher_middle`: features.custom, features.description, features.expected_count, features.name
- `pitcher_ball`: features.custom, features.description, features.expected_count, features.name
- `batter_middle`: features.custom, features.description, features.expected_count, features.name
- `pitcher_middle_ball`: features.custom, features.description, features.expected_count, features.name
- `all_state`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/037_middle_ball_sequence/20260817T183805072174Z_a0401826110b`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_036`
- 기준 variant: `reverse_short`
- 검증할 변경: main77 reverse-short와 GPU CatBoost를 고정하고 투수 middle, 투수 ball, 타자 middle의 직전·3·5·10 창만 개별·조합 추가

### main77_control

- role: control

### pitcher_middle

- declared change: 투수 middle 단기 창 추가
- added features: `pitcher_previous_pitch_middle`, `pitcher_recent3_pitch_middle`, `pitcher_recent5_pitch_middle`, `pitcher_recent10_pitch_middle`
- removed features: none
- model changes: none

### pitcher_ball

- declared change: 투수 ball 단기 창 추가
- added features: `pitcher_previous_pitch_ball`, `pitcher_recent3_pitch_ball`, `pitcher_recent5_pitch_ball`, `pitcher_recent10_pitch_ball`
- removed features: none
- model changes: none

### batter_middle

- declared change: 타자 middle 단기 창 추가
- added features: `batter_previous_pitch_middle`, `batter_recent3_pitch_middle`, `batter_recent5_pitch_middle`, `batter_recent10_pitch_middle`
- removed features: none
- model changes: none

### pitcher_middle_ball

- declared change: 투수 middle·ball 단기 창 추가
- added features: `pitcher_previous_pitch_middle`, `pitcher_recent3_pitch_middle`, `pitcher_recent5_pitch_middle`, `pitcher_recent10_pitch_middle`, `pitcher_previous_pitch_ball`, `pitcher_recent3_pitch_ball`, `pitcher_recent5_pitch_ball`, `pitcher_recent10_pitch_ball`
- removed features: none
- model changes: none

### all_state

- declared change: 투수 middle·ball 및 타자 middle 단기 창 모두 추가
- added features: `pitcher_previous_pitch_middle`, `pitcher_recent3_pitch_middle`, `pitcher_recent5_pitch_middle`, `pitcher_recent10_pitch_middle`, `pitcher_previous_pitch_ball`, `pitcher_recent3_pitch_ball`, `pitcher_recent5_pitch_ball`, `pitcher_recent10_pitch_ball`, `batter_previous_pitch_middle`, `batter_recent3_pitch_middle`, `batter_recent5_pitch_middle`, `batter_recent10_pitch_middle`
- removed features: none
- model changes: none
