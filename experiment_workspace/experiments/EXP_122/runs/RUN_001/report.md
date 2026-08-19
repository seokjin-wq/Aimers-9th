# 122_extended_reliability_rates: Extended pitcher-history reliability rates

- 가설: Reliability weighting that helped success/reverse/middle may also stabilize noisy pitcher ball/strike and pitch-mix rates for low-history pitchers.
- control: `main78_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `27db72203aa8`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main78_control | control: six-feature history reliability winner | 0.247487993 | 0.000000000 | 0/1 | 928.291 |
| add_all_extended_rates | add all five extended reliability-weighted rates | 0.247514700 | 0.000026707 | 0/1 | 917.600 |
| add_pitchmix_reliability | add reliability-weighted fastball, breaking, and offspeed rates only | 0.247542707 | 0.000054715 | 0/1 | 906.388 |
| add_ball_strike_reliability | add reliability-weighted pitcher ball and strike rates only | 0.247550763 | 0.000062770 | 0/1 | 903.163 |

## 실제 변경 필드

- `main78_control`: control
- `add_ball_strike_reliability`: features.custom, features.description, features.expected_count, features.name
- `add_pitchmix_reliability`: features.custom, features.description, features.expected_count, features.name
- `add_all_extended_rates`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/122_extended_reliability_rates/20260818T125812443541Z_27db72203aa8`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_114`
- 기준 variant: `reliability_k100_control`
- 검증할 변경: Fix main78 reliability CPU winner; add only ball/strike reliability-weighted rates, only three pitch-mix reliability-weighted rates, or all five.

### main78_control

- role: control

### add_ball_strike_reliability

- declared change: add reliability-weighted pitcher ball and strike rates only
- added features: `pitcher_ball_x_reliability`, `pitcher_strike_x_reliability`
- removed features: none
- model changes: none

### add_pitchmix_reliability

- declared change: add reliability-weighted fastball, breaking, and offspeed rates only
- added features: `pitcher_fastball_x_reliability`, `pitcher_breaking_x_reliability`, `pitcher_offspeed_x_reliability`
- removed features: none
- model changes: none

### add_all_extended_rates

- declared change: add all five extended reliability-weighted rates
- added features: `pitcher_ball_x_reliability`, `pitcher_strike_x_reliability`, `pitcher_fastball_x_reliability`, `pitcher_breaking_x_reliability`, `pitcher_offspeed_x_reliability`
- removed features: none
- model changes: none
