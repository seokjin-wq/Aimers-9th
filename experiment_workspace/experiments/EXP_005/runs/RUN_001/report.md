# 005_categorical_scope: CatBoost 범주 컬럼 범위

- 가설: 숫자 코드인 선수·팀·이산 상황 변수를 명목 범주로 처리하면 2024 Brier가 개선된다
- control: `basic3_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a17c54bfa2b9`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| basic3_control | control: 문자열 3개만 native categorical | 0.248009268 | 0.000000000 | 0/1 | 719.619 |
| add_players_teams_hands | 선수·팀 ID와 손 유형을 범주로 추가 | 0.248211411 | 0.000202144 | 0/1 | 638.699 |
| add_player_ids | pitcher_id와 batter_id를 범주로 추가 | 0.248397805 | 0.000388538 | 0/1 | 564.084 |
| all_discrete | 달력·카운트·주자 등 소수준 이산값도 범주로 추가 | 0.250603519 | 0.002594251 | 0/1 | 0.000 |

## 실제 변경 필드

- `basic3_control`: control
- `add_player_ids`: features.categorical, features.description, features.name
- `add_players_teams_hands`: features.categorical, features.description, features.name
- `all_discrete`: features.categorical, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/005_categorical_scope/20260817T153944697580Z_a17c54bfa2b9`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_004`
- 기준 variant: `native_basic`
- 검증할 변경: CatBoost native 모델을 고정하고 범주로 지정하는 컬럼 범위만 basic3, 선수 ID, 선수·팀·손, 전체 이산으로 확대

### basic3_control

- role: control

### add_player_ids

- declared change: pitcher_id와 batter_id를 범주로 추가
- added features: none
- removed features: none
- model changes: none

### add_players_teams_hands

- declared change: 선수·팀 ID와 손 유형을 범주로 추가
- added features: none
- removed features: none
- model changes: none

### all_discrete

- declared change: 달력·카운트·주자 등 소수준 이산값도 범주로 추가
- added features: none
- removed features: none
- model changes: none
