# 086_exact_season_snapshots: 직전 시즌 마지막 공식 타깃까지 닫은 정확한 시즌 상태

- 가설: 기존 시즌 상태의 선수별 한 투구 off-by-one을 제거하면 특히 시즌 초 확률이 정확해진다.
- control: `approximate_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `fd6b36131337`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| batter_exact | 타자 시즌 n·success만 공식 마지막 타깃으로 정확히 닫음 | 0.247509462 | -0.000002405 | 1/1 | 919.696 |
| approximate_control | control: EXP_084 approximate season snapshot | 0.247511867 | 0.000000000 | 0/1 | 918.734 |
| pitcher_exact | 투수 시즌 n·success만 공식 마지막 타깃으로 정확히 닫음 | 0.247518530 | 0.000006664 | 0/1 | 916.066 |
| both_exact_k20 | 투수·타자 모두 exact snapshot, success k20 | 0.247521991 | 0.000010125 | 0/1 | 914.681 |
| both_exact_k50 | 투수·타자 모두 exact snapshot, success k50 | 0.247527694 | 0.000015827 | 0/1 | 912.398 |

## 실제 변경 필드

- `approximate_control`: control
- `pitcher_exact`: features.custom, features.description, features.name
- `batter_exact`: features.custom, features.description, features.name
- `both_exact_k20`: features.custom, features.description, features.name
- `both_exact_k50`: features.custom, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/086_exact_season_snapshots/20260818T061047523177Z_fd6b36131337`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_084`
- 기준 variant: `same_hand_pitchmix`
- 검증할 변경: Fix EXP_084 CPU features; replace approximate pitcher/batter current-season success and count with exact completed-season snapshots using official training labels only, individually and together.

### approximate_control

- role: control

### pitcher_exact

- declared change: 투수 시즌 n·success만 공식 마지막 타깃으로 정확히 닫음
- added features: `pitcher_season_n_exact`, `pitcher_season_success_rate_exact_k20`
- removed features: `pitcher_season_n`, `pitcher_season_success_rate_k20`
- model changes: none

### batter_exact

- declared change: 타자 시즌 n·success만 공식 마지막 타깃으로 정확히 닫음
- added features: `batter_season_n_exact`, `batter_season_success_rate_exact_k20`
- removed features: `batter_season_n`, `batter_season_success_rate_k20`
- model changes: none

### both_exact_k20

- declared change: 투수·타자 모두 exact snapshot, success k20
- added features: `pitcher_season_n_exact`, `pitcher_season_success_rate_exact_k20`, `batter_season_n_exact`, `batter_season_success_rate_exact_k20`
- removed features: `pitcher_season_n`, `pitcher_season_success_rate_k20`, `batter_season_n`, `batter_season_success_rate_k20`
- model changes: none

### both_exact_k50

- declared change: 투수·타자 모두 exact snapshot, success k50
- added features: `pitcher_season_n_exact`, `pitcher_season_success_rate_exact_k50`, `batter_season_n_exact`, `batter_season_success_rate_exact_k50`
- removed features: `pitcher_season_n`, `pitcher_season_success_rate_k20`, `batter_season_n`, `batter_season_success_rate_k20`
- model changes: none
