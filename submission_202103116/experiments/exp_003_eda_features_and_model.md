# exp_003 — EDA 기반 피처 추가 + season-aware shrinkage + CatBoost

---

## 실험 개요

- **실험 ID**: exp_003
- **날짜 / 담당자**: 2026-08-19 / Claude(대화 세션), 담당자 정승엽 확인 대기
- **가설**: `reports/eda_group1~5`, `reports/eda_final`에서 실제 검증된
  후보들(§Feature Engineering 우선순위 표)을 적용하고, 팀원들이
  체감상 더 낫다고 한 CatBoost를 LightGBM과 실제로 비교하면 exp_002
  (706.28)보다 로컬 검증 점수가 개선될 것이다.
- **기준(baseline)**: exp_002 (LightGBM, local score 706.28, Brier
  0.248043) — LB는 exp_001의 781.0134가 최신 기록(exp_002는 LB
  미제출).
- **이번에 바꾸는 것**: 아래 4가지를 한 번에 묶어서 적용함(단일 변경
  원칙에서 의도적으로 벗어난 것 — "실험 설계" 절 참고).
- **검증 방법**: season 2019-2023 학습 / 2024 검증 (공식 baseline과
  동일).
- **누수(leakage) 위험 검토**: shrinkage prior는 여전히 학습
  스플릿에서만 계산(검증 실행 시 2019-2023, 최종 재학습 시
  2019-2024) — "최근 시즌만 쓴다"는 이번 변경도 그 학습 스플릿 *안의*
  최근 시즌(검증 실행: 2022-2023, 최종 재학습: 2023-2024)만 쓰므로
  2024 검증/2025 실제 평가 정보가 새어 들어가지 않음. 새 피처 4개는
  전부 행 단위(row-local) 계산이라 CLAUDE.md 누수 규칙과 충돌 없음.

### 실험 설계 — 왜 이번엔 여러 변경을 한 번에 묶었는가

exp_001/exp_002는 "피처만 바꾼다"/"모델은 그대로 둔다" 식으로 단일
변경을 지켰다. 이번엔 사용자가 "1~5번 통합 EDA 결과를 전부 반영한
최고 성능 제출물"과 "모델 비교(팀원 의견: CatBoost)"를 한 번에
요청했고, 개별 ablation(피처만/모델만/season-aware prior만 따로)을
전부 돌리기엔 오늘 회의 전 시간이 부족했다. 따라서 이번 실험은
**"피처+prior+모델을 함께 바꾼 하나의 묶음"**으로 기록하고, 어떤
요소가 얼마나 기여했는지는 정확히 분리하지 못했다는 걸 명시한다.
개별 기여도를 알고 싶으면 후속 실험(exp_004 이전에 가능)으로
분리해야 한다 — §다음 가설 참고.

---

## 변경 내용 상세

### 1. 신규 파생 피처 4개 (`src/features.py`)

| 피처 | 계산 | EDA 근거 |
|---|---|---|
| `same_hand_x_breaking_rate` | `same_hand_matchup * asof_pitcher_breaking_rate` | `reports/eda_final` §B — 손 유형 조합 안에서도 구종 성향에 따라 성공률이 46.82~56.41%로 갈림 |
| `same_hand_x_offspeed_rate` | `same_hand_matchup * asof_pitcher_offspeed_rate` | 상동 |
| `three_ball_x_risp` | `three_ball * runners_scoring_position` | `reports/eda_final` §D — 3볼 상황에서 득점권 주자 유무가 outs=0/1에서 방향성을 가짐(가설 수준) |
| `shrunk_pitcher_x_batter_success` | `shrunk_pitcher_success_rate * shrunk_batter_success_rate` (post-shrinkage) | `reports/eda_final` §H — 투수·타자 품질 매치업이 거의 가법적이지만 약한 곱셈적 잔차가 있음 |

### 2. `asof_batter_*` shrinkage k 50 → 150

