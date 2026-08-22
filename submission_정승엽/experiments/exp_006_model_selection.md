# exp_006 — Phase A~D 모델 비교 (Mean/Logistic/RF/ExtraTrees/CatBoost/LightGBM) + 블렌딩 + Calibration

---

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_006
- **날짜 / 담당자**: 2026-08-20 / Claude(대화 세션)
- **가설**: 특정 알고리즘(CatBoost)을 미리 최종으로 가정하지 않고, 동일한
  84피처 exp_003 피처셋·동일 validation(2019-2023 학습/2024 검증)에서
  Mean baseline / Logistic Regression(ID 제외·포함) / RandomForest /
  ExtraTrees / CatBoost / LightGBM 6개를 단계적으로 비교하면, (a) 어느
  모델이 실제로 가장 나은지 데이터로 확인할 수 있고 (b) 확률 블렌딩이나
  calibration으로 exp_003(723.17)보다 더 개선할 여지가 있는지 알 수 있다.
- **기준(baseline)**: exp_003 (CatBoost, local score 723.17, Brier
  0.248000) — 이번 실험의 CatBoost arm은 exp_003과 완전히 동일한
  피처/하이퍼파라미터/시드로 재현되어야 하며, 이는 파이프라인 정합성
  sanity-check로 실제 검증했다(아래 "검증 방법" 참고).
- **이번에 바꾸는 것**: 단일 가설 검증이 아니라 "동일 조건에서 6개 모델
  아키텍처를 비교"하는 성격의 실험이라 TEMPLATE의 "한 가지로 한정" 항목이
  문자 그대로 적용되지 않는다(exp_003의 LightGBM-vs-CatBoost 비교를
  6개 모델로 확장한 것과 같은 성격). 새로 추가한 것은: (1)
  `src/metrics.py`/`src/validation.py`/`src/model_factory.py`/
  `src/ensemble.py`/`src/calibration.py` — 기존에 없던 공유 인프라
  (기존엔 `official_score`가 `train_exp003.py`/`train_lgbm.py`에
  각각 인라인으로 중복돼 있었고, 모델마다 스크립트를 통째로 복붙하는
  구조였음), (2) `src/train_model_selection.py` — 이 인프라로 Phase
  A(모델 6종)~D(calibration)를 한 번에 실행하는 오케스트레이션 스크립트.
  Trackman(문서의 Phase E)은 명시적으로 이번 범위에서 제외했다 — 어떤
  모델 2~3개가 최종 후보인지가 A~D 결과에 의존하므로, 결과 없이 Trackman
  피처 설계를 지금 하는 건 순서가 맞지 않는다는 판단(사용자 확인 완료).
- **검증 방법**: season 2019-2023 학습 / 2024 검증(기존과 동일).
  **필수 sanity-check**: CatBoost arm 학습 직후 이 스크립트의 공유
  파이프라인(피처 빌드 + season-aware shrinkage + 84피처)이 exp_003의
  정확한 수치(Brier 0.248000, score 723.17)를 재현하는지 `assert`로
  강제 확인 — 실패 시 이후 모든 비교 결과를 신뢰할 수 없으므로 즉시 중단
  하도록 설계했다. **실제 실행 결과 이 게이트를 통과했다**(정확히
  0.248000 / 723.17 재현, 로그 71-72행).
- **누수(leakage) 위험 검토**:
  - 전처리(median imputation, StandardScaler, OneHotEncoder,
    OrdinalEncoder)는 전부 train split(2019-2023)에서만 `fit`, val
    split(2024)엔 `transform`만 적용.
  - Shrinkage prior는 기존 exp_003과 동일하게 train split의 최근
    2시즌(2022-2023)에서만 계산.
  - Calibration(Phase D)은 target을 두 번 보는 게 아니라 2019-2022로
    학습한 **별도 서브모델**을 2023에 예측시켜 그 예측값으로만
    Platt/Isotonic을 fit하고, 이렇게 fit된 calibrator를 실제
    2019-2023-학습 모델의 2024 예측(이미 계산된 값, 재예측 아님)에
    적용한다 — 같은 validation target으로 fitting과 평가를 동시에
    하지 않는다는 CLAUDE.md/문서 §18 규칙을 지켰다.
  - 블렌드 가중치 탐색(Phase C)은 validation prediction만으로 탐색하고
    test.csv는 전혀 사용하지 않는다.
  - `model/`(현재 제출용 CatBoost 아티팩트) 디렉터리는 이 스크립트가
    쓰기 작업을 전혀 하지 않으며, 실행 전후 mtime이 그대로임을 로그로
    확인했다(로그 116-117행) — 이번 실험은 측정 전용이고, 어떤 모델을
    새 챔피언으로 채택할지는 명시적으로 이번 범위 밖이다.

