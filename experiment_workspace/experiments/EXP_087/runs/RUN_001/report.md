# 087_promote_safe_feature_gains: EXP_084·086 피처 개선을 현재 최고 3모델 앙상블에 승격

- 가설: CPU에서 개선된 합법 피처가 GPU와 ExtraTrees에도 유용해 전체 최고를 높인다.
- control: `original_triple`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `906581d7b164`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| same_hand_pitchmix_triple | EXP_084 동일손×과거 구종군 피처 3개 승격 | 0.247471431 | -0.000022294 | 1/1 | 934.920 |
| batter_exact_triple | 동일손×구종군과 EXP_086 정확 타자 시즌 상태 동시 승격 | 0.247483625 | -0.000010101 | 1/1 | 930.039 |
| original_triple | control: EXP_080 count+hands triple | 0.247493726 | 0.000000000 | 0/1 | 925.996 |

## 실제 변경 필드

- `original_triple`: control
- `same_hand_pitchmix_triple`: features.custom, features.description, features.expected_count, features.name
- `batter_exact_triple`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/087_promote_safe_feature_gains/20260818T061615540516Z_906581d7b164`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_086`
- 기준 variant: `batter_exact`
- 검증할 변경: Fix EXP_080 triple model; compare original count+hands, same-hand pitchmix, and same-hand pitchmix plus exact batter snapshot feature sets.

### original_triple

- role: control

### same_hand_pitchmix_triple

- declared change: EXP_084 동일손×과거 구종군 피처 3개 승격
- added features: `same_hand_x_fastball`, `same_hand_x_breaking`, `same_hand_x_offspeed`
- removed features: none
- model changes: none

### batter_exact_triple

- declared change: 동일손×구종군과 EXP_086 정확 타자 시즌 상태 동시 승격
- added features: `batter_season_n_exact`, `batter_season_success_rate_exact_k20`, `same_hand_x_fastball`, `same_hand_x_breaking`, `same_hand_x_offspeed`
- removed features: `batter_season_n`, `batter_season_success_rate_k20`
- model changes: none
