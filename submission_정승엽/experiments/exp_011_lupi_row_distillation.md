# exp_011 — LUPI 행단위 trackman privileged 정보 지식증류(distillation)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_011
- **날짜 / 담당자**: 2026-08-21 / (Claude, 사용자 요청 — `dacon-score-push-round2`)
- **가설**: exp_007/008은 Phase 2 **투수 단위** as-of 평균만 썼다. 하지만
  Phase 2는 이미 **행(투구) 단위** 매칭(`row_mapping.csv`, train 행의
  87.23%)도 만들어 뒀고, 이건 "그 투수가 과거에 보통 어땠는가"가 아니라
  "바로 이 투구가 실제로 어떤 물리 특성이었는가"라는 더 직접적인
  정보다. DACON 공식 Q&A로 LUPI/teacher-student 방식(학습시에만 특권
  정보 사용, 추론시엔 미사용)이 허용된 것이 확인됨(`dacon-lupi-
  distillation` 메모리). 다만 trackman에는 실제 판정 위치(스트라이크존
  기준 최종 볼 위치)가 없어(구속/무브먼트/릴리스 포인트뿐) 이 신호가
  control_success와 얼마나 상관 있을지는 미검증 — 이번 실험이 그 자체를
  검증한다.
- **기준(baseline)**: exp_008/009 확정 설정의 "control"(privileged 정보
  없는 표준 학습, 이 실행에서 재현).
- **이번에 바꾸는 것**: (1) 2019-2023 학습분을 5-fold cross-fit해서
  privileged 피처(그 행에 실제 매칭된 trackman 물리값 8개) 포함 teacher를
  fold별로 학습, out-of-fold soft label(그 행에 대해 자기 자신을 학습에
  쓰지 않은 teacher의 예측 확률) 생성. (2) student는 privileged 피처
  없이(exp_008과 동일한 피처만), target을 `alpha*실제라벨 +
  (1-alpha)*teacher_oof확률`로 블렌딩(alpha ∈ {0.5, 0.7, 0.85})해
  `loss_function="CrossEntropy"`로 학습. (3) 2024 검증은 항상 실제
  라벨로만 채점 — teacher/student 어느 쪽도 2024 정보를 학습에 쓰지
  않음.
- **검증 방법**: season 2019-2023 학습(그 안에서 5-fold cross-fit) /
  2024 검증(공식 정책 그대로, 실제 라벨).
- **누수 위험 검토**: teacher가 자기 자신이 학습한 행을 그대로
  재예측하면 과적합된 신호를 student에 전달할 위험이 있어 cross-fit(각
  fold의 teacher는 그 fold 행을 전혀 보지 않음)으로 방지. student는
  추론에 privileged 컬럼을 전혀 쓰지 않으므로 test/제출 시 안전(2025
  trackman 데이터 없음 문제와 무관). "alpha=1.0"은 사실상 사실 라벨만
  쓰는 control과 동치 — 이걸 사실상의 안전장치로 항상 같이 비교.

## 결과 (실행 후에 작성)

실행: `src/train_exp011_lupi.py` (전체 로그 `experiments/exp011_run_log.txt`,
2회차 실행 — 1회차는 `CatBoostClassifier(**CB_PARAMS_LOGLOSS,
iterations=2000)`에서 `iterations` 중복 전달 `TypeError`로 3단계에서
크래시, teacher cross-fit 39분이 날아갈 뻔해서 `output/
exp011_teacher_oof_cache.npy` 캐시를 추가하고 재실행 — 이후 유사
실험에서도 비싼 중간 단계는 캐시하는 패턴 재사용할 것).

- **row-level privileged 피처 커버리지**: 87.03%(행 기준, exp_007의
  투수 단위 매핑 98.23%보다 낮음 — 당연히 행 단위가 더 세밀해서 빈틈이
  더 많이 드러남).
- **teacher OOF(2019-2023, 참고용, privileged 피처 포함)**: Brier=0.242862,
  **score=2466.12** — control(740.86)의 3배 이상. 즉 "그 투구의 실제
  트랙맨 물리값"은 그 자체로 매우 강한 신호. 하지만 이건 학습에만 쓸 수
  있는 정보이므로 student(추론 시 privileged 없음)로 얼마나 전달되는지가
  관건.
- **student 결과(2019-2023 학습/2024 검증, 실제 라벨로만 채점)**:

| 구성 | Brier | score | Δ vs control |
| --- | --- | --- | --- |
| control(표준 Logloss, exp_007 재현) | 0.247956 | 740.86 | 0 |
| LUPI alpha=0.5 | 0.247970 | 735.53 | -5.33 |
| LUPI alpha=0.7 | 0.247998 | 724.25 | -16.61 |
| LUPI alpha=0.85 | 0.247981 | 730.82 | -10.04 |

**결과: 기각.** 3개 alpha 전부 control보다 낮음(alpha=0.5가 그나마
손해가 가장 적음, teacher 비중을 높일수록(alpha 낮출수록) 더 나빠지는
단조 패턴). teacher가 자기 자신의(cross-fit) 데이터에서는 압도적으로
강한데도(score 2466) student에는 전달되지 않고 오히려 해가 됨 —
해석: (1) CrossEntropy 손실로 "부드러운" 블렌드 타겟을 준 게 손실
함수의 곡률을 바꿔 최적화 난이도를 높였을 뿐, teacher가 아는 "그
투구의 실제 물리값"이라는 *정보*가 student 피처(사전 정보만)로는 재구성
불가능한 성질의 것이라 증류가 안 됨(투수의 과거 평균(exp_007 방식)과
"이번 투구의 실측값"은 근본적으로 다른 종류의 정보 — 후자는 사전에
알 수 없는 그 순간의 무작위성이 큰 비중을 차지할 가능성). (2) alpha가
낮을수록(teacher 의존 커질수록) 더 나빠지는 단조 경향은 이 해석과
일치 — teacher 신호를 많이 섞을수록 student가 예측 불가능한 노이즈를
따라가려다 실제 패턴 학습을 방해받음.

**전체 재학습 + 아카이브(사용자 지시 — exp_010/011은 로컬 기각이어도
반드시 아카이브)**: 3개 alpha 중 손해가 가장 적은 **alpha=0.5**를
`src/train_exp011_final.py`로 전체 2019-2024 재학습(teacher cross-fit도
전체 데이터로 재수행 후 블렌드 타겟으로 student 최종 학습) —
`submission/archive/exp011_lupi_alpha0.5/`. student는 privileged 피처를
전혀 쓰지 않으므로 `model_type="catboost"`(exp_007/009와 동일 추론
경로), 격리 테스트까지 통과.

**Next 가설**: 행단위 privileged 정보를 살리려면 "블렌드 타겟"보다
"teacher와 student 중간 표현(feature) 매칭"이나, teacher 예측을
student의 *추가 입력 피처*가 아니라 *별도 보조 head의 타겟*으로 쓰는
멀티태스크 구조(같은 backbone, 두 출력 헤드)가 더 나을 수 있음 — 다만
CatBoost는 네이티브 멀티태스크/멀티아웃풋 헤드 공유가 sklearn
인터페이스로는 번거로워 상대적으로 구현 비용이 큼. 현재로선 exp_007
방식(투수 단위 as-of 평균)이 이 프로젝트에서 trackman을 쓰는 가장
효과적인 방법이라는 결론 유지.
