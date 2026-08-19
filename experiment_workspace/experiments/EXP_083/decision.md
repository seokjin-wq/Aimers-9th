# EXP_083 decision

- decision: `reject`
- selected variant: `count_hands_control`
- based on run: `RUN_001`
- comparison basis: `EXP_080`
- reference variant: `count_hands_promoted`
- decided at: `2026-08-18T05:56:14.148968+00:00`

## Ablation

Fix the EXP_080 count+hands CPU base; add only row-local weighted recent success, middle, quality, or horizon-spread features.

## Result

- selected Brier: `0.2475158585`
- delta Brier vs control: `0.0`
- competition score: `917.135588661`

## Reason

최근 성공·가운데 비율의 모든 행 단위 요약이 control BSS 917.14보다 낮았다(최선 900.72). 기존 원시 최근경기 피처의 중복·잡음으로 판단한다.
