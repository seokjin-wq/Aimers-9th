# 078_low_card_categorical: 저카디널리티 블록별 CatBoost 범주 처리

- 가설: 의미상 이산적인 블록을 한 번에 하나씩 native categorical로 처리하면 숫자 임계값보다 정확한 조건부 확률을 학습할 수 있다.
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `33aa5092cfb5`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_hands_cat | control 대비 count_state와 양손 코드를 categorical 추가 | 0.247515859 | -0.000021862 | 1/1 | 917.136 |
| main69_control | control: 문자열 3개와 batter_team만 categorical | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| count_state_cat | control 대비 count_state만 categorical 추가 | 0.247540981 | 0.000003260 | 0/1 | 907.079 |
| pitcher_team_cat | control 대비 pitcher_team_id만 categorical 추가 | 0.247548014 | 0.000010293 | 0/1 | 904.264 |
| hands_cat | control 대비 pitcher_hand·batter_hand만 categorical 추가 | 0.247548550 | 0.000010829 | 0/1 | 904.049 |
| calendar_cat | control 대비 game_month·game_dayofweek만 categorical 추가 | 0.247597221 | 0.000059501 | 0/1 | 884.565 |

## 실제 변경 필드

- `main69_control`: control
- `count_state_cat`: features.categorical, features.description, features.name
- `hands_cat`: features.categorical, features.description, features.name
- `calendar_cat`: features.categorical, features.description, features.name
- `pitcher_team_cat`: features.categorical, features.description, features.name
- `count_hands_cat`: features.categorical, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/078_low_card_categorical/20260818T050609006344Z_33aa5092cfb5`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_072`
- 기준 variant: `main69_control`
- 검증할 변경: Fix main69 and d8 decay0.85; separately add count_state, hands, calendar, pitcher_team, or count plus hands to the native categorical list.

### main69_control

- role: control

### count_state_cat

- declared change: control 대비 count_state만 categorical 추가
- added features: none
- removed features: none
- model changes: none

### hands_cat

- declared change: control 대비 pitcher_hand·batter_hand만 categorical 추가
- added features: none
- removed features: none
- model changes: none

### calendar_cat

- declared change: control 대비 game_month·game_dayofweek만 categorical 추가
- added features: none
- removed features: none
- model changes: none

### pitcher_team_cat

- declared change: control 대비 pitcher_team_id만 categorical 추가
- added features: none
- removed features: none
- model changes: none

### count_hands_cat

- declared change: control 대비 count_state와 양손 코드를 categorical 추가
- added features: none
- removed features: none
- model changes: none
