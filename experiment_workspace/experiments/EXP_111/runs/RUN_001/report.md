# 111_promote_cpu_subsample08: Subsample 0.8 promotion to corrected triple blend

- 가설: Replacing only the CPU CatBoost component with the EXP_109 subsample=0.8 winner will transfer its holdout gain into the rule-compliant corrected triple blend.
- control: `triple_sub07_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `6b8c7bc887af`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| triple_cpu_sub08 | CPU CatBoost subsample 0.7 -> 0.8 only | 0.247458679 | -0.000004024 | 1/1 | 940.025 |
| triple_sub07_control | control: EXP_101 corrected triple with CPU subsample=0.7 | 0.247462703 | 0.000000000 | 0/1 | 938.414 |

## 실제 변경 필드

- `triple_sub07_control`: control
- `triple_cpu_sub08`: model.cpu_params.subsample, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/111_promote_cpu_subsample08/20260818T105129208491Z_6b8c7bc887af`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_101`
- 기준 variant: `catshift_m0095`
- 검증할 변경: Keep main72 features, GPU CatBoost, ExtraTrees, 45/40/15 weights, count residual correction k=500, scales, and shifts fixed; change only CPU CatBoost subsample from 0.7 to 0.8.

### triple_sub07_control

- role: control

### triple_cpu_sub08

- declared change: CPU CatBoost subsample 0.7 -> 0.8 only
- added features: none
- removed features: none
- model changes:
  - `model.cpu_params.subsample`: `0.7` → `0.8`
  - `model.name`: `triple_group_count_k500_catshift_m0095` → `triple_group_count_k500_catshift_m0095_cpu_sub08`
