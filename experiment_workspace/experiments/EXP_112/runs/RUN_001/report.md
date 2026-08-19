# 112_history_reliability: Row-local history reliability representation

- 가설: Explicit sample-size buckets and reliability-weighted as-of rates will make the latest CatBoost robust to the 2024 new-player and small-history population identified in EDA.
- control: `main72_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `5e2601454495`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| history_reliability | add six row-local reliability and reliability-weighted rate features only | 0.247487993 | -0.000016179 | 1/1 | 928.291 |
| main72_control | control: EXP_109 CPU winner | 0.247504172 | 0.000000000 | 0/1 | 921.814 |
| history_buckets | add pitcher/batter as-of history-size categorical buckets only | 0.247562787 | 0.000058615 | 0/1 | 898.350 |
| buckets_plus_reliability | add both history-size buckets and reliability features | 0.247564974 | 0.000060803 | 0/1 | 897.474 |

## 실제 변경 필드

- `main72_control`: control
- `history_buckets`: features.categorical, features.custom, features.description, features.expected_count, features.name
- `history_reliability`: features.custom, features.description, features.expected_count, features.name
- `buckets_plus_reliability`: features.categorical, features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/112_history_reliability/20260818T111820292645Z_5e2601454495`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_109`
- 기준 variant: `subsample_08`
- 검증할 변경: Fix CPU CatBoost subsample=0.8 and main72; add only two categorical history-size buckets, only six numeric reliability features, or both blocks.

### main72_control

- role: control

### history_buckets

- declared change: add pitcher/batter as-of history-size categorical buckets only
- added features: `pitcher_history_bucket`, `batter_history_bucket`
- removed features: none
- model changes: none

### history_reliability

- declared change: add six row-local reliability and reliability-weighted rate features only
- added features: `pitcher_history_reliability_k100`, `batter_history_reliability_k100`, `pitcher_success_x_reliability`, `batter_success_x_reliability`, `pitcher_reverse_x_reliability`, `pitcher_middle_x_reliability`
- removed features: none
- model changes: none

### buckets_plus_reliability

- declared change: add both history-size buckets and reliability features
- added features: `pitcher_history_bucket`, `batter_history_bucket`, `pitcher_history_reliability_k100`, `batter_history_reliability_k100`, `pitcher_success_x_reliability`, `batter_success_x_reliability`, `pitcher_reverse_x_reliability`, `pitcher_middle_x_reliability`
- removed features: none
- model changes: none
