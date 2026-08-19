# 076_season_event_counts: 행 독립 당해 시즌 사건 횟수 표현

- 가설: 당해 시즌 비율과 전체 표본 수만으로 트리가 개별 사건량을 복원하기 어려우므로, 성공·실패·reverse·middle·ball·strike의 로그 횟수를 직접 주면 성능이 개선된다.
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `184ce208985f`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main69_control | control: 당해 시즌 스무딩 비율과 표본 수 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| pitcher_success_counts | control 대비 투수 당해 시즌 성공·실패 로그 횟수 추가 | 0.247552900 | 0.000015179 | 0/1 | 902.308 |
| batter_event_counts | control 대비 타자 성공·실패·middle 로그 횟수 추가 | 0.247556628 | 0.000018907 | 0/1 | 900.815 |
| pitcher_event_counts | control 대비 투수 reverse·middle·ball·strike 로그 횟수 추가 | 0.247560859 | 0.000023139 | 0/1 | 899.121 |
| all_event_counts | control 대비 투수 6개와 타자 3개 사건 로그 횟수 모두 추가 | 0.247585685 | 0.000047965 | 0/1 | 889.183 |

## 실제 변경 필드

- `main69_control`: control
- `pitcher_success_counts`: features.custom, features.description, features.expected_count, features.name
- `pitcher_event_counts`: features.custom, features.description, features.expected_count, features.name
- `batter_event_counts`: features.custom, features.description, features.expected_count, features.name
- `all_event_counts`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/076_season_event_counts/20260818T045452565467Z_184ce208985f`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_072`
- 기준 variant: `main69_control`
- 검증할 변경: Fix main69 and CPU d8 decay0.85; add pitcher success/failure counts, pitcher event counts, batter event counts, or all counts.

### main69_control

- role: control

### pitcher_success_counts

- declared change: control 대비 투수 당해 시즌 성공·실패 로그 횟수 추가
- added features: `pitcher_season_success_count_log`, `pitcher_season_failure_count_log`
- removed features: none
- model changes: none

### pitcher_event_counts

- declared change: control 대비 투수 reverse·middle·ball·strike 로그 횟수 추가
- added features: `pitcher_season_reverse_count_log`, `pitcher_season_middle_count_log`, `pitcher_season_ball_count_log`, `pitcher_season_strike_count_log`
- removed features: none
- model changes: none

### batter_event_counts

- declared change: control 대비 타자 성공·실패·middle 로그 횟수 추가
- added features: `batter_season_success_count_log`, `batter_season_failure_count_log`, `batter_season_middle_count_log`
- removed features: none
- model changes: none

### all_event_counts

- declared change: control 대비 투수 6개와 타자 3개 사건 로그 횟수 모두 추가
- added features: `pitcher_season_success_count_log`, `pitcher_season_failure_count_log`, `pitcher_season_reverse_count_log`, `pitcher_season_middle_count_log`, `pitcher_season_ball_count_log`, `pitcher_season_strike_count_log`, `batter_season_success_count_log`, `batter_season_failure_count_log`, `batter_season_middle_count_log`
- removed features: none
- model changes: none
