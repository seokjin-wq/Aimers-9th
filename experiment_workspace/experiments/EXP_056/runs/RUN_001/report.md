# 056_current_season_state: 현재 시즌 누적 상태 복원

- 가설: 공식 학습 종료 스냅샷과 현재 한 행의 asof 누적값 차이로 계산한 현재 시즌 투수 상태가 커리어 누적값보다 2024 제구 확률을 잘 설명한다
- control: `main60_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b2d52b5bf787`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| pitcher_batter_season_all | 투수 시즌 전체 상태에 타자 시즌 n·성공·middle 추가 | 0.247599268 | -0.000221053 | 1/1 | 883.746 |
| pitcher_season_all | 현재 시즌 투수 성공·reverse·middle·ball·strike와 n 추가 | 0.247636228 | -0.000184093 | 1/1 | 868.951 |
| pitcher_season_success | 공식 학습 스냅샷 대비 현재 시즌 투수 n와 성공률(k=20) 추가 | 0.247649205 | -0.000171115 | 1/1 | 863.756 |
| main60_control | control: 합법 main60 CatBoost | 0.247820321 | 0.000000000 | 0/1 | 795.256 |

## 실제 변경 필드

- `main60_control`: control
- `pitcher_season_success`: features.custom, features.description, features.expected_count, features.name
- `pitcher_season_all`: features.custom, features.description, features.expected_count, features.name
- `pitcher_batter_season_all`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/056_current_season_state/20260818T023407131113Z_b2d52b5bf787`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_054`
- 기준 variant: `extra_w24_safe`
- 검증할 변경: main60 CatBoost 대비 투수 시즌 성공+n, 투수 시즌 전체 상태, 투수+타자 시즌 전체 상태를 단계적으로 추가

### main60_control

- role: control

### pitcher_season_success

- declared change: 공식 학습 스냅샷 대비 현재 시즌 투수 n와 성공률(k=20) 추가
- added features: `pitcher_season_n`, `pitcher_season_success_rate_k20`
- removed features: none
- model changes: none

### pitcher_season_all

- declared change: 현재 시즌 투수 성공·reverse·middle·ball·strike와 n 추가
- added features: `pitcher_season_n`, `pitcher_season_success_rate_k20`, `pitcher_season_reverse_rate_k20`, `pitcher_season_middle_rate_k20`, `pitcher_season_ball_rate_k20`, `pitcher_season_strike_rate_k20`
- removed features: none
- model changes: none

### pitcher_batter_season_all

- declared change: 투수 시즌 전체 상태에 타자 시즌 n·성공·middle 추가
- added features: `pitcher_season_n`, `pitcher_season_success_rate_k20`, `pitcher_season_reverse_rate_k20`, `pitcher_season_middle_rate_k20`, `pitcher_season_ball_rate_k20`, `pitcher_season_strike_rate_k20`, `batter_season_n`, `batter_season_success_rate_k20`, `batter_season_middle_rate_k20`
- removed features: none
- model changes: none