`reports/eda_group5` §8 — 타자 쪽 소표본 편향(n=1 vs n=1001+ 격차
7.0%p)이 투수 쪽(1.8%p)보다 훨씬 커서, 기존 k=50이 타자 컬럼엔
과소 보정이라고 판단.

### 3. Season-aware shrinkage prior

기존: `fit_shrinkage_priors(train_split_전체)` (검증 시 2019-2023
평균, 최종 재학습 시 2019-2024 평균).
변경: `fit_shrinkage_priors(train_split의_최근_2개_시즌만)` (검증 시
2022-2023 평균, 최종 재학습 시 2023-2024 평균).

`reports/eda_final` §E/§F — 투수·타자 품질 분위 내에서도 시즌별
절대 성공률이 계속 하락하므로, 2019년까지 포함한 전체 평균 prior는
2025년 예측 시점 기준으로 이미 낡은(너무 높은) 값이다. 실제로 확인된
prior 변화(검증 실행 기준):

| 컬럼 | 전체 학습기간(2019-2023) 평균 | 최근 2개 시즌(2022-2023) 평균 |
|---|---|---|
| `asof_pitcher_success_rate` | 0.5402 | 0.5296 |
| `asof_pitcher_reverse_rate` | 0.2106 | 0.2282 |
| `asof_pitcher_middle_rate` | 0.1390 | 0.1456 |

### 4. 모델 비교: LightGBM vs CatBoost — **LightGBM은 이 환경에서 학습 불가**

CatBoost(1.2.10, `pip install`로 신규 설치)와 exp_001/exp_002부터
써온 LightGBM(4.7.0)을 동일한 피처셋으로 비교하려 했으나,
**LightGBM이 이 세션의 로컬 Windows 환경에서 완전히 무관한 합성
데이터(`pandas.DataFrame(np.random...)`, 프로젝트 코드 전혀 사용
안 함)로도 `OSError: exception: access violation reading
0x0000000000000000`로 즉시 죽는 것을 확인**했다. 시도한 원인 규명/
조치:

- 프로젝트 피처(84개) → 실패
- 5만 행 샘플만 → 실패
- catboost를 import하지 않은 프로세스 → 여전히 실패 (catboost와의
  DLL 충돌은 아님)
- `n_jobs=1`(단일 스레드) → 여전히 실패 (스레딩 경쟁 조건 아님)
- 완전 합성 데이터(1000행 x 5열 랜덤) → 여전히 실패 → **이 세션의
  코드/데이터와 무관한 환경 레벨 문제로 결론**
- `pip install --force-reinstall --no-cache-dir lightgbm==4.7.0` →
  재현됨(해결 안 됨). 이 과정에서 실수로 numpy가 2.4.6으로 같이
  올라갔던 것을 즉시 `numpy==1.26.4`(평가 서버 고정 버전)로 되돌림 —
  최종 결과물엔 영향 없음.
- CatBoost는 같은 환경(같은 프로세스, 같은 합성 데이터)에서 정상
  동작 확인.

결론: exp_001/2 당시엔 분명 LightGBM이 정상 동작했는데, 이 세션
시점엔 원인 불명의 로컬 환경(Windows DLL/드라이버 등) 문제로 깨져
있다. 이번 실험 코드(`src/train_exp003.py`)와 무관한 문제라 더 깊게
파지 않고, **CatBoost 단독으로 진행**했다 — 어차피 팀원들 의견과
같은 방향이라 실질적 손실은 없다. LightGBM 자체 비교는 이 환경이
복구되거나 다른 머신에서 재실행하면 다시 시도할 수 있다.

---

## 결과

- **피처 목록**: `BASE_FEATURES`(공식 47개, row_id 제외) +
  `DERIVED_COLS`(26개, exp_001 15개 + exp_002 8개 + exp_003 3개) +
  `SHRUNK_COLS`(10개) + `POST_SHRINKAGE_COLS`(1개, `shrunk_pitcher_x_batter_success`)
  = **총 84개**.
