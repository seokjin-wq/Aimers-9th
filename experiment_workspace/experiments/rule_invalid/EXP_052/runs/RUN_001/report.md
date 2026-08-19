# exp_052: best prediction calibration probe

- 가설: EXP050 최고 모델 예측의 잔여 평균·분산 편향을 보정하면 Brier를 추가로 낮출 수 있다
- control: `best_replay`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `e164ad302fe0`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| best_replay | EXP050 최고 설정을 동일 seed로 재현하고 예측 저장 | 0.246647686 | 0.000000000 | 0/1 | 1264.673 |

## 실제 변경 필드

- `best_replay`: control

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/exp_052/20260817T203128846768Z_e164ad302fe0`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_050`
- 기준 variant: `d6_i600`
- 검증할 변경: EXP050 최고 설정을 그대로 1회 재현하고 2024 row별 예측을 저장하여 affine 보정 가능 범위를 진단

### best_replay

- role: control