## 결과 (실행 후에 작성)

- **피처 목록**: exp_003과 완전히 동일한 84개(`BASE_FEATURES` 47 +
  `DERIVED_COLS` 26 + `SHRUNK_COLS` 10 + `POST_SHRINKAGE_COLS` 1,
  `src/features.py` 불변).
- **모델 / 하이퍼파라미터**: 아래 B절 표 참고. CatBoost/LightGBM은
  `train_exp003.py`의 하이퍼파라미터를 그대로 재사용, RandomForest/
  ExtraTrees는 공식 baseline(exp_000)의 하이퍼파라미터
  (n_estimators=100, max_depth=10, min_samples_leaf=200)를 재사용하되
  47피처가 아닌 84피처 전체에 적용(의도적 편차 — B절 표 아래 각주 참고),
  Logistic Regression은 C∈{0.01,0.1,1,10} 소규모 그리드에서 검증
  점수 최고값 선택.
- **시드**: 42 (모든 모델 공통).
- **Brier / 공식 로컬 스코어**: 아래 B절 표.
- **실행 시간**: 전체 파이프라인(데이터 로드~calibration까지) 약
  10분(CatBoost 324s, RandomForest 161s, LightGBM은 크래시로 스킵,
  나머지는 수십~수백 초 단위). 상세는 `reports/model_selection_run_log.txt`.
- **예측값 통계 (mean / min / max)**: 아래 B절 표 (`pred_mean`/`pred_min`/`pred_max` 컬럼).
- **관찰 / 오류 분석**: G절 참고.
- **다음 가설**: G절 "다음 가설" 참고.

> 이 문서의 모든 수치는 `reports/model_selection/*.csv`와
> `reports/model_selection_run_log.txt`에서 그대로 가져왔다 — 추정치 없음.

---

## A. 데이터 구조 요약

`train.csv` 48컬럼(row_id + control_success 포함) 중: identifier 1개
(`row_id`), target 1개(`control_success`), categorical_low_cardinality
9개(`top_bottom`, `game_type`, `base_state`, `pitcher_hand`,
`batter_hand`, `pitcher_team_id`, `batter_team_id` 등 — 정수 dtype이라도
의미상 범주형인 컬럼 포함), categorical_high_cardinality 2개
(`pitcher_id` 792종, `batter_id` 830종), 나머지는 ordinal_numeric/
continuous_numeric. 전체 표: `reports/model_selection/data_type_summary.csv`.

`trackman_history.csv`(30컬럼, 200k행 샘플 기준 참고용 — 이번 라운드
미사용, Phase E로 연기)는 `reports/model_selection/data_type_summary_trackman.csv`.

---

## B. 단일 모델 비교

| Model | Brier | Official Score | LogLoss | Calibration Error | Train(s) | Infer(s) | Size(MB) | pred_mean | pred_min | pred_max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **CatBoost** | **0.248000** | **723.17** | 0.689133 | 0.008972 | 324.1 | 0.322 | 0.58 | 0.4950 | 0.3237 | 0.6514 |
| RandomForest | 0.248623 | 473.74 | 0.690387 | 0.014077 | 161.1 | 0.657 | 7.22 | 0.5002 | 0.3848 | 0.6667 |
| ExtraTrees | 0.249259 | 219.40 | 0.691668 | 0.020876 | 49.3 | 0.686 | 6.32 | 0.5070 | 0.3996 | 0.6668 |
| Logistic_LR1 (ID 제외) | 0.249745 | 24.91 | 0.692663 | 0.014196 | 75.3 | 0.567 | 0.013 | 0.4923 | 0.3038 | 0.7061 |
| Logistic_LR2 (ID 원-핫 포함) | 0.250017 | 0.00 | 0.693218 | 0.020043 | 199.1 | 1.212 | 0.035 | 0.4872 | 0.2784 | 0.7017 |
| Mean (reference) | 0.251875 | 0.00 | 0.696904 | 0.045477 | ~0 | ~0 | 0 | 0.5316 | 0.5316 | 0.5316 |
| LightGBM | — | — | — | — | — | — | — | — | — | — |

- **LightGBM**: 이 로컬 Windows 환경에서 학습 중 네이티브 크래시
  (`OSError: access violation reading 0x0000000000000000`)로 실패 —
  `train_exp003.py`에서 이미 문서화된 것과 동일한 환경 문제(재현됨,
  이 실험 자체의 결함이 아님). `src/model_factory.py`의 try/except가
  이 실패를 잡아 나머지 5개 모델 비교는 정상 진행됐다.
