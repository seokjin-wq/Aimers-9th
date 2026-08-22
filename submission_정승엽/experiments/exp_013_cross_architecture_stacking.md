# exp_013 — LightGBM/XGBoost 교차 아키텍처 스태킹/블렌딩

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_013
- **날짜 / 담당자**: 2026-08-21 / (Claude, 사용자 요청 — `dacon-score-push-round2`, 목표 로컬 1000/LB 1100)
- **가설**: exp_006에서 CatBoost를 RandomForest/ExtraTrees/Logistic과
  블렌딩했을 때 최적 가중치가 CatBoost=1.0으로 수렴해 개선이 없었다 —
  하지만 그 셋은 CatBoost보다 훨씬 약한 모델이라 다양성 이득보다 정확도
  손실이 컸을 뿐이다. exp_010(같은 CatBoost를 시드만 바꿔 배깅)은
  분산 감소로 +8.72 개선을 냈다. 이번엔 그 중간 지점 — **CatBoost와
  비슷한 급의 boosted tree인 LightGBM/XGBoost**로 진짜 다른 트리 성장
  방식(leaf-wise vs symmetric/oblivious, 다른 분할 탐색·정칙화)의
  다양성을 시도한다. 비슷하게 강하면서 오차 상관관계가 seed-bagging보다
  낮을 가능성이 있다.
- **기준(baseline)**: exp_007/010 챔피언 89피처 세트의 CatBoost 단독
  (이 실행에서 재현).
- **이번에 바꾸는 것**: 동일 89피처 세트로 LightGBM(`train_lgbm.py`
  패턴, native booster) + XGBoost를 추가 학습하고, `src/ensemble.py`의
  `coarse_fine_blend_search`로 validation에서만 블렌드 가중치를 찾는다
  (리더보드 프로빙 아님 — `dacon-leaderboard-probing-risk` 메모리
  준수).
- **검증 방법**: season 2019-2023 학습 / 2024 검증 (공식 정책 그대로).
- **누수 위험 검토**: 세 모델 모두 동일 학습/검증 분할, 동일 피처만
  사용 — 신규 누수 위험 없음. 블렌드 가중치는 2024 validation 예측에만
  그리드서치를 적용(재예측 없음, `src/ensemble.py` 기존 leak-safe
  설계 그대로 재사용). 범주형은 LightGBM/XGBoost용으로 `OrdinalEncoder`를
  **학습 스플릿에서만** fit.

## 결과 (실행 후에 작성)

실행: `src/train_exp013_stacking.py` (전체 로그
`experiments/exp013_run_log.txt`, 2회 크래시 후 3회차 성공 — (1)
`LGBMClassifier.fit(eval_set=...)` sklearn 래퍼가 access violation으로
크래시(신규 발견, `lgb.train()` 네이티브 API로 우회), (2) 그래도 같은
지점에서 재현 — 근본 원인은 **`catboost`를 `lightgbm`보다 먼저
import하면 이후 모든 `lgb.Dataset` 생성이 데이터 무관하게 크래시하는
DLL 로드순서 충돌**이었음(순수 랜덤 배열로 재현·격리 확인). import
순서를 `lightgbm` → `xgboost` → `catboost`로 바꿔서 해결. `CLAUDE.md`
"Submission Constraints"에 이 사실을 기록해 향후 실험이 반복하지 않게
함).

| 모델 | Brier | score | best_iter |
| --- | --- | --- | --- |
| CatBoost 단독(챔피언 재현) | 0.247956 | 740.86 | 695 |
| LightGBM 단독(기본 하이퍼파라미터) | 0.248077 | 692.52 | 154 |
| XGBoost 단독(기본 하이퍼파라미터) | 0.248146 | 664.91 | 146 |

블렌드(validation에서만 `coarse_fine_blend_search`로 가중치 탐색):

| 조합 | 가중치 | score | Δ vs CatBoost |
| --- | --- | --- | --- |
| CatBoost+LightGBM+XGBoost | cb=0.83, lgb=0.17, xgb=0.0 | 742.87 | +2.02 |
| CatBoost+LightGBM | cb=0.83, lgb=0.17 | 742.87 | +2.02 |
| CatBoost+XGBoost | cb=0.95, xgb=0.05 | 741.07 | +0.21 |
| LightGBM+XGBoost | lgb=0.82, xgb=0.18 | 693.98 | -46.88 |

**결과: 미채택(exp_010 챔피언 749.58 대비 열세, 아카이브 안 함).**
가설(진짜 다른 아키텍처 다양성이 seed-bagging보다 유리할 수 있다)은
부분적으로만 맞음 — exp_006의 RF/ET/LR(가중치 CatBoost=1.0로 수렴,
개선 0)보다는 낫지만(+2.02는 0보다 큼), LightGBM/XGBoost 둘 다
**기본 하이퍼파라미터**로만 학습해서 CatBoost보다 훨씬 약함(-48~76점) —
너무 약한 모델과의 블렌딩이라 다양성 이득이 정확도 손실에 거의
잠식됨(3-way 최적해가 XGBoost 가중치를 0으로 만든 것이 이를 보여줌).
exp_010의 순수 분산감소(+8.72, 동급 모델끼리)가 이 방식보다 훨씬
효율적임을 재확인.

**Next 가설**: LightGBM/XGBoost를 exp_009 수준으로 제대로 튜닝하면
격차가 줄어 블렌딩 이득이 커질 수도 있지만, exp_009가 CatBoost
쪽에서는 하이퍼파라미터 미세조정이 이미 전량 기각됐던 것과 같은
패턴이 반복될 가능성이 높아 보임 — 투입 대비 기대이득이 낮다고 판단,
이번 세션에서는 우선순위를 낮춤.
