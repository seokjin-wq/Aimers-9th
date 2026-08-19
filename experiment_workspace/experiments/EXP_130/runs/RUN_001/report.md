# 130_count_trend_estimator: Count trend estimator final ablation

- 가설: OLS or endpoint count-relative slopes from all official 2019-2023 seasons will improve the EXP_129 WLS trend without using evaluation-row information.
- control: `wls_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `032b2992ab80`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| ols_slope | change only trend estimator from count-weighted WLS to equal-season OLS | 0.247445149 | -0.000000050 | 1/1 | 945.441 |
| wls_control | control: EXP_129 count-weighted linear slope | 0.247445200 | 0.000000000 | 0/1 | 945.421 |
| endpoint_slope | change only trend estimator to 2019-to-2023 endpoint slope | 0.247445473 | 0.000000274 | 0/1 | 945.311 |

## 실제 변경 필드

- `wls_control`: control
- `ols_slope`: model.name, model.trend_method
- `endpoint_slope`: model.name, model.trend_method

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/130_count_trend_estimator/20260818T143419094274Z_032b2992ab80`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_129`
- 기준 variant: `shrinkage_0`
- 검증할 변경: Fix EXP_129 shrinkage 0, trend strength 1.0, features, models, weights, and calibration; vary only count trend estimator among WLS, OLS, and first-to-last endpoint slope.

### wls_control

- role: control

### ols_slope

- declared change: change only trend estimator from count-weighted WLS to equal-season OLS
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_k0` → `triple_count_trend_ols`
  - `model.trend_method`: `None` → `ols`

### endpoint_slope

- declared change: change only trend estimator to 2019-to-2023 endpoint slope
- added features: none
- removed features: none
- model changes:
  - `model.name`: `triple_count_trend_k0` → `triple_count_trend_endpoint`
  - `model.trend_method`: `None` → `endpoint`