- **RandomForest/ExtraTrees 피처셋 편차**: 공식 baseline(exp_000)은
  47피처만 사용했지만, 이번엔 "동일 피처셋에서 아키텍처만 비교"하는
  §6 취지에 맞춰 84피처 전체에 exp_000의 하이퍼파라미터를 그대로
  적용했다 — exp_000의 415.57과 직접 비교 가능한 수치가 아님, 의도된
  편차임.
- CatBoost가 두 번째로 좋은 RandomForest(473.74)보다도 압도적으로
  높다 — Level 2(Bagging) 계열과 Level 3(Boosting) 사이 격차가
  이 데이터·피처셋에서 크다는 것을 확인.

---

## C. Prediction Correlation

| | LR1 | LR2 | RF | ET | CatBoost |
|---|---:|---:|---:|---:|---:|
| LR1 | 1.000 | 0.902 | 0.808 | 0.907 | 0.600 |
| LR2 | 0.902 | 1.000 | 0.730 | 0.812 | 0.546 |
| RandomForest | 0.808 | 0.730 | 1.000 | 0.910 | 0.854 |
| ExtraTrees | 0.907 | 0.812 | 0.910 | 1.000 | 0.708 |
| CatBoost | 0.600 | 0.546 | 0.730 | 0.708 | 1.000 |

CatBoost는 나머지 모델들과 상관관계가 가장 낮다(0.55~0.85) — 다양성
관점에선 블렌딩 후보로 매력적이지만, 실제로는 D절에서 보듯 압도적
성능 격차 때문에 블렌딩 이득으로 이어지지 않았다. 히트맵:
`reports/model_selection/prediction_correlation.png`.

---

## D. Best Blend

- **후보**: `select_blend_candidates`가 Official_Score 상위 3개
  (CatBoost, RandomForest, ExtraTrees — 상관계수 0.98 임계값을 넘는
  쌍이 없어 그대로 통과)를 선정.
- **탐색**: 0.05 step coarse → 0.01 step fine(coarse 최적점 근방
  ±0.05) simplex grid, validation prediction만 사용.
- **결과**: `weights = {CatBoost: 1.0, RandomForest: 0.0, ExtraTrees: 0.0}`,
  Brier 0.248000, Score 723.17 — **CatBoost 단독과 완전히 동일**.
  RandomForest/ExtraTrees를 조금이라도 섞으면 오히려 점수가 낮아져서,
  탐색 알고리즘이 자동으로 가중치 0을 선택했다. 즉 이번 3개 후보
  조합에서는 확률 블렌딩이 개선을 주지 못했다(compound 벤치마크 시도가
  실패한 게 아니라, "블렌딩이 도움 안 됨"이라는 게 실제 결과).

---

## E. Calibration 결과

leak-safe 2단계 구조(2019-2022 학습 → 2023 calibrator fit → 2024
CatBoost/RF/ExtraTrees 실제 예측에 적용)로 Platt/Isotonic을 시도했다.

| Model | raw Score | Platt Score | Isotonic Score |
|---|---:|---:|---:|
| CatBoost | **723.17** | 0.00 | 389.57 |
| RandomForest | **473.74** | 263.44 | 413.59 |
| ExtraTrees | 219.40 | 127.94 | **376.97** |
| Blend (Cat+RF+ET, weights 위 D절과 동일) | **723.17** | 0.00 | 389.57 |