- **모델**: CatBoostClassifier — `iterations=2000`(early stopping으로
  511에서 멈춤), `learning_rate=0.03`, `depth=6`, `l2_leaf_reg=3.0`,
  `loss_function="Logloss"`, `cat_features=["top_bottom", "game_type",
  "base_state"]`(원본 문자열 그대로, OrdinalEncoder 불필요).
- **시드**: `random_seed=42`.
- **Brier Score**: 0.248000
- **공식 로컬 스코어**: **723.17** (exp_002 대비 +16.89)
- **실행 시간**: 검증 학습 실제 계산 시간 약 4분(노트북 절전모드로
  인해 `time.time()` 기준 로그엔 55425.2s로 찍혔으나 이는 절전 중에도
  흐르는 벽시계 때문 — CatBoost 자체 내부 타이머는 4분 근처에서
  early stopping 조건 충족을 보여줌); 최종 2019-2024 전체 재학습은
  225.2초(3분 45초).
- **예측값 통계** (2024 검증셋): mean 0.4950 / min 0.3237 / max 0.6514.
- **관찰 / 오류 분석** (구간별 Brier, `train_shrunk` 기준):

| 구간 | n | Brier | 실제 성공률 | 평균 예측 |
|---|---|---|---|---|
| two_strike=1 | 72,965 | 0.248521 | 0.4880 | 0.4923 |
| two_strike=0 | 180,542 | 0.247790 | 0.4853 | 0.4961 |
| is_close_game=1 | 113,660 | 0.248068 | 0.4921 | 0.5007 |
| is_close_game=0 | 139,847 | 0.247945 | 0.4812 | 0.4903 |
| cold_start(n<50) | 3,980 | **0.246327** | 0.4560 | 0.4734 |
| warm(n>=50) | 249,527 | 0.248027 | 0.4866 | 0.4953 |

exp_002 때는 cold_start 구간이 warm 구간보다 오차가 더 컸는데,
이번엔 **cold_start 구간 Brier(0.246327)가 warm 구간(0.248027)보다
오히려 낮다** — batter shrinkage k 상향(50→150)과 season-aware
prior가 실제로 cold-start 예측을 개선했을 가능성을 시사한다(단,
표본이 3,980건으로 작아 확정적 결론은 아니다 — "가설"로 기록).

**Feature importance top 15 (CatBoost)**:

```
game_type: 24.3
season: 17.5
shrunk_pitcher_x_batter_success: 8.5   <- exp_003 신규 피처, 3위
asof_pitcher_prev5_game_success_rate: 2.5
asof_pitcher_reverse_rate: 2.2
pitcher_team_id: 1.9
shrunk_pitcher_success_rate: 1.9
asof_pitcher_prev1_game_success_rate: 1.8
game_month: 1.8
shrunk_pitcher_ball_rate: 1.8
batter_team_id: 1.7
shrunk_pitcher_reverse_rate: 1.6
same_hand_matchup: 1.5
pitcher_id: 1.5
asof_pitcher_success_rate: 1.5
```

`shrunk_pitcher_x_batter_success`(이번에 새로 추가한 곱셈 피처)가
전체 84개 피처 중 3위로 올라왔다 — `reports/eda_final` §H의 가설
("약한 곱셈적 상호작용의 여지")이 실제 모델에서도 유의미하게
쓰이고 있음을 뒷받침한다. 다만 `game_type`(24.3)과 `season`(17.5)
두 개가 압도적으로 큰 비중을 차지 — 이는 그룹1/최종 EDA에서 이미
발견한 시즌 하락·game_type 반전 현상과 일치한다.

---

## 코드 구조 변경

- `src/features.py`: exp_003 파생 피처 4개 추가, `SHRINKAGE_SPECS`의
  타자 관련 두 항목 k=50→150, `POST_SHRINKAGE_COLS`/`ALL_DERIVED_COLS`
  갱신 (기존 exp_001/exp_002 피처는 그대로 유지 — 하위 호환).
