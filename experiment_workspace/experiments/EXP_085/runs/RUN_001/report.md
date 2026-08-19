# 085_history_missingness: EDA 기반 최근·선수 이력 결측 신호 재검증

- 가설: 결측 여부 자체가 시즌 초와 신규 선수 상태를 나타내므로 현재 강한 모델에서도 추가 신호를 준다.
- control: `count_hands_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `522f6d7353fa`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_hands_control | control: EXP_080 CPU count+hands base | 0.247515859 | 0.000000000 | 0/1 | 917.136 |
| batter_missing | 타자 상대 통산 성공률 결측 여부만 추가 | 0.247546079 | 0.000030221 | 0/1 | 905.038 |
| all_missing | 최근·투수·타자 이력 결측 플래그 3개 동시 추가 | 0.247562134 | 0.000046275 | 0/1 | 898.611 |
| recent_missing | 직전 경기 성공률 결측 여부만 추가 | 0.247573214 | 0.000057355 | 0/1 | 894.176 |
| pitcher_missing | 투수 통산 성공률 결측 여부만 추가 | 0.247589793 | 0.000073934 | 0/1 | 887.539 |

## 실제 변경 필드

- `count_hands_control`: control
- `recent_missing`: features.custom, features.description, features.expected_count, features.name
- `pitcher_missing`: features.custom, features.description, features.expected_count, features.name
- `batter_missing`: features.custom, features.description, features.expected_count, features.name
- `all_missing`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/085_history_missingness/20260818T060355928744Z_522f6d7353fa`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_080`
- 기준 variant: `count_hands_promoted`
- 검증할 변경: Fix EXP_080 CPU base; add recent, pitcher, batter, or all three history-missing flags one block at a time.

### count_hands_control

- role: control

### recent_missing

- declared change: 직전 경기 성공률 결측 여부만 추가
- added features: `recent_history_missing`
- removed features: none
- model changes: none

### pitcher_missing

- declared change: 투수 통산 성공률 결측 여부만 추가
- added features: `pitcher_history_missing`
- removed features: none
- model changes: none

### batter_missing

- declared change: 타자 상대 통산 성공률 결측 여부만 추가
- added features: `batter_history_missing`
- removed features: none
- model changes: none

### all_missing

- declared change: 최근·투수·타자 이력 결측 플래그 3개 동시 추가
- added features: `recent_history_missing`, `pitcher_history_missing`, `batter_history_missing`
- removed features: none
- model changes: none
