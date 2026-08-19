# 016_seed_ensemble: CatBoost seed 확률 앙상블

- 가설: 서로 다른 seed CatBoost의 확률 평균이 단일 모델 분산을 줄여 2024 Brier를 개선한다
- control: `single_seed_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `ff8e8b7b4da5`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| single_seed_control | control: seed42 단일 모델 + shift | 0.247875492 | 0.000000000 | 0/1 | 773.171 |
| ensemble_3seed | seed 17·42·73 확률 평균 + shift | 0.247901713 | 0.000026220 | 0/1 | 762.675 |
| ensemble_5seed | seed 7·17·42·73·101 확률 평균 + shift | 0.247906397 | 0.000030905 | 0/1 | 760.799 |

## 실제 변경 필드

- `single_seed_control`: control
- `ensemble_3seed`: model.family, model.name, model.params.random_seed, model.seeds
- `ensemble_5seed`: model.family, model.name, model.params.random_seed, model.seeds

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/016_seed_ensemble/20260817T163456326052Z_ff8e8b7b4da5`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_015`
- 기준 variant: `shift_m010`
- 검증할 변경: main55+count와 -0.010 shift를 고정하고 단일 seed 대비 3-seed, 5-seed 확률 평균만 비교

### single_seed_control

- role: control

### ensemble_3seed

- declared change: seed 17·42·73 확률 평균 + shift
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_ensemble`
  - `model.name`: `catboost_native_shift_m010` → `catboost_ensemble3_shift`
  - `model.params.random_seed`: `42` → `None`
  - `model.seeds`: `None` → `[17, 42, 73]`

### ensemble_5seed

- declared change: seed 7·17·42·73·101 확률 평균 + shift
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_ensemble`
  - `model.name`: `catboost_native_shift_m010` → `catboost_ensemble5_shift`
  - `model.params.random_seed`: `42` → `None`
  - `model.seeds`: `None` → `[7, 17, 42, 73, 101]`
