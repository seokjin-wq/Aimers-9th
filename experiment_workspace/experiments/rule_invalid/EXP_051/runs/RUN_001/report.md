# exp_051: global reverse rolling windows

- 가설: 전역 최근 역방향 비율이 직전 경기 환경과 scorer 경향을 보완해 Brier를 낮춘다
- control: `control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `6d6b8ce12132`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| control | control: EXP050 d6 i600 + global200 success | 0.246647686 | 0.000000000 | 0/1 | 1264.673 |
| reverse200 | global recent200 reverse 추가 | 0.246669225 | 0.000021540 | 0/1 | 1256.051 |
| reverse300 | global recent300 reverse 추가 | 0.246672130 | 0.000024444 | 0/1 | 1254.888 |
| reverse150 | global recent150 reverse 추가 | 0.246672475 | 0.000024789 | 0/1 | 1254.750 |
| reverse50 | global recent50 reverse 추가 | 0.246675197 | 0.000027511 | 0/1 | 1253.660 |
| reverse100 | global recent100 reverse 추가 | 0.246675221 | 0.000027535 | 0/1 | 1253.650 |

## 실제 변경 필드

- `control`: control
- `reverse50`: features.custom, features.description, features.expected_count, features.name
- `reverse100`: features.custom, features.description, features.expected_count, features.name
- `reverse150`: features.custom, features.description, features.expected_count, features.name
- `reverse200`: features.custom, features.description, features.expected_count, features.name
- `reverse300`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/exp_051/20260817T202228812876Z_6d6b8ce12132`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_050`
- 기준 variant: `d6_i600`
- 검증할 변경: EXP050의 main81·CPU d6 i600을 고정하고 global reverse rolling window 50·100·150·200·300만 하나씩 추가

### control

- role: control

### reverse50

- declared change: global recent50 reverse 추가
- added features: `global_recent50_reverse`
- removed features: none
- model changes: none

### reverse100

- declared change: global recent100 reverse 추가
- added features: `global_recent100_reverse`
- removed features: none
- model changes: none

### reverse150

- declared change: global recent150 reverse 추가
- added features: `global_recent150_reverse`
- removed features: none
- model changes: none

### reverse200

- declared change: global recent200 reverse 추가
- added features: `global_recent200_reverse`
- removed features: none
- model changes: none

### reverse300

- declared change: global recent300 reverse 추가
- added features: `global_recent300_reverse`
- removed features: none
- model changes: none
