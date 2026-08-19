# 032_segmented_catboost: 상황별 분리 CatBoost

- 가설: game_type 또는 투타 상황별 별도 모델이 전역 트리보다 조건부 상호작용을 더 잘 학습한다
- control: `global_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `2b024d2e84dd`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| global_control | control: 전역 GPU CatBoost | 0.247818247 | 0.000000000 | 0/1 | 796.087 |
| game_i600 | game_type별 600-tree | 0.247842714 | 0.000024466 | 0/1 | 786.293 |
| game_i300 | game_type별 300-tree | 0.247870285 | 0.000052038 | 0/1 | 775.255 |
| top_bottom_i600 | top_bottom별 600-tree | 0.247898064 | 0.000079817 | 0/1 | 764.135 |
| pitcher_hand_i600 | pitcher_hand별 600-tree | 0.247906391 | 0.000088144 | 0/1 | 760.802 |
| game_pitcher_hand_i400 | game_type × pitcher_hand별 400-tree | 0.248051993 | 0.000233745 | 0/1 | 702.516 |

## 실제 변경 필드

- `global_control`: control
- `game_i300`: model.family, model.name, model.params.iterations, model.params.learning_rate, model.segment_columns
- `game_i600`: model.family, model.name, model.segment_columns
- `top_bottom_i600`: model.family, model.name, model.segment_columns
- `pitcher_hand_i600`: model.family, model.name, model.segment_columns
- `game_pitcher_hand_i400`: model.family, model.name, model.params.iterations, model.params.learning_rate, model.segment_columns

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/032_segmented_catboost/20260817T181513441644Z_2b024d2e84dd`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_031`
- 기준 variant: `ensemble_3seed`
- 검증할 변경: GPU CatBoost와 main60을 고정하고 game_type, top_bottom, pitcher_hand 및 game_type×pitcher_hand로 학습 데이터를 분리

### global_control

- role: control

### game_i300

- declared change: game_type별 300-tree
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_segmented`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `seg_gpu_game_i300`
  - `model.params.iterations`: `600` → `300`
  - `model.params.learning_rate`: `0.025` → `0.05`
  - `model.segment_columns`: `None` → `['game_type']`

### game_i600

- declared change: game_type별 600-tree
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_segmented`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `seg_gpu_game_i600`
  - `model.segment_columns`: `None` → `['game_type']`

### top_bottom_i600

- declared change: top_bottom별 600-tree
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_segmented`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `seg_gpu_topbottom_i600`
  - `model.segment_columns`: `None` → `['top_bottom']`

### pitcher_hand_i600

- declared change: pitcher_hand별 600-tree
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_segmented`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `seg_gpu_pitcherhand_i600`
  - `model.segment_columns`: `None` → `['pitcher_hand']`

### game_pitcher_hand_i400

- declared change: game_type × pitcher_hand별 400-tree
- added features: none
- removed features: none
- model changes:
  - `model.family`: `catboost` → `catboost_segmented`
  - `model.name`: `catboost_gpu_d6_i600_lr025_b128` → `seg_gpu_game_pitcherhand_i400`
  - `model.params.iterations`: `600` → `400`
  - `model.params.learning_rate`: `0.025` → `0.04`
  - `model.segment_columns`: `None` → `['game_type', 'pitcher_hand']`
