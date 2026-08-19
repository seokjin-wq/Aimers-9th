# 091_promote_late_history: 후반 투수이력 피처의 앙상블 승격

- 가설: EXP_090 피처 개선이 현재 3모델 앙상블에서도 유지된다.
- control: `current_triple_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `6b47f1555a72`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| late_history_triple | EXP_090 후반×투수이력 3개를 triple에 승격 | 0.247478778 | -0.000001898 | 1/1 | 931.979 |
| current_triple_control | control: EXP_087 same-hand pitchmix triple | 0.247480676 | 0.000000000 | 0/1 | 931.219 |

## 실제 변경 필드

- `current_triple_control`: control
- `late_history_triple`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/091_promote_late_history/20260818T070728084855Z_6b47f1555a72`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_090`
- 기준 variant: `late_pitcher_history`
- 검증할 변경: Fix the EXP_087 triple model and compare only the original same-hand features against the EXP_090 late-history feature addition.

### current_triple_control

- role: control

### late_history_triple

- declared change: EXP_090 후반×투수이력 3개를 triple에 승격
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none
