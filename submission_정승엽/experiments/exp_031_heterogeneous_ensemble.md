# exp_031 — 이종 앙상블 (CatBoost-A + CatBoost-B + ExtraTrees)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_031
- **날짜 / 담당자**: 2026-08-22 / (Claude, 사용자 요청 —
  `docs/teammate_score_gap_analysis.md`의 확신도 1순위 후보)
- **가설**: exp_010의 시드 배깅(동일 CatBoost, 시드만 다름)은 분산만
  줄이고 편향은 그대로다. 허찬 EXP_130처럼 서로 다른 depth/lr의
  CatBoost 2종 + 구조가 다른 ExtraTrees를 섞으면 편향까지
  다양화되어, 시드 배깅만으로는 못 넘던 개선 여지를 확보할 수 있다.
- **기준(baseline)**: exp_030_repro, **score=875.00**(Brier
  0.247621) — `src/train_exp030_repro.py`로 방금 재확인한 공식 기준선
  (기존 "~828" 근사치는 부정확했음, `docs/current_best_pipeline.md`
  참고).
- **이번에 바꾸는 것(한 가지로 한정)**: 모델 구조만 바꾼다 — 피처셋
  (exp_030의 105개 그대로), 캘리브레이션(아직 미적용, exp_030의 것
  그대로 재사용해서 비교), season_decay(미적용, exp_033에서 별도
  검증) 전부 동결. CatBoost-A(exp_030과 동일: depth=6/lr=0.03) +
  CatBoost-B(depth=7/lr=0.025/iterations=600, 팀원 GPU 스펙을 CPU로
  재현) + ExtraTrees(n_estimators=300, min_samples_leaf=20,
  max_features=0.7, max_depth=None) 3개를 블렌드.
- **검증 방법**: season 2019-2023 학습 / 2024 검증(표준). 블렌드
  가중치는 `src/ensemble.py:coarse_fine_blend_search`로 2024 검증
  예측 위에서 탐색(재학습 없음).
- **누수 위험 검토**: 세 모델 다 동일한 2019-2023/2024 분할로 학습.
  ExtraTrees의 범주형 인코더(`fit_cat_ordinal_encoder`)와 imputer는
  train split(2019-2023)에만 fit — `model_factory.py`의 기존 계약
  그대로. 블렌드 가중치 탐색은 이미 계산된 2024 검증 예측 배열만
  사용(`ensemble.py` 자체 문서화: "재학습 없음, test.csv 미접촉").

## 결과 (실행 후에 작성)

실행: `src/train_exp031_heterogeneous_ensemble.py`(로그:
`experiments/exp031_run_log.txt`). **1차 실행은 피처 오염 버그로
재실행함** — `exp030_baseline.py`가 처음엔 `features.py`의 현재
`DERIVED_COLS`(exp_028의 기각된 reliability 7개 포함, 112개)를
그대로 썼다가, 실제 아카이브(`submission/archive/exp030_season_state_
no_extrapolation/model/model_meta.pkl`)의 `all_features`(정확히 105개)를
직접 로드하도록 고쳐서 재실행 — 이후 모든 exp_03X가 이 helper를
공유하므로 같은 실수 반복 안 됨.

- **피처 목록**: exp_030과 정확히 동일한 105개(트랙맨 5 + 이번시즌
  상태 16 포함).
- **모델 / 하이퍼파라미터**:
  - CatBoost-A: depth=6, lr=0.03, iterations≤2000(early stop), seed=42
    → best_iter=571 (523.2s)
  - CatBoost-B: depth=7, lr=0.025, iterations=600, bootstrap_type=
    Bayesian, seed=42 → best_iter=468 (484.1s)
  - ExtraTrees: n_estimators=300, min_samples_leaf=20, max_features=0.7,
    max_depth=None, seed=42 (833.2s, model 2103.9MB)
- **Brier / 공식 로컬 스코어 (raw, 보정 전)**:
  | 모델 | Brier | score |
  |---|---|---|
  | CatBoost-A | 0.247762 | 818.79 |
  | CatBoost-B | 0.247757 | 820.61 |
  | ExtraTrees | 0.248082 | 690.50 |
  | 블렌드(가중치 CatBoost-A 0.40 / CatBoost-B 0.39 / ExtraTrees 0.21) | 0.247718 | **836.02** |
- **근사 보정 후(2024 자체로 Platt 직접 피팅, 스크리닝용)**:
  CatBoost-A=869.44, 블렌드=**890.18**
  — 참고: exp_030_repro의 진짜(OOF+2024가중) step1 보정 점수는
  868.07, count-trend까지 더하면 875.00.
- **실행 시간**: 총 1840.5s(약 30.7분) — CatBoost-A 523.2s +
  CatBoost-B 484.1s + ExtraTrees 833.2s.
- **관찰**:
  - ExtraTrees는 단독으로 CatBoost보다 훨씬 약함(690.50 vs 818~820)
    — 다만 이건 이 프로젝트의 기존 패턴과 일치(exp_006 당시 기본
    하이퍼파라미터 ExtraTrees는 219.40으로 더 낮았음,
    `reports/model_selection/model_comparison.csv`). ID 컬럼
    (pitcher_id 등)을 raw 정수로 넣는 이 프로젝트 관행이 트리
    배깅 계열엔 불리한 것으로 보이나, 이번 실험 범위 밖이라
    별도 조사 안 함.
  - 그럼에도 **블렌드가 단일 CatBoost-A보다 확실히 나음**(raw
    +17.23, 근사보정 +20.74) — 약한 모델이라도 편향이 다르면
    앙상블에 실질적 가치를 더한다는 가설이 방향성 있게 확인됨.
  - 근사보정 블렌드(890.18)가 exp_030_repro 공식 기준선(875.00)보다
    높게 나왔지만, **이 비교는 완전히 공정하지 않음**(근사보정은
    2024 자체로 순환 피팅, count-trend 미포함, CatBoost-A도 2시드
    아님 단일시드) — exp_037에서 진짜 OOF 기반 보정 + count-trend
    까지 재적용해서 재검증 필요.
- **다음 가설**: 이종 앙상블 자체는 유효한 신호로 판단 — exp_037
  조립 단계에서 채택. affine 보정(exp_032)을 블렌드 전에 추가하면
  더 개선되는지 다음 실험으로 확인.
