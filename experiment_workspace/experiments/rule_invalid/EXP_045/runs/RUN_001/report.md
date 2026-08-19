# 045_cpu_ewma: CPU 지수감쇠 최근 제구

- 가설: EWMA가 고정 rolling보다 최근성과 장기성을 잘 균형화한다
- control: `main77_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `f5fea1770c9b`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| best_three | 상관 최상 EWMA 세 개 추가 | 0.246930345 | -0.000007786 | 1/1 | 1151.522 |
| main77_control | control: 고정 rolling | 0.246938131 | 0.000000000 | 0/1 | 1148.405 |
| pitcher_success05 | 투수 success EWMA 0.05 추가 | 0.246939864 | 0.000001733 | 0/1 | 1147.712 |
| all_six | EWMA 여섯 개 모두 추가 | 0.246941977 | 0.000003846 | 0/1 | 1146.866 |
| pitcher_reverse05 | 투수 reverse EWMA 0.05 추가 | 0.246954130 | 0.000015999 | 0/1 | 1142.001 |
| batter_success20 | 타자 success EWMA 0.20 추가 | 0.246962277 | 0.000024147 | 0/1 | 1138.739 |

## 실제 변경 필드

- `main77_control`: control
- `pitcher_success05`: features.custom, features.description, features.expected_count, features.name
- `batter_success20`: features.custom, features.description, features.expected_count, features.name
- `pitcher_reverse05`: features.custom, features.description, features.expected_count, features.name
- `best_three`: features.custom, features.description, features.expected_count, features.name
- `all_six`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/045_cpu_ewma/20260817T193621460072Z_f5fea1770c9b`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_044`
- 기준 variant: `main77_control`
- 검증할 변경: CPU main77을 고정하고 투수 success EWMA 0.05·0.10, 타자 success EWMA 0.10·0.20, 투수 reverse EWMA 0.05·0.10만 개별·조합 추가

### main77_control

- role: control

### pitcher_success05

- declared change: 투수 success EWMA 0.05 추가
- added features: `pitcher_success_ewm05`
- removed features: none
- model changes: none

### batter_success20

- declared change: 타자 success EWMA 0.20 추가
- added features: `batter_success_ewm20`
- removed features: none
- model changes: none

### pitcher_reverse05

- declared change: 투수 reverse EWMA 0.05 추가
- added features: `pitcher_reverse_ewm05`
- removed features: none
- model changes: none

### best_three

- declared change: 상관 최상 EWMA 세 개 추가
- added features: `pitcher_success_ewm05`, `batter_success_ewm20`, `pitcher_reverse_ewm05`
- removed features: none
- model changes: none

### all_six

- declared change: EWMA 여섯 개 모두 추가
- added features: `pitcher_success_ewm05`, `pitcher_success_ewm10`, `batter_success_ewm10`, `batter_success_ewm20`, `pitcher_reverse_ewm05`, `pitcher_reverse_ewm10`
- removed features: none
- model changes: none
