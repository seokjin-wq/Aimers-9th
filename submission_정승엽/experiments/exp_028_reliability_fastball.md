# exp_028 — reliability 피처 + same_hand_x_fastball_rate (기각, 노이즈 수준)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_028
- **날짜 / 담당자**: 2026-08-22 / 야간 자동 실험(팀원 코드 추가 이식)
- **출처**: 팀원 저장소 EXP_112(reliability, Brier -1.62e-5 단독 보고)
  + EXP_084/087(same_hand_x_fastball_rate, 우리는 breaking/offspeed만
  있고 fastball만 빠져 있었음).
- **가설**: exp_027(이번시즌 상태 피처, +77.93)에 이 두 저비용 피처를
  더 얹으면 추가로 소폭 개선될 것 — 팀원 보고에서도 EXP_056(가장 큰
  이득) 이후 추가되어 작지만 양의 기여를 한 축들이었음.
- **기준(baseline)**: exp_027 피처셋(105개), 단일 seed=42, score=818.79
  (`experiments/exp027_run_log.txt`).
- **이번에 바꾸는 것**: `src/features.py`에 7개 컬럼 추가만 함(제거
  없음) — `same_hand_x_fastball_rate` 1개 + reliability 6개
  (`{pitcher,batter}_history_reliability_k100`,
  `{pitcher,batter}_success_x_reliability`,
  `pitcher_reverse_x_reliability`, `pitcher_middle_x_reliability`).
  `DERIVED_COLS`에 편입되어 다른 모든 스크립트에도 자동 반영됨.
- **검증 방법**: exp_027과 동일(2019-2023 학습/2024 검증), 단일
  seed=42로 먼저 확인.
- **누수 위험 검토**: 전부 행-로컬 계산(공식 `asof_*` 컬럼과 고정
  상수 k=100만 사용, fit 불필요) — leak-safe.

## 결과 (실행 후에 작성)

`src/train_exp028_reliability_fastball.py`
(로그: `experiments/exp028_run_log.txt`).

| 변형 | Brier | score | n_features |
| --- | --- | --- | --- |
| exp_027 단독(기준) | 0.247762 | 818.79 | 105 |
| exp_027 + exp_028(7개 신규) | 0.247766 | 817.18 | 112 |

**Δ = -1.61 — 이 프로젝트 노이즈 기준(<2점, exp_016/021/024/025에서
확립)에 들어감. 기각.**

**해석(확정 아님)**: 팀원 저장소에서 이 두 피처가 양의 기여를 보인
건 팀원의 피처셋(78개, `main78_history_reliability`)이 우리의 exp_027
피처셋(112개, 이미 트랙맨 개인별 피처+이번시즌 상태 피처까지 포함)과
상당히 다르기 때문일 수 있다 — 특히 exp_027의 `{entity}_season_n`
피처가 이미 "이 표본을 얼마나 믿을 수 있는가"와 상당 부분 겹치는
정보를 담고 있어서(이번 시즌 표본 수 자체가 낮으면 그 시즌 rate의
신뢰도도 낮다는 걸 트리가 이미 배울 수 있음), reliability 피처가
추가로 줄 수 있는 새 정보가 우리 쪽에선 이미 대부분 소진된 상태였을
가능성. same_hand_x_fastball_rate 쪽은 단일 피처라 영향이 원래도
작을 것으로 예상됐음(팀원 보고도 solo -3.99e-6로 가장 작은 축).

**결론**: 전체 재학습/보정/아카이브 사이클(exp_027 방식, ~1.5-2시간
소요) 진행 안 함 — 기대이득이 노이즈 수준이라 비용 대비 맞지 않음.
코드 자체(`src/features.py`의 7개 컬럼)는 해롭지 않으므로 남겨두되,
프로덕션 champion(exp_027)에는 포함하지 않음.

**다음 가설**: 없음(이 축은 여기서 종료). 다음은 EXP_127류 count-state
시즌추세 보정과 "역방향"(팀원 예측에 우리 보정 얹기) 실험으로 이동.
