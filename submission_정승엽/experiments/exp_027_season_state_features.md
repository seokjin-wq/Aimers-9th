# exp_027 — 이번 시즌(current-season-only) 투수/타자 상태 피처 (팀원 코드에서 이식)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_027
- **날짜 / 담당자**: 2026-08-22 / 사용자 요청 — 팀원(윤석진,
  github `seokjin-wq/Aimers-9th`) 저장소의 `experiment_workspace`
  (독립 실험 프레임워크, EXP_001~EXP_130, 로컬 검증 BSS 945.44,
  실제 LB ~1045)를 분석해 우리 파이프라인에 이식 가능한 기법을 찾고
  적용.
- **출처**: 팀원 저장소 `experiment_workspace/experiments/EXP_056`
  ("현재 시즌 누적 상태") — 팀원의 130개 실험 중 **단일 최대 개선폭**
  (Brier -0.000221, 다른 어떤 단일 기법보다 10배 이상 큼)으로 보고됨.
  탐색 에이전트가 `src/aimers_exp/features.py`를 직접 읽어 정확한
  구현을 확인함(아래 "메커니즘" 참고).
- **가설**: 공식 `asof_pitcher_*`/`asof_batter_*` 컬럼은 전부 **커리어
  누적**(2019년 데뷔 이후 전체)이다. `control_success` 성공률이
  해마다 하락한다는 건 이미 이 프로젝트에서 확인됨(exp_022/023) —
  커리어 평균은 "지금" 투수의 실제 폼보다 항상 약간 높게(낙관적으로)
  잡힐 수 있다. 이걸 보정기(calibration)로만 전역적으로 고치는 대신,
  **투수/타자별로 "이번 시즌만의" 통계**를 명시적 피처로 주면 모델이
  개인별 최근 폼 신호를 직접 학습할 수 있을 것.
- **기준(baseline)**: exp_007/010 챔피언 피처셋(EXP003_FEATURES +
  TRACKMAN_PITCHER_ASOF_COLS, 89개), 단일 seed=42, score=740.86.
- **이번에 바꾸는 것**: 위 89개 피처에 새 피처 16개를 추가만 함(제거
  없음). 모델/하이퍼파라미터 불변.
- **메커니즘(leak-safe, `src/season_state_features.py`)**: 각
  투수/타자의 "시즌 경계마다의 커리어 누적 스냅샷"을 공식 train
  데이터만으로 한 번 구축(`build_season_baselines`, train-only 계약은
  `features.fit_shrinkage_priors`와 동일) — 각 (선수, 시즌S) 조합에
  대해 시즌 S보다 **엄격히 이전** 시즌 중 가장 최근 시즌의 마지막 행
  스냅샷을 `merge_asof(..., direction="backward", allow_exact_matches=False)`로
  찾는다(트랙맨 as-of 테이블과 동일 패턴, `trackman_pitcher_features.py`
  참고). 그 스냅샷의 누적 n/rate를 행 자신의 누적 n/rate에서 빼면
  "이번 시즌만의" 표본수/성공횟수가 나오고, 이를 empirical-Bayes
  shrinkage(k=20, `SHRINKAGE_SPECS`와 동일 공식)로 다듬는다. 데뷔
  시즌(이전 스냅샷 없음)은 baseline=0으로 자동 폴백 — 이번 시즌 =
  커리어 전체이므로 정확함. 순수 행-로컬 lookup이라 test 행 간
  의존성 없음(CLAUDE.md 규칙 6 위반 없음).
- **검증 방법**: season 2019-2023 학습 / 2024 검증(표준 프로토콜),
  단일 seed=42로 먼저 A/B, 개선 확인되면 2시드(42+1) 배깅까지.
- **누수 위험 검토**: `build_season_baselines`/`fit_season_state_priors`는
  둘 다 train_only(`~is_val`, 즉 2019-2023)에서만 fit — val(2024)이나
  test 통계 미사용. 스냅샷 자체도 시즌 S보다 엄격히 이전 시즌만 사용
  — leak-safe.

## 결과 (실행 후에 작성)

`src/train_exp027_season_state.py` (로그: `experiments/exp027_run_log.txt`).

| 변형 | Brier | score | best_iter | n_features |
| --- | --- | --- | --- | --- |
| A. 챔피언(기존) 피처만 | 0.247956 | 740.86 | 695 | 89 |
| **B. +이번시즌 상태 피처(exp_027)** | **0.247762** | **818.79** | 571 | 105 |

**Δ = +77.93 — 이 프로젝트 전체 역사상 단일 최대 개선폭**(참고:
exp_018 Platt +19.54, exp_022 재보정 +19.96, 지금까지 모든 계산/구조
실험을 합친 것보다 큼). 팀원의 EXP_056 보고(단일 최대 개선)가 우리
파이프라인에도 그대로 이식되어 재현됨 — 우연이 아니라 진짜 구조적
신호로 판단.

