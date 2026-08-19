# 097_late_history_triple_repro: Late-history triple promotion reproducibility

- 가설: The complete late-inning pitcher-history block reproduces its small EXP_091 gain in a fresh three-model ensemble run.
- control: `current_triple`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `19766e0787fd`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| current_triple | control: current same-hand pitch-mix triple without count calibration | 0.247471942 | 0.000000000 | 0/1 | 934.716 |
| late_history_triple | add EXP_096 complete late-history feature block | 0.247478540 | 0.000006598 | 0/1 | 932.074 |

## 실제 변경 필드

- `current_triple`: control
- `late_history_triple`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/097_late_history_triple_repro/20260818T080643779299Z_19766e0787fd`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_096`
- 기준 variant: `late_all_three`
- 검증할 변경: Rerun the fixed triple ensemble with current versus complete late-history features only; defer count calibration to a separate experiment.

### current_triple

- role: control

### late_history_triple

- declared change: add EXP_096 complete late-history feature block
- added features: `late_inning_x_pitcher_success`, `late_inning_x_pitcher_reverse`, `late_inning_x_pitcher_middle`
- removed features: none
- model changes: none
