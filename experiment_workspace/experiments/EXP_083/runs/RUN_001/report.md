# 083_recent_form_blends: 평가 행 자체의 사전 제공 최근경기 통계 조합

- 가설: 직전 1·3·5경기 성공·가운데 비율을 안정적으로 요약하면 개별 원시 horizon보다 일반화가 좋아진다.
- control: `count_hands_control`
- 변경 허용 범위: `features`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `4dffdaaab882`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| count_hands_control | control: EXP_080 CPU count+hands base | 0.247515859 | 0.000000000 | 0/1 | 917.136 |
| recent_success_blend | 0.2×직전1 + 0.5×직전3 + 0.3×직전5 경기 성공률 추가 | 0.247556858 | 0.000040999 | 0/1 | 900.723 |
| recent_spans | 직전1-직전5 성공률·가운데공 절대차 추가 | 0.247557198 | 0.000041339 | 0/1 | 900.587 |
| recent_all | 다섯 최근 폼 요약을 모두 추가 | 0.247565507 | 0.000049649 | 0/1 | 897.261 |
| recent_middle_blend | 동일 가중치의 최근 가운데공 비율 추가 | 0.247568580 | 0.000052722 | 0/1 | 896.031 |
| recent_quality | 최근 성공률 요약에서 가운데공 요약을 뺀 quality 추가 | 0.247570387 | 0.000054528 | 0/1 | 895.307 |
| recent_both_blends | 최근 성공률·가운데공 가중 요약 동시 추가 | 0.247580081 | 0.000064222 | 0/1 | 891.427 |

## 실제 변경 필드

- `count_hands_control`: control
- `recent_success_blend`: features.custom, features.description, features.expected_count, features.name
- `recent_middle_blend`: features.custom, features.description, features.expected_count, features.name
- `recent_both_blends`: features.custom, features.description, features.expected_count, features.name
- `recent_quality`: features.custom, features.description, features.expected_count, features.name
- `recent_spans`: features.custom, features.description, features.expected_count, features.name
- `recent_all`: features.custom, features.description, features.expected_count, features.name

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/083_recent_form_blends/20260818T054925536782Z_4dffdaaab882`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_080`
- 기준 variant: `count_hands_promoted`
- 검증할 변경: Fix the EXP_080 count+hands CPU base; add only row-local weighted recent success, middle, quality, or horizon-spread features.

### count_hands_control

- role: control

### recent_success_blend

- declared change: 0.2×직전1 + 0.5×직전3 + 0.3×직전5 경기 성공률 추가
- added features: `recent_success_blend_135`
- removed features: none
- model changes: none

### recent_middle_blend

- declared change: 동일 가중치의 최근 가운데공 비율 추가
- added features: `recent_middle_blend_135`
- removed features: none
- model changes: none

### recent_both_blends

- declared change: 최근 성공률·가운데공 가중 요약 동시 추가
- added features: `recent_success_blend_135`, `recent_middle_blend_135`
- removed features: none
- model changes: none

### recent_quality

- declared change: 최근 성공률 요약에서 가운데공 요약을 뺀 quality 추가
- added features: `recent_quality_blend_135`
- removed features: none
- model changes: none

### recent_spans

- declared change: 직전1-직전5 성공률·가운데공 절대차 추가
- added features: `recent_success_span_15`, `recent_middle_span_15`
- removed features: none
- model changes: none

### recent_all

- declared change: 다섯 최근 폼 요약을 모두 추가
- added features: `recent_success_blend_135`, `recent_middle_blend_135`, `recent_quality_blend_135`, `recent_success_span_15`, `recent_middle_span_15`
- removed features: none
- model changes: none
