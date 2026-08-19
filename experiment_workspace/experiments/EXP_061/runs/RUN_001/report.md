# 061_metric_specific_shrinkage: 시즌 지표별 스무딩 강도

- 가설: 현재 시즌 ball·strike·타자 middle은 성공률보다 저표본 변동이 커 더 강한 shrinkage가 일반화를 개선한다
- control: `common_k20`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `be483c1e3065`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| common_k20 | control: 모든 현재 시즌 비율 k20 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| metric_specific_all | ball500·strike200·batter-middle200을 동시에 적용 | 0.247553484 | 0.000015763 | 0/1 | 902.074 |
| ball_k500 | 투수 ball만 k20에서 k500으로 변경 | 0.247556542 | 0.000018822 | 0/1 | 900.849 |
| batter_middle_k200 | 타자 middle만 k20에서 k200으로 변경 | 0.247567650 | 0.000029930 | 0/1 | 896.403 |
| strike_k200 | 투수 strike만 k20에서 k200으로 변경 | 0.247573126 | 0.000035405 | 0/1 | 894.211 |

## 실제 변경 필드

- `common_k20`: control
- `ball_k500`: features.custom, features.description, features.name
- `strike_k200`: features.custom, features.description, features.name
- `batter_middle_k200`: features.custom, features.description, features.name
- `metric_specific_all`: features.custom, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/061_metric_specific_shrinkage/20260818T030159574418Z_be483c1e3065`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_060`
- 기준 variant: `decay085`
- 검증할 변경: main69 k20 공통 기준 대비 ball k500, strike k200, batter-middle k200을 개별 및 동시 교체

### common_k20

- role: control

### ball_k500

- declared change: 투수 ball만 k20에서 k500으로 변경
- added features: `pitcher_season_ball_rate_k500`
- removed features: `pitcher_season_ball_rate_k20`
- model changes: none

### strike_k200

- declared change: 투수 strike만 k20에서 k200으로 변경
- added features: `pitcher_season_strike_rate_k200`
- removed features: `pitcher_season_strike_rate_k20`
- model changes: none

### batter_middle_k200

- declared change: 타자 middle만 k20에서 k200으로 변경
- added features: `batter_season_middle_rate_k200`
- removed features: `batter_season_middle_rate_k20`
- model changes: none

### metric_specific_all

- declared change: ball500·strike200·batter-middle200을 동시에 적용
- added features: `pitcher_season_ball_rate_k500`, `pitcher_season_strike_rate_k200`, `batter_season_middle_rate_k200`
- removed features: `pitcher_season_ball_rate_k20`, `pitcher_season_strike_rate_k20`, `batter_season_middle_rate_k20`
- model changes: none
