# EXP_036 decision

- decision: `adopt`
- selected variant: `reverse_short`
- based on run: `RUN_001`
- comparison basis: `EXP_035`
- reference variant: `add_all_extensions`
- decided at: `2026-08-17T18:36:46.566121+00:00`

## Ablation

main73과 GPU CatBoost를 고정하고 투수 reverse 직전·3·5·10·20·50투구 창의 포함 조합만 변경

## Result

- selected Brier: `0.2469380019`
- delta Brier vs control: `-0.0002318994`
- competition score: `1148.4568692102`

## Reason

투수 reverse 직전·3·5·10 창이 Brier 0.2469380, BSS 1148.46으로 장기·전체 reverse 조합보다 우수
