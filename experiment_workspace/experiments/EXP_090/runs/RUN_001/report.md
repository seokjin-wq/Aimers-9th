# 090_inning_interactions: EDA 기반 이닝 구간 조건부 상호작용

- 가설: 후반 이닝 하락은 LI와 투수 과거 상태에 따라 다른 기울기로 나타난다.
- control: `same_hand_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `dda2b48326e7`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| late_pitcher_history | 후반 이닝×투수 성공·반대·가운데 이력 추가 | 0.247501577 | -0.000010289 | 1/1 | 922.853 |
| inning_all | 이닝 phase·LI·투수이력 블록 동시 추가 | 0.247509175 | -0.000002692 | 1/1 | 919.811 |
| same_hand_control | control: EXP_084 CPU same-hand pitchmix | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| phase_li_slopes | 네 이닝 구간별 LI 상호작용 추가 | 0.247526637 | 0.000014771 | 0/1 | 912.821 |
| inning_phase_cat | 1-3·4-6·7-9·연장 inning phase categorical 추가 | 0.247570667 | 0.000058800 | 0/1 | 895.195 |

## 실제 변경 필드

- `same_hand_control`: control
- `inning_phase_cat`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `phase_li_slopes`: features.custom, features.description, features.expected_count, features.name
- `late_pitcher_history`: features.custom, features.description, features.expected_count, features.name
- `inning_all`: features.categorical, features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/090_inning_interactions/20260818T070118465423Z_dda2b48326e7`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_087`
- 기준 variant: `same_hand_pitchmix_triple`
- 검증할 변경: Fix EXP_084 CPU features; add inning phase category, phase×LI slopes, late-inning×pitcher history slopes, or all blocks.

### same_hand_control

- role: control

### inning_phase_cat

- declared change: 1-3·4-6·7-9·연장 inning phase categorical 추가
- added features: `inning_phase_state`
- removed features: none
- model changes: none

### phase_li_slopes

- declared change: 네 이닝 구간별 LI 상호작용 추가
- added features: `early_inning_x_li`, `middle_inning_x_li`, `late_inning_x_li`, `extra_inning_x_li`
- removed features: none
- model changes: none

### late_pitcher_history

- declared change: 후반 이닝×투수 성공·반대·가운데 이력 추가
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none

### inning_all

- declared change: 이닝 phase·LI·투수이력 블록 동시 추가
- added features: `inning_phase_state`, `early_inning_x_li`, `middle_inning_x_li`, `late_inning_x_li`, `extra_inning_x_li`, `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none
