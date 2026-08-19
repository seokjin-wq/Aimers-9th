# 121_histgb_fourth_blend: Rule-compliant HistGB fourth-model blend

- 가설: A small HistGradientBoosting component can reduce correlated CatBoost/ExtraTrees errors despite weaker standalone Brier, improving the reliability-enhanced ensemble through diversity.
- control: `hist_weight_0_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `1bfa7ba908c8`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| hist_weight_0_control | control: train HistGB but assign weight 0; CPU/GPU/Extra=50/35/15 | 0.247451494 | 0.000000000 | 0/1 | 942.901 |
| hist_weight_025 | replace 2.5% ExtraTrees weight with HistGB only | 0.247453802 | 0.000002308 | 0/1 | 941.977 |
| hist_weight_05 | replace 5% ExtraTrees weight with HistGB only | 0.247456949 | 0.000005455 | 0/1 | 940.717 |

## 실제 변경 필드

- `hist_weight_0_control`: control
- `hist_weight_025`: model.extra_weight, model.hist_weight, model.name
- `hist_weight_05`: model.extra_weight, model.hist_weight, model.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/121_histgb_fourth_blend/20260818T124353100500Z_1bfa7ba908c8`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_117`
- 기준 variant: `weights_50_35_15`
- 검증할 변경: Fix main78 features, CPU/GPU weights 50/35, all component parameters and calibration; replace only 0%, 2.5%, or 5% of the ExtraTrees weight with a fixed HistGB component trained on official pre-validation data.

### hist_weight_0_control

- role: control

### hist_weight_025

- declared change: replace 2.5% ExtraTrees weight with HistGB only
- added features: none
- removed features: none
- model changes:
  - `model.extra_weight`: `0.15` → `0.125`
  - `model.hist_weight`: `0.0` → `0.025`
  - `model.name`: `quad_hist0_count_m0095_sub08_w50_35_15` → `quad_hist025_count_m0095_sub08`

### hist_weight_05

- declared change: replace 5% ExtraTrees weight with HistGB only
- added features: none
- removed features: none
- model changes:
  - `model.extra_weight`: `0.15` → `0.1`
  - `model.hist_weight`: `0.0` → `0.05`
  - `model.name`: `quad_hist0_count_m0095_sub08_w50_35_15` → `quad_hist05_count_m0095_sub08`