**2시드(42+1) 배깅**: `src/train_exp027_seedbag.py`
(로그: `experiments/exp027_seedbag_run_log.txt`) — seed42=818.79,
seed1=806.74, 평균=**818.30**(단일시드보다 -0.49, 노이즈 수준이라
표준 2시드 배깅 그대로 채택, exp_010과 동일 정책).

**전체 재학습**: `src/train_exp027_final.py`(로그:
`experiments/exp027_final_retrain_log.txt`) — 2019-2023/2024 검증
재확인(818.30, 위와 동일) 후 전체 2019-2024로 최종 재학습 완료.
`model/season_state_{pitcher,batter}_lookup.csv` 신규 아티팩트 저장
(`season_state_features.latest_season_baselines` — 투수 792명,
타자 830명, 각자 2024시즌 말 커리어 누적 스냅샷). 추론 시엔 test 행
자신의 `asof_{entity}_n/rate`(2025 내내 실제로 갱신됨, `data/test.csv`
직접 확인: TEST_000001의 `asof_pitcher_n=3465`처럼 큰 실제값 —
트랙맨과 달리 2025 데이터 자체가 없는 게 아니라 공식 제공 컬럼이
매 행 갱신됨)에서 이 lookup을 빼는 방식이라 트랙맨의 "2025 blind"
문제가 발생하지 않음(`submission/script.py`에
`attach_season_state_features_flat` 추가, 격리 테스트로 직접
확인 — 아래).

**보정(calibration)**: 5-fold OOF 재계산(`src/train_exp027_
calibration_oof.py`, 시드별 2019-2023 5폴드 cross-fit — 로그
`experiments/exp027_calibration_oof_log.txt`, OOF 자체 점수는
~2100대로 매우 높게 나오나 이건 무작위 5-fold 내 교차검증이라
2024로의 실제 외삽보다 항상 낙관적임 — exp_018 때도 같은 패턴이었고
보정기 학습용으로만 씀, 성능 주장 아님) 후 exp_022(2024 가중
weight=100 Platt) + exp_023(2025 추세외삽 prior-shift, 동일 상수
-0.04571) 그대로 재적용(`src/train_exp027_calibration_final.py`,
로그 `experiments/exp027_calibration_final_log.txt`):

| 단계 | 2024 예측 평균 |
| --- | --- |
| raw(무보정) | 0.4969 |
| step1(2024가중 Platt) | 0.4865(실제 2024 rate 0.4861과 거의 일치) |
| step2(2025 추세외삽) | 0.4752(목표 0.4747과 거의 일치) |

기존 챔피언(exp_022/023)과 거의 동일한 gap 크기(raw 0.4969 vs 챔피언
raw 0.4962)와 보정 후 수렴 패턴 — 시즌 드리프트가 피처셋과 무관하게
라벨 자체의 성질이라는 걸 재확인.

**아카이브**: `submission/archive/exp027_season_state_calibrated/`
— 패키징 + 격리 테스트 통과(TEST_000001: 0.3818, TEST_000017: 0.3680,
TEST_000213: 0.4430, TEST_005332: 0.4910, TEST_035185: 0.4812).
**기본 `submission/submit.zip`은 exp_023로 원상 복구함**(exp_027이
+77.93이라는 파격적 개선이라 사용자 직접 확인 후 기본값 교체 여부
결정하는 게 안전하다고 판단, LB 미검증 상태).

**한계/주의(솔직히 공개)**:
- 5-fold OOF의 절대 점수(~2100대)는 교차검증 낙관편향이 매우 커서
  참고 불가 — 신뢰 가능한 숫자는 2019-2023학습/2024검증의 818.30뿐.
- 이번 세션에서 처음 발견된 기법이라 LB 델타 패턴(기존 118~158)이
  그대로 적용될지 불확실 — 개선폭이 워낙 커서(+77.93) LB에서도
  비례해서 크게 나올 가능성이 높지만(팀원 실제 LB 945→1045 사례가
  방증), 로컬-LB 델타가 항상 정확히 비례하진 않았음(exp_018/019
  때 델타 자체가 122→152로 급증한 전례 있음 — 원인은 나중에
  exp_022에서 규명됨). **사용자가 직접 제출해 실제 LB를 확인하는 게
  최우선 권장.**

**추가 이식 후보(팀원 저장소에서, 순서대로 시도 예정)**:
- EXP_112 "reliability" 피처: `n/(n+k)`(k≈100) 를 곱셈적 confidence
  스칼라로 별도 피처화(기존 shrinkage와는 다른 별도 신호). 팀원
  보고 Brier -1.6e-5.
- `same_hand_x_fastball_rate` — 우리는 이미 `same_hand_x_breaking_rate`/
  `same_hand_x_offspeed_rate`는 갖고 있는데(exp_003) fastball만 빠져
  있었음. 팀원은 3개 다 사용. 저비용 추가.
- EXP_127류 count-state(`balls_before`,`strikes_before`)별 시즌추세
  보정 — 우리 exp_022/023의 전역 보정과 상호보완적일 수 있음(팀원
  보고 결합 -1.3e-5, 우리 전역 보정보다는 작지만 별도 축).
