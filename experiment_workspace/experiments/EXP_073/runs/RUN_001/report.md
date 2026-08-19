# 073_season_success_shrinkage: 당해 시즌 투수·타자 성공률 스무딩 강도 탐색

- 가설: 현재 k=20이 당해 시즌 성공률을 과도하거나 부족하게 스무딩할 수 있으므로, 성공률 피처의 k만 조정하면 행 독립성을 유지하면서 보정력이 개선된다.
- control: `success_k20_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `1b873ea689bb`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| success_k50 | control 대비 투수·타자 당해 시즌 성공률 k=50 | 0.247529588 | -0.000008133 | 1/1 | 911.640 |
| success_k20_control | control: 투수·타자 당해 시즌 성공률 k=20 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| success_k100 | control 대비 투수·타자 당해 시즌 성공률 k=100 | 0.247542631 | 0.000004911 | 0/1 | 906.418 |
| success_k10 | control 대비 투수·타자 당해 시즌 성공률 k=10 | 0.247556598 | 0.000018877 | 0/1 | 900.827 |
| success_k5 | control 대비 투수·타자 당해 시즌 성공률 k=5 | 0.247582275 | 0.000044554 | 0/1 | 890.549 |

## 실제 변경 필드

- `success_k20_control`: control
- `success_k5`: features.custom, features.description, features.name
- `success_k10`: features.custom, features.description, features.name
- `success_k50`: features.custom, features.description, features.name
- `success_k100`: features.custom, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/073_season_success_shrinkage/20260818T043447177095Z_1b873ea689bb`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_072`
- 기준 variant: `main69_control`
- 검증할 변경: Fix main69 and CPU CatBoost d8 decay0.85; replace only pitcher/batter current-season success smoothing k among 5,10,20,50,100.

### success_k20_control

- role: control

### success_k5

- declared change: control 대비 투수·타자 당해 시즌 성공률 k=5
- added features: `pitcher_season_success_rate_k5`, `batter_season_success_rate_k5`
- removed features: `pitcher_season_success_rate_k20`, `batter_season_success_rate_k20`
- model changes: none

### success_k10

- declared change: control 대비 투수·타자 당해 시즌 성공률 k=10
- added features: `pitcher_season_success_rate_k10`, `batter_season_success_rate_k10`
- removed features: `pitcher_season_success_rate_k20`, `batter_season_success_rate_k20`
- model changes: none

### success_k50

- declared change: control 대비 투수·타자 당해 시즌 성공률 k=50
- added features: `pitcher_season_success_rate_k50`, `batter_season_success_rate_k50`
- removed features: `pitcher_season_success_rate_k20`, `batter_season_success_rate_k20`
- model changes: none

### success_k100

- declared change: control 대비 투수·타자 당해 시즌 성공률 k=100
- added features: `pitcher_season_success_rate_k100`, `batter_season_success_rate_k100`
- removed features: `pitcher_season_success_rate_k20`, `batter_season_success_rate_k20`
- model changes: none
