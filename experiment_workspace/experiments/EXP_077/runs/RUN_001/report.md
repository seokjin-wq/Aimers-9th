# 077_direct_brier_revisit: 강화 피처에서 CatBoost RMSE 직접 최적화 재검증

- 가설: 당해 시즌 상태와 최근성 가중치가 추가된 환경에서는 제곱오차를 직접 학습하는 회귀 CatBoost가 Logloss보다 Brier를 낮추거나 앙상블 다양성을 제공한다.
- control: `logloss_d8_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `4fed9cc4a8c6`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| logloss_d8_control | control: Logloss depth8 300 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| rmse_d8_scaled | RMSE depth8에 classifier와 동일한 scale1.06 shift-0.008 | 0.247565024 | 0.000027303 | 0/1 | 897.454 |
| rmse_d9_i200 | RMSE 회귀 depth9 200 | 0.247647571 | 0.000109851 | 0/1 | 864.410 |
| rmse_d7_i500 | RMSE 회귀 depth7 500 | 0.247661180 | 0.000123459 | 0/1 | 858.962 |
| rmse_d8_i300 | RMSE 회귀 depth8 300 | 0.247664822 | 0.000127101 | 0/1 | 857.504 |

## 실제 변경 필드

- `logloss_d8_control`: control
- `rmse_d7_i500`: model.family, model.name, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.learning_rate, model.params.loss_function, model.prediction_scale, model.prediction_shift
- `rmse_d8_i300`: model.family, model.name, model.params.eval_metric, model.params.loss_function, model.prediction_scale, model.prediction_shift
- `rmse_d8_scaled`: model.family, model.name, model.params.eval_metric, model.params.loss_function
- `rmse_d9_i200`: model.family, model.name, model.params.depth, model.params.eval_metric, model.params.iterations, model.params.loss_function, model.prediction_scale, model.prediction_shift

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/077_direct_brier_revisit/20260818T050019074391Z_4fed9cc4a8c6`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_072`
- 기준 variant: `main69_control`
- 검증할 변경: Fix main69; compare Logloss d8 against RMSE d7/d8 and affine-scaled RMSE d8, all with season decay 0.85.

### logloss_d8_control

- role: control

### rmse_d7_i500

- declared change: RMSE 회귀 depth7 500
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_regressor`
  - `model.name`: `catboost_d8_decay085` → `catreg_d7_i500_decay85`
  - `model.params.depth`: `8` → `7`
  - `model.params.eval_metric`: `BrierScore` → `RMSE`
  - `model.params.iterations`: `300` → `500`
  - `model.params.learning_rate`: `0.035` → `0.03`
  - `model.params.loss_function`: `Logloss` → `RMSE`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### rmse_d8_i300

- declared change: RMSE 회귀 depth8 300
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_regressor`
  - `model.name`: `catboost_d8_decay085` → `catreg_d8_i300_decay85`
  - `model.params.eval_metric`: `BrierScore` → `RMSE`
  - `model.params.loss_function`: `Logloss` → `RMSE`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`

### rmse_d8_scaled

- declared change: RMSE depth8에 classifier와 동일한 scale1.06 shift-0.008
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_regressor`
  - `model.name`: `catboost_d8_decay085` → `catreg_d8_i300_decay85_scaled`
  - `model.params.eval_metric`: `BrierScore` → `RMSE`
  - `model.params.loss_function`: `Logloss` → `RMSE`

### rmse_d9_i200

- declared change: RMSE 회귀 depth9 200
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_regressor`
  - `model.name`: `catboost_d8_decay085` → `catreg_d9_i200_decay85`
  - `model.params.depth`: `8` → `9`
  - `model.params.eval_metric`: `BrierScore` → `RMSE`
  - `model.params.iterations`: `300` → `200`
  - `model.params.loss_function`: `Logloss` → `RMSE`
  - `model.prediction_scale`: `1.06` → `None`
  - `model.prediction_shift`: `-0.008` → `None`