- `src/train_exp003.py` (신규): season-aware prior + LightGBM/CatBoost
  비교 + 승자 자동 선택 + 전체 재학습/저장까지 한 번에 수행. 승자에
  따라 `model/lgbm_booster.txt`+`model/lgbm_meta.pkl` 또는
  `model/catboost_model.cbm`+`model/model_meta.pkl`을 저장(과거
  `lgbm_meta.pkl`이라는 이름을 모델 종류 무관하게 `model_meta.pkl`로
  통일 — `submission/script.py`가 `model_meta.pkl`의 `model_type`
  필드로 분기).
- `src/train_lgbm.py`: 그대로 보존(과거 exp_001/exp_002 기록 재현용,
  이번 실험엔 사용하지 않음).
- `submission/script.py`: `model_meta.pkl`의 `model_type`에 따라
  LightGBM/CatBoost 중 실제 학습된 쪽만 지연 import해서 로드하도록
  일반화. CatBoost는 `cat_features`를 원본 문자열 그대로 받으므로
  `OrdinalEncoder` 인코딩을 건너뜀(`cat_encoder=None`).
- `requirements.txt`(루트), `submission/requirements.txt`: 제출용은
  `catboost==1.2.10`만 포함(가벼운 설치를 위해 lightgbm/xgboost는
  제출 zip에서 제외). 루트 requirements.txt엔 로컬 개발 참고용으로
  lightgbm/xgboost도 계속 남겨둠(현재 lightgbm은 로컬에서 크래시
  중이라는 주석 추가).
- `model/`에 남아있던 exp_002 시절 `lgbm_booster.txt`/`lgbm_meta.pkl`
  삭제(패키징 시 옛 파일이 zip에 같이 들어가는 걸 방지).
- `submission/submit.zip` 재빌드 완료
  (`python src/package_submission.py exp003_catboost`) — 격리 폴더
  압축 해제 후 `script.py` 단독 실행으로 재현 테스트 통과
  (`row_id`/예측 5건 정상 생성, 확률 [0,1] 범위, `row_id` 순서
  `sample_submission.csv`와 일치).

---

## 다음 가설

1. **가장 중요 — 이번 개선은 작다.** 706.28 → 723.17(+16.89)는
   실제 개선이지만, 목표(1200+)까지 가는 데 필요한 폭에 비하면
   미미하다. Brier 자체도 0.248043 → 0.248000으로 거의 안 움직였다
   (점수 공식이 baseline 근처에서 민감하게 반응할 뿐). **이건 사전
   예상(대화 기록 참고: "EDA만으로는 790→1200을 못 채울 것")과
   일치하는 결과다.** → 다음 우선순위는 예정대로 `data/trackman_history.csv`
   조인(exp_004).
2. **묶음 실험이라 개별 기여도 불명.** 4개 신규 피처, batter k 상향,
   season-aware prior, CatBoost 전환 중 무엇이 얼마나 기여했는지
   분리되지 않았다. LightGBM 환경이 복구되면 "CatBoost 자체 효과"만
   따로 검증할 가치가 있고, season-aware prior만 껐다 켜는 ablation도
   저렴하게 해볼 수 있다(exp_004 이전에 짬날 때 시도 가능).
3. **cold-start 구간 개선이 실제인지 재확인 필요.** 표본 3,980건으로
   작아 이번 관찰(cold_start Brier < warm Brier)이 우연일 수 있다 —
   trackman 실험 전에 시드를 바꿔 재확인하거나, cross-validation으로
   안정성을 확인해볼 것.
4. **LightGBM 환경 문제는 미해결로 남김.** 이번 세션에서 재현/원인
   규명은 했지만(환경 레벨, 이 코드와 무관), 실제 수정은 하지 않음 —
   급하지 않다면 다음에 별도로 처리(Python 재설치, VC++ 재배포판
   업데이트 등 시도 가능).

> 실제로 실행해서 비교한 결과만 기록함 — 로컬 723.17은
> `experiments/exp003_run_log.txt` 전체 로그에서 그대로 가져온 값.
> 리더보드 점수는 아직 제출 전이라 이 문서엔 없음 — 제출 후
> `experiments/SUBMISSION_LOG.md`에 별도로 기록.
