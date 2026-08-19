# 065_context_season_oof: 상황 교차 season-OOF 재검증

- 가설: 학습행의 전체 시즌을 제외한 상황 효과는 자기 정답 지문 없이 안정적 상호작용을 제공한다
- control: `main69_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `d7d0c3b8e547`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| main69_control | control: 합법 main69 | 0.247537721 | 0.000000000 | 0/1 | 908.384 |
| count_out_base_season_oof | season-OOF 볼카운트×아웃×주자 효과 | 0.247552330 | 0.000014610 | 0/1 | 902.536 |
| count_hands_season_oof | season-OOF 볼카운트×손 조합 효과 | 0.247553592 | 0.000015871 | 0/1 | 902.031 |
| game_pressure_season_oof | season-OOF 경기·압박 효과 | 0.247686875 | 0.000149154 | 0/1 | 848.676 |
| all_context_season_oof | season-OOF 네 상황 효과 전체 | 0.247757220 | 0.000219499 | 0/1 | 820.516 |

## 실제 변경 필드

- `main69_control`: control
- `count_hands_season_oof`: features.custom, features.description, features.expected_count, features.name
- `count_out_base_season_oof`: features.custom, features.description, features.expected_count, features.name
- `game_pressure_season_oof`: features.custom, features.description, features.expected_count, features.name
- `all_context_season_oof`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/065_context_season_oof/20260818T032811988849Z_d7d0c3b8e547`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_064`
- 기준 variant: `main69_control`
- 검증할 변경: EXP_064와 동일한 네 상황 효과를 leave-one-row-out 대신 leave-one-season-out으로 재계산

### main69_control

- role: control

### count_hands_season_oof

- declared change: season-OOF 볼카운트×손 조합 효과
- added features: `count_hands_target_effect`
- removed features: none
- model changes: none

### count_out_base_season_oof

- declared change: season-OOF 볼카운트×아웃×주자 효과
- added features: `count_out_base_target_effect`
- removed features: none
- model changes: none

### game_pressure_season_oof

- declared change: season-OOF 경기·압박 효과
- added features: `inning_game_target_effect`, `pressure_state_target_effect`
- removed features: none
- model changes: none

### all_context_season_oof

- declared change: season-OOF 네 상황 효과 전체
- added features: `count_hands_target_effect`, `count_out_base_target_effect`, `inning_game_target_effect`, `pressure_state_target_effect`
- removed features: none
- model changes: none
