# 116_promote_history_reliability: History reliability promotion to corrected triple blend

- 가설: The six row-local reliability features that improved CPU BSS by 6.48 will transfer into the EXP_111 corrected triple blend and set a new compliant best.
- control: `triple_main72_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `a15a958ccc29`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| triple_history_reliability | add six EXP_112 row-local history reliability features only | 0.247457280 | -0.000001064 | 1/1 | 940.585 |
| triple_main72_control | control: EXP_111 new-best triple on main72 | 0.247458344 | 0.000000000 | 0/1 | 940.159 |

## 실제 변경 필드

- `triple_main72_control`: control
- `triple_history_reliability`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/116_promote_history_reliability/20260818T113749850324Z_a15a958ccc29`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_111`
- 기준 variant: `triple_cpu_sub08`
- 검증할 변경: Keep the full EXP_111 triple model, CPU subsample=0.8, weights, calibration, and count residual correction fixed; change only main72 versus main78 reliability features.

### triple_main72_control

- role: control

### triple_history_reliability

- declared change: add six EXP_112 row-local history reliability features only
- added features: `pitcher_history_reliability_k100`, `batter_history_reliability_k100`, `pitcher_success_x_reliability`, `batter_success_x_reliability`, `pitcher_reverse_x_reliability`, `pitcher_middle_x_reliability`
- removed features: none
- model changes: none
