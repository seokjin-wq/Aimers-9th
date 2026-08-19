# 063_pitchmix_and_readded_raw: 구종 구성과 제외 피처 재검증

- 가설: 현재 시즌 구종 구성과 과거에 제외했던 prev5·strike·fastball 원시값이 시즌 상태 모델에서는 추가 신호를 제공할 수 있다
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `12966d178c28`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| season_pitchmix | 현재 시즌 fastball·breaking·offspeed 비율 추가 | 0.247534702 | -0.000003018 | 1/1 | 909.592 |
| main69_control | control: EXP_060 최고 CatBoost | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| readd_prev5 | 제외했던 prev5 game success 원시값 재추가 | 0.247549501 | 0.000011780 | 0/1 | 903.668 |
| readd_strike_fast | 제외했던 커리어 strike·fastball 원시값 재추가 | 0.247549910 | 0.000012189 | 0/1 | 903.505 |
| all_readded_pitchmix | 원시값 3개와 현재 시즌 pitchmix 3개를 모두 추가 | 0.247569909 | 0.000032188 | 0/1 | 895.499 |

## 실제 변경 필드

- `main69_control`: control
- `season_pitchmix`: features.custom, features.description, features.expected_count, features.name
- `readd_prev5`: features.description, features.exclude, features.expected_count, features.name
- `readd_strike_fast`: features.description, features.exclude, features.expected_count, features.name
- `all_readded_pitchmix`: features.custom, features.description, features.exclude, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/063_pitchmix_and_readded_raw/20260818T031544775575Z_12966d178c28`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_062`
- 기준 variant: `extra_w18`
- 검증할 변경: main69 decay85 CatBoost 대비 시즌 pitchmix 3개, prev5 재추가, strike+fastball 재추가, 전체 조합 비교

### main69_control

- role: control

### season_pitchmix

- declared change: 현재 시즌 fastball·breaking·offspeed 비율 추가
- added features: `pitcher_season_fastball_rate_k20`, `pitcher_season_breaking_rate_k20`, `pitcher_season_offspeed_rate_k20`
- removed features: none
- model changes: none

### readd_prev5

- declared change: 제외했던 prev5 game success 원시값 재추가
- added features: `asof_pitcher_prev5_game_success_rate`
- removed features: none
- model changes: none

### readd_strike_fast

- declared change: 제외했던 커리어 strike·fastball 원시값 재추가
- added features: `asof_pitcher_strike_rate`, `asof_pitcher_fastball_rate`
- removed features: none
- model changes: none

### all_readded_pitchmix

- declared change: 원시값 3개와 현재 시즌 pitchmix 3개를 모두 추가
- added features: `asof_pitcher_strike_rate`, `asof_pitcher_prev5_game_success_rate`, `asof_pitcher_fastball_rate`, `pitcher_season_fastball_rate_k20`, `pitcher_season_breaking_rate_k20`, `pitcher_season_offspeed_rate_k20`
- removed features: none
- model changes: none
