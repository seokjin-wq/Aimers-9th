# 075_success_k50_factorial: 투수·타자 당해 시즌 성공률 k=50 기여 분해

- 가설: k=50의 소폭 개선은 투수 또는 타자 한쪽에서만 나올 수 있으므로 기여 요소만 유지하면 추가 개선된다.
- control: `k20_k20_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `412236db9a08`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| both_k50 | control 대비 투수·타자 성공률 모두 k50 | 0.247529588 | -0.000008133 | 1/1 | 911.640 |
| k20_k20_control | control: 투수 k20, 타자 k20 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| batter_k50 | control 대비 타자 성공률만 k50 | 0.247561992 | 0.000024272 | 0/1 | 898.668 |
| pitcher_k50 | control 대비 투수 성공률만 k50 | 0.247566701 | 0.000028980 | 0/1 | 896.783 |

## 실제 변경 필드

- `k20_k20_control`: control
- `pitcher_k50`: features.custom, features.description, features.name
- `batter_k50`: features.custom, features.description, features.name
- `both_k50`: features.custom, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/075_success_k50_factorial/20260818T045005885751Z_412236db9a08`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_073`
- 기준 variant: `success_k50`
- 검증할 변경: Fix all else and compare k20/k20, pitcher50/batter20, pitcher20/batter50, and k50/k50.

### k20_k20_control

- role: control

### pitcher_k50

- declared change: control 대비 투수 성공률만 k50
- added features: `pitcher_season_success_rate_k50`
- removed features: `pitcher_season_success_rate_k20`
- model changes: none

### batter_k50

- declared change: control 대비 타자 성공률만 k50
- added features: `batter_season_success_rate_k50`
- removed features: `batter_season_success_rate_k20`
- model changes: none

### both_k50

- declared change: control 대비 투수·타자 성공률 모두 k50
- added features: `pitcher_season_success_rate_k50`, `batter_season_success_rate_k50`
- removed features: `pitcher_season_success_rate_k20`, `batter_season_success_rate_k20`
- model changes: none
