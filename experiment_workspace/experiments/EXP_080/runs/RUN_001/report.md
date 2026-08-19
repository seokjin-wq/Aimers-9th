# 080_count_hands_triple_promotion: 카운트×양손 범주 피처의 3모델 앙상블 승격

- 가설: CPU CatBoost에서 확인된 카운트×양손 범주 상호작용이 CPU·GPU·ExtraTrees 앙상블에서도 전체 Brier를 개선한다.
- control: `old_main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `08dcec119fe1`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_hands_promoted | control 대비 count_state·pitcher_hand·batter_hand categorical 추가 | 0.247493806 | -0.000002941 | 1/1 | 925.964 |
| old_main69_control | control: EXP_072 재현, 기존 categorical 4개 | 0.247496747 | 0.000000000 | 0/1 | 924.786 |

## 실제 변경 필드

- `old_main69_control`: control
- `count_hands_promoted`: features.categorical, features.description, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/080_count_hands_triple_promotion/20260818T051741579377Z_08dcec119fe1`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_072`
- 기준 variant: `main69_control`
- 검증할 변경: Fix triple CPU45/GPU40/Extra15; compare old main69 against only the count+both-hands categorical treatment.

### old_main69_control

- role: control

### count_hands_promoted

- declared change: control 대비 count_state·pitcher_hand·batter_hand categorical 추가
- added features: none
- removed features: none
- model changes: none
