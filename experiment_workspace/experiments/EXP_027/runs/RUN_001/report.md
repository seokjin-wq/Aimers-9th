# 027_catboost_gpu: CatBoost GPU 학습 후보

- 가설: GPU CatBoost의 다른 histogram과 categorical 계산이 CPU 모델보다 낮은 Brier 또는 유용한 앙상블 다양성을 만든다
- control: `cpu_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `81ee32bd2568`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| gpu_d6_i600 | GPU depth6 600 lr0.025 border128 | 0.247815837 | -0.000003191 | 1/1 | 797.052 |
| cpu_control | control: CPU depth6 400 lr0.04 | 0.247819028 | 0.000000000 | 0/1 | 795.774 |
| gpu_d7_i300 | GPU depth7 300 lr0.04 border128 | 0.247819521 | 0.000000493 | 0/1 | 795.577 |
| gpu_d6_i500 | GPU depth6 500 lr0.03 border128 | 0.247838173 | 0.000019145 | 0/1 | 788.110 |
| gpu_d6_i300 | GPU depth6 300 lr0.05 border128 | 0.247853716 | 0.000034688 | 0/1 | 781.888 |
| gpu_d6_i400_b64 | GPU depth6 400 lr0.04 border64 | 0.247860807 | 0.000041779 | 0/1 | 779.049 |
| gpu_d8_i250 | GPU depth8 250 lr0.04 border128 | 0.247868950 | 0.000049922 | 0/1 | 775.790 |

## 실제 변경 필드

- `cpu_control`: control
- `gpu_d6_i300`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.devices, model.params.iterations, model.params.learning_rate, model.params.subsample, model.params.task_type, model.params.thread_count
- `gpu_d6_i500`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.devices, model.params.iterations, model.params.learning_rate, model.params.subsample, model.params.task_type, model.params.thread_count
- `gpu_d6_i600`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.devices, model.params.iterations, model.params.learning_rate, model.params.subsample, model.params.task_type, model.params.thread_count
- `gpu_d7_i300`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.iterations, model.params.subsample, model.params.task_type, model.params.thread_count
- `gpu_d8_i250`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.depth, model.params.devices, model.params.iterations, model.params.subsample, model.params.task_type, model.params.thread_count
- `gpu_d6_i400_b64`: model.name, model.params.bagging_temperature, model.params.bootstrap_type, model.params.border_count, model.params.devices, model.params.subsample, model.params.task_type, model.params.thread_count

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/027_catboost_gpu/20260817T175200760547Z_81ee32bd2568`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_026`
- 기준 variant: `count_k500`
- 검증할 변경: main60과 affine을 고정하고 GPU depth 6~8, iterations 300~600, learning rate 0.025~0.05를 비교

### cpu_control

- role: control

### gpu_d6_i300

- declared change: GPU depth6 300 lr0.05 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_gpu_d6_i300_lr050_b128`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `400` → `300`
  - `model.params.learning_rate`: `0.04` → `0.05`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`

### gpu_d6_i500

- declared change: GPU depth6 500 lr0.03 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_gpu_d6_i500_lr030_b128`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `400` → `500`
  - `model.params.learning_rate`: `0.04` → `0.03`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`

### gpu_d6_i600

- declared change: GPU depth6 600 lr0.025 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_gpu_d6_i600_lr025_b128`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `400` → `600`
  - `model.params.learning_rate`: `0.04` → `0.025`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`

### gpu_d7_i300

- declared change: GPU depth7 300 lr0.04 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_gpu_d7_i300_lr040_b128`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.depth`: `6` → `7`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `400` → `300`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`

### gpu_d8_i250

- declared change: GPU depth8 250 lr0.04 border128
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_gpu_d8_i250_lr040_b128`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `128`
  - `model.params.depth`: `6` → `8`
  - `model.params.devices`: `None` → `0`
  - `model.params.iterations`: `400` → `250`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`

### gpu_d6_i400_b64

- declared change: GPU depth6 400 lr0.04 border64
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_top_d6_i400_lr040` → `catboost_gpu_d6_i400_lr040_b64`
  - `model.params.bagging_temperature`: `None` → `1.0`
  - `model.params.bootstrap_type`: `None` → `Bayesian`
  - `model.params.border_count`: `None` → `64`
  - `model.params.devices`: `None` → `0`
  - `model.params.subsample`: `0.7` → `None`
  - `model.params.task_type`: `CPU` → `GPU`
  - `model.params.thread_count`: `8` → `None`
