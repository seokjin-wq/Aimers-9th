# EXP_004 decision

- decision: `adopt`
- selected variant: `native_basic`
- based on run: `RUN_001`
- comparison basis: `EXP_003`
- reference variant: `main55_control`
- decided at: `2026-08-17T15:38:52.980997+00:00`

## Ablation

main55와 CatBoost 파라미터를 고정하고 범주 전처리만 ordinal encoding에서 CatBoost native categorical로 변경

## Result

- selected Brier: `0.2480092675`
- delta Brier vs control: `-1.41869e-05`
- competition score: `719.6194426463`

## Reason

동일 main55에서 CatBoost native categorical 처리가 ordinal 대비 Brier를 0.000014187 개선해 다음 실험 기준으로 채택
