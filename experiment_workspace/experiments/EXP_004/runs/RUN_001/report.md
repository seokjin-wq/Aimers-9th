# 004_native_categorical: CatBoost 네이티브 범주 처리

- 가설: 문자열 범주를 CatBoost ordered statistics로 처리하면 ordinal 숫자 처리보다 2024 Brier가 개선된다
- control: `ordinal_control`
- 변경 허용 범위: `model`
- 검증 시즌: `[2024]`
- 분할 규칙: `before_validation_season`
- calibration: `none`
- config hash: `b6f93d4ab123`

## 결과

| variant | change | mean_brier | delta_brier_vs_control | seasons_improved | mean_brier_skill_score |
| --- | --- | --- | --- | --- | --- |
| native_basic | 동일 3개 범주를 CatBoost native categorical로 처리 | 0.248009268 | -0.000014187 | 1/1 | 719.619 |
| ordinal_control | control: top_bottom, game_type, base_state를 ordinal 숫자로 변환 | 0.248023454 | 0.000000000 | 0/1 | 713.940 |

## 실제 변경 필드

- `ordinal_control`: control
- `native_basic`: model.name, model.native_categorical

## 판정 메모

Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.
자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.

- 결론:
- 다음 실험:

원본 산출물: `/home/chanheo/lgaimers/experiment_workspace/runs/004_native_categorical/20260817T153756417596Z_b6f93d4ab123`

## 실험 계보와 정확한 ablation

- 비교 기준: `EXP_003`
- 기준 variant: `main55_control`
- 검증할 변경: main55와 CatBoost 파라미터를 고정하고 범주 전처리만 ordinal encoding에서 CatBoost native categorical로 변경

### ordinal_control

- role: control

### native_basic

- declared change: 동일 3개 범주를 CatBoost native categorical로 처리
- added features: none
- removed features: none
- model changes:
  - `model.name`: `catboost_default` → `catboost_native_300`
  - `model.native_categorical`: `None` → `True`
