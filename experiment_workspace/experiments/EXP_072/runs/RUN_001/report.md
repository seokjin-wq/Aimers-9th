# 072_career_state_pruning: 당해 시즌 상태 사용 시 통산 누적 상태 피처 가지치기

- 가설: 당해 시즌 상태 피처가 이미 최신 선수 상태를 설명하므로, 중복되는 통산 누적 상태 피처를 제거하면 CatBoost의 분할 용량과 확률 보정이 개선된다.
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `fe1730e1cabb`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main69_control | control: EXP_070 최고 조합과 동일 | 0.247496084 | 0.000000000 | 0/1 | 925.051 |
| drop_batter_career | control 대비 타자 통산 n/success/middle 상태 3개 제거 | 0.247509302 | 0.000013217 | 0/1 | 919.760 |
| drop_all_career | control 대비 투수 5개와 타자 3개 통산 상태를 모두 제거 | 0.247520871 | 0.000024786 | 0/1 | 915.129 |
| drop_pitcher_career | control 대비 투수 통산 n/success/reverse/middle/ball 상태 5개 제거 | 0.247554038 | 0.000057953 | 0/1 | 901.852 |

## 실제 변경 필드

- `main69_control`: control
- `drop_pitcher_career`: features.description, features.exclude, features.expected_count, features.name
- `drop_batter_career`: features.description, features.exclude, features.expected_count, features.name
- `drop_all_career`: features.description, features.exclude, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/072_career_state_pruning/20260818T040904964217Z_fe1730e1cabb`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_070`
- 기준 variant: `cpu45_gpu40_extra15`
- 검증할 변경: Keep EXP_070 model family fixed conceptually and compare main69 against dropping pitcher career, batter career, or both career state blocks.

### main69_control

- role: control

### drop_pitcher_career

- declared change: control 대비 투수 통산 n/success/reverse/middle/ball 상태 5개 제거
- added features: none
- removed features: `asof_pitcher_n`, `asof_pitcher_success_rate`, `asof_pitcher_reverse_rate`, `asof_pitcher_middle_rate`, `asof_pitcher_ball_rate`
- model changes: none

### drop_batter_career

- declared change: control 대비 타자 통산 n/success/middle 상태 3개 제거
- added features: none
- removed features: `asof_batter_n`, `asof_batter_success_rate`, `asof_batter_middle_rate`
- model changes: none

### drop_all_career

- declared change: control 대비 투수 5개와 타자 3개 통산 상태를 모두 제거
- added features: none
- removed features: `asof_pitcher_n`, `asof_pitcher_success_rate`, `asof_pitcher_reverse_rate`, `asof_pitcher_middle_rate`, `asof_pitcher_ball_rate`, `asof_batter_n`, `asof_batter_success_rate`, `asof_batter_middle_rate`
- model changes: none
