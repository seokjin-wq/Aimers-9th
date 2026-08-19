# EXP_015 decision

- decision: `adopt`
- selected variant: `shift_m010`
- based on run: `RUN_001`
- comparison basis: `EXP_014`
- reference variant: `main60_control`
- decided at: `2026-08-17T16:34:36.913615+00:00`

## Ablation

main55+count CatBoost를 고정하고 prediction shift만 0, -0.005, -0.010, 과거-fold -0.0113955, -0.015로 변경

## Result

- selected Brier: `0.2478754923`
- delta Brier vs control: `-9.26476e-05`
- competition score: `773.1709037273`

## Reason

shift -0.010이 Brier를 0.000092648 개선해 채택하며 과거-fold 고정 shift -0.0113955도 거의 같은 성능으로 누수 없는 근거를 확인