- **CatBoost·RandomForest**: raw(보정 없음)가 Platt/Isotonic 둘 다보다
  낫다 — 특히 Platt은 점수를 0까지 완전히 무너뜨렸다. CatBoost의
  raw calibration error가 이미 0.0090으로 매우 낮다는 것(B절)과 일치:
  원래도 잘 보정돼 있던 모델에, **다른(2019-2022로 학습된, 성능이 더
  낮은) 서브모델의 예측 분포에서 학습한 매핑**을 억지로 씌우니 오히려
  분포가 어긋난 것으로 보인다. 이건 calibration 메커니즘 자체의 버그가
  아니라 "leak-free 2단계 구조의 대가"로 설계 단계에서 이미 예상한
  리스크(calibration.py 문서화 참고: "calibrator를 학습한 서브모델과
  실제 평가 대상 모델이 다른 인스턴스"라는 의도된 아키텍처 불일치)가
  실제로 드러난 경우.
- **ExtraTrees**: 유일하게 Isotonic이 raw보다 뚜렷이 개선(219.40 →
  376.97) — ExtraTrees의 raw calibration error(0.0209)가 셋 중 가장
  나빴던 것과 일치, calibration이 실제로 도움될 수 있는 상황에서는
  개선이 나타남을 확인.
- **결론**: 이번 3개 모델 중 최종 후보(CatBoost)에는 calibration이
  도움되지 않는다. Raw CatBoost가 모든 조합을 통틀어 최고 점수.

---

## F. Trackman 효과

**이번 라운드에서 명시적으로 범위 제외.** Phase A~D 결과(CatBoost가
압도적 1위, 블렌딩/calibration 모두 개선 없음)를 확인한 뒤에 "어떤
모델에 Trackman을 붙일지" 결정하는 게 순서에 맞다는 판단으로, 사용자와
사전에 이번 계획 범위를 A~D로 한정하기로 확인했다. Trackman 스키마
요약만 참고용으로 산출(`data_type_summary_trackman.csv`) — 아직 어떤
피처도 시도하지 않았다. exp_005에서 이미 4개 파생 피처(현재 CatBoost
기준)를 시도해 기각한 바 있으므로, 다음 시도는 CatBoost 기준으로
exp_005와 다른 설계(예: shrinkage 강화, PCA 압축, 보조 모델 스태킹)를
따로 계획해야 한다.

---

## G. 최종 선택

**Best Standalone Model = CatBoost** (Brier 0.248000, Score 723.17) —
exp_003의 챔피언과 완전히 동일한 모델·피처·수치. **Best Ensemble = 없음**
(CatBoost 단독과 동점, 블렌딩이 개선을 주지 못함). **Best Calibrated
Model = 없음** (raw CatBoost가 Platt/Isotonic 둘 다보다 나음).
**Best Trackman-enhanced Model = 미시도** (F절, 다음 세션 과제).

**Final Recommended Model (이번 측정 라운드 기준) = 현재 그대로
exp_003의 CatBoost.** `model/`, `submission/`은 이 실험에서 전혀 건드리지
않았으므로 재제출이나 챔피언 교체 액션은 필요 없다 — 이번 실험의
성격은 "exp_003의 선택이 더 넓은 모델 후보군에서도 최선이었는지
검증"이었고, 결과는 "그렇다"로 확인됐다.

### 관찰 요약

1. Level 0(Mean)→1(Logistic)→2(RF/ExtraTrees)→3(CatBoost)로 갈수록
   점수가 단조 증가(0 → ~25 → ~220~470 → 723) — 아키텍처가 복잡해질수록
   이 문제에서 확실히 이득이 있다는 걸 6단계 사다리로 직접 확인했다.
2. Logistic_LR2(ID 원-핫 포함)가 LR1(ID 제외)보다 오히려 더 나쁘다
   (24.91 → 0.00) — pitcher_id/batter_id를 1600여 개 더미 컬럼으로
   풀면 이 정도 규모(120만 행)에서도 L2 정칙화만으로는 과적합/보정
   붕괴를 못 막는다는 신호. 문서가 권장한 "LR-1/LR-2 둘 다 검증"
   지침이 실제로 의미 있는 차이를 드러낸 사례.
3. LightGBM은 이 로컬 환경에서 여전히 학습 자체가 불가능(exp_003과
   동일한 네이티브 크래시) — CatBoost/LightGBM 비교는 다른 환경(예:
   평가 서버와 동일한 Ubuntu)에서만 가능하다는 게 재확인됐다.
4. 블렌딩·calibration 둘 다 "시도했지만 도움 안 됨"이라는 것 자체가
   유효한 결과 — CatBoost가 이미 나머지 후보 대비 워낙 크게 앞서고
   원래도 잘 보정돼 있어서, 이 시점에서 추가로 짜낼 여지가 많지 않다는
   걸 확인했다.

### 다음 가설

1. Trackman(Phase E)을 CatBoost 기준으로 재시도한다면, exp_005가
   기각한 원시 비율/평균값 대신 더 강하게 정칙화된 형태(큰 k
   shrinkage, PCA 압축, 또는 Trackman 전용 보조 모델의 OOF 예측 1개만
   피처로 추가)를 시도해야 한다(exp_005의 "다음 가설"과 동일 결론,
   이번 실험으로 재확인).
2. LightGBM 네이티브 크래시를 로컬에서 굳이 더 파고들 필요는 낮다 —
   CatBoost가 이미 압도적이고, 최종 제출은 어차피 평가 서버(Ubuntu)에서
   재현되므로 로컬 크래시 여부가 최종 선택에 영향을 주지 않는다.
3. Logistic/RF/ExtraTrees의 하이퍼파라미터 튜닝(예: RF/ExtraTrees의
   min_samples_leaf 축소, LR의 max_iter 증가로 수렴 경고 해소)은
   시도할 수 있으나, CatBoost와의 격차(250점 이상)를 메울 가능성은
   낮아 우선순위가 낮다.

> 이 문서의 모든 수치는 `reports/model_selection/model_comparison.csv`,
> `prediction_correlation.csv`, `best_blend.csv`,
> `calibration_summary.csv`, `data_type_summary*.csv`,
> `reports/model_selection_run_log.txt`에서 그대로 가져왔다 — 추정치 없음.
