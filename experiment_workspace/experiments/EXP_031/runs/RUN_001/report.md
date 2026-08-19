# 031_gpu_seed_ensemble: GPU CatBoost seed 앙상블

- 가설: GPU 학습 변동을 여러 seed 평균으로 줄이면 단일 GPU 모델보다 Brier가 개선된다
- control: `single_seed_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `7b468a3b3176`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| ensemble_3seed | GPU 3 seed 평균 | 0.247803944 | -0.000013604 | 1/1 | 801.812 |
| ensemble_5seed | GPU 5 seed 평균 | 0.247809767 | -0.000007781 | 1/1 | 799.481 |
| single_seed_control | control: GPU seed42 단일 | 0.247817548 | 0.000000000 | 0/1 | 796.367 |

## 실제 변경 필드

- `single_seed_control`: control
- `ensemble_3seed`: model.family, model.name, model.params.random_seed, model.seeds
- `ensemble_5seed`: model.family, model.name, model.params.random_seed, model.seeds

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/031_gpu_seed_ensemble/20260817T181030793669Z_7b468a3b3176`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_030`
- 기준 variant: `main60_control`
- 검증할 변경: GPU depth6 600 lr0.025와 main60을 고정하고 3-seed 및 5-seed 확률 평균만 비교

### single_seed_control

- role: control

### ensemble_3seed

- declared change: GPU 3 seed 평균
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_ensemble`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catboost_gpu_ensemble3`
  - `model.params.random_seed`: `42` → `None`
  - `model.seeds`: `None` → `[17, 42, 97]`

### ensemble_5seed

- declared change: GPU 5 seed 평균
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_ensemble`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `catboost_gpu_ensemble5`
  - `model.params.random_seed`: `42` → `None`
  - `model.seeds`: `None` → `[7, 17, 42, 97, 2025]`
