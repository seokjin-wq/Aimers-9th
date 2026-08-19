# 035_recent_window_search: 최근 투구 rolling 창 탐색

- 가설: 투수 장기 창과 타자 단기 창이 main68을 보완한다
- control: `main68_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `3614fb04c38e`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| add_all_extensions | 투수 20·30·50 및 타자 2·8투구 모두 추가 | 0.247169078 | -0.000117191 | 1/1 | 1055.955 |
| add_pitcher20_50 | 투수 최근 20·50투구 추가 | 0.247184572 | -0.000101698 | 1/1 | 1049.753 |
| add_pitcher20 | 투수 최근 20투구 추가 | 0.247208811 | -0.000077458 | 1/1 | 1040.050 |
| add_pitcher50 | 투수 최근 50투구 추가 | 0.247210455 | -0.000075814 | 1/1 | 1039.391 |
| main68_control | control: 직전 및 3·5·10투구 | 0.247286269 | 0.000000000 | 0/1 | 1009.042 |
| add_batter2_8 | 타자 최근 2·8투구 추가 | 0.247294207 | 0.000007937 | 0/1 | 1005.865 |

## 실제 변경 필드

- `main68_control`: control
- `add_pitcher20`: features.custom, features.description, features.expected_count, features.name
- `add_pitcher50`: features.custom, features.description, features.expected_count, features.name
- `add_pitcher20_50`: features.custom, features.description, features.expected_count, features.name
- `add_batter2_8`: features.custom, features.description, features.expected_count, features.name
- `add_all_extensions`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/035_recent_window_search/20260817T182956906211Z_3614fb04c38e`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_034`
- 기준 variant: `entity_recent_all`
- 검증할 변경: main68과 GPU CatBoost를 고정하고 투수 recent20·30·50 및 타자 recent2·8 rolling 피처만 개별·조합 추가

### main68_control

- role: control

### add_pitcher20

- declared change: 투수 최근 20투구 추가
- added features: `pitcher_recent20_pitch_success`
- removed features: none
- model changes: none

### add_pitcher50

- declared change: 투수 최근 50투구 추가
- added features: `pitcher_recent50_pitch_success`
- removed features: none
- model changes: none

### add_pitcher20_50

- declared change: 투수 최근 20·50투구 추가
- added features: `pitcher_recent20_pitch_success`, `pitcher_recent50_pitch_success`
- removed features: none
- model changes: none

### add_batter2_8

- declared change: 타자 최근 2·8투구 추가
- added features: `batter_recent2_pitch_success`, `batter_recent8_pitch_success`
- removed features: none
- model changes: none

### add_all_extensions

- declared change: 투수 20·30·50 및 타자 2·8투구 모두 추가
- added features: `pitcher_recent20_pitch_success`, `pitcher_recent30_pitch_success`, `pitcher_recent50_pitch_success`, `batter_recent2_pitch_success`, `batter_recent8_pitch_success`
- removed features: none
- model changes: none
