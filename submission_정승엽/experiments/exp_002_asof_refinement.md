# exp_002 — asof_* 기반 파생 피처 정교화 + cold-start shrinkage

## 실험 개요

- **실험 ID**: exp_002
- **날짜 / 담당자**: 2026-08-12 / (설정 필요)
- **가설**: exp_001의 15개 파생 피처는 대부분 단순 차이/합/로그 정도의 얕은 조합이었다. 여기에 (1) 상황(압박/득점권)별로 조건화한 투수 경향 피처, (2) `prev1/3/5_game_*`의 중첩 구조를 대수적으로 풀어낸 더 정확한 최근 폼 추세/변동성 피처, (3) 표본 수가 적은 cold-start 행에 대한 경험적 베이즈 축소추정(shrinkage), (4) 상대적으로 덜 쓰인 타자 지표·손잡이 매치업을 추가하면, **모델은 그대로 두고도** exp_001 대비 Brier Skill Score가 개선된다.
- **기준(baseline)**: exp_001 (공식 로컬 스코어 628.51)
- **이번에 바꾸는 것 (한 가지로 한정)**: 피처 세트만 변경 (`src/features.py`에 파생 피처 8개 + shrinkage 출력 10개 추가). **모델·하이퍼파라미터는 exp_001과 완전히 동일하게 고정** — exp_001이 "피처 추가 + 모델 교체"를 동시에 해서 각각의 기여도를 분리하지 못했던 것을 이번엔 분리해서 순수 피처 효과만 측정한다. `trackman_history.csv` 조인은 이번 실험 범위에서 제외 (다음 실험으로 분리).
- **검증 방법**: season 2019-2023 학습 / season 2024 검증 (기존과 동일, 변경 없음)
- **누수(leakage) 위험 검토**: 아래 "피처 목록"의 A~D는 모두 해당 행 자신의 공식 컬럼(`asof_*`, `li`, `runners_scoring_position`, `pitcher_hand`/`batter_hand`)만 사용하는 행 단위(row-local) 연산 — 다른 행 참조 없음. E(shrinkage)는 유일하게 "학습에서 계산한 통계를 적용"하는 방식이라 특히 주의해서 설계함: prior(전역 평균)는 **검증 실행에서는 2019-2023 학습 스플릿에서만, 최종 제출 모델에서는 2019-2024 전체 학습 데이터에서만** 계산하고(`fit_shrinkage_priors`), `test.csv`/2024 검증 데이터의 통계는 전혀 사용하지 않음. `src/train_lgbm.py` 실행 로그에서 `val_priors`(2019-2023)와 `final_priors`(2019-2024)가 서로 다르게 나온 것으로 스플릿별로 실제로 다시 fit됐음을 확인함 (아래 "관찰" 참고). CLAUDE.md 규칙 6~8번과 충돌 없음.

## 결과

### 피처 목록

exp_001의 기존 15개 파생 피처는 그대로 유지하고, 아래 A~E를 추가했다 (`src/features.py`). 모든 피처는 공식 `train.csv`/`test.csv` 컬럼만 사용한 행 단위 계산이며 다른 행 정보를 참조하지 않는다 (CLAUDE.md 누수 규칙 6번 위반 없음).

#### A. 압박 상황별 투수 경향 (3개)

| 피처명 | 목적 / 가설 | 계산식 | 왜 누수 안전한가 |
|---|---|---|---|
| `pitcher_success_under_pressure` | 투수의 전반적 제구 성공률을 상황 중요도(`li`, leverage index)로 조건화. 압박이 클수록 제구가 흔들리는 투수와 아닌 투수를 구분하려는 목적. 트리 모델은 두 변수를 각각 분할할 순 있어도 곱셈적(비율) 관계는 잘 못 찾기 때문에 명시적으로 상호작용항을 만들어줌 | `asof_pitcher_success_rate * li` | 둘 다 해당 행에 이미 존재하는 투구 직전 시점 공식 컬럼 |
| `pitcher_reverse_under_pressure` | `asof_pitcher_reverse_rate`(의도 반대성 투구 비율)는 제공된 컬럼 중 "제구 실패"에 가장 직접적인 신호로 판단됨. 압박 상황에서 이 비율이 커지는 투수를 포착 | `asof_pitcher_reverse_rate * li` | 위와 동일 |
| `pitcher_success_x_risp` | `li`는 이닝/점수차/아웃/주자상황을 이미 종합한 지표라 완전히 동일하지 않지만, 득점권 주자(RISP)는 더 직관적이고 해석하기 쉬운 별도의 압박 신호라 병행 실험 | `asof_pitcher_success_rate * runners_scoring_position` (기존 exp_001 피처 재사용) | `runners_scoring_position`도 해당 행의 `runner_on_2b`/`runner_on_3b`만으로 계산된 행 단위 피처 |

#### B. 최근 폼 추세/변동성 (3개)

`asof_pitcher_prev1/3/5_game_success_rate`는 **중첩된 누적 평균**이다 (prev3는 최근 3경기 평균, prev5는 최근 5경기 평균이라 prev5 안에 prev3의 경기들이 포함됨). 기존 exp_001의 `pitcher_recent_form_delta = prev1 - prev5`는 prev5에 가장 최근 경기가 섞여 있어 추세가 실제보다 흐려지는 문제가 있었다. 대수적으로 "4~5경기 전만의 평균"을 아래처럼 분리할 수 있다:

`오래된_구간_평균 = (5*prev5 - 3*prev3) / 2`

| 피처명 | 목적 / 가설 | 계산식 | 왜 누수 안전한가 |
|---|---|---|---|
| `pitcher_form_trend_isolated` | "가장 최근 경기" 대 "진짜 예전 경기(4~5경기 전)"를 비교하는, 오염이 덜한 추세 피처. 기존 `pitcher_recent_form_delta`보다 방향성이 더 명확할 것으로 기대 | `prev1 - (5*prev5 - 3*prev3)/2` | `asof_*` 컬럼끼리의 사칙연산 |
| `pitcher_middle_trend_isolated` | 같은 추세 로직을 성공률이 아니라 `middle_rate`(가운데/위험 코스 비율)에 적용 — 제구 위험도의 추세를 더 직접적으로 볼 수 있을 것으로 기대 | `prev1_middle - (5*prev5_middle - 3*prev3_middle)/2` | 동일 |
| `pitcher_form_volatility` | 방향(추세)과 별개로, 최근 폼의 변동 폭 자체가 큰 투수(기복이 심한 투수)를 잡아내려는 목적 | `max(prev1,prev3,prev5) - min(prev1,prev3,prev5)` (행 단위, NaN 자동 skip) | 동일 |

**가정 및 한계 (명시)**: 이 분리 공식은 제공처가 prev3/prev5를 정확히 "최근 3/5경기 평균"으로 계산했다는 가정에 의존한다. 만약 cold-start 투수에게 "그때까지 있는 경기만 평균"하는 방식이 쓰였다면 이 분리는 근사치일 뿐 정확하지 않다 — 공식 데이터 설명서에는 이 세부 계산 방식이 명시되어 있지 않으므로, 이는 **검증되지 않은 가정**임을 밝힌다.

#### C. 타자 지표 보완 (1개)

| 피처명 | 목적 / 가설 | 계산식 | 왜 누수 안전한가 |
|---|---|---|---|
| `batter_middle_minus_success` | 기존엔 `pitcher_middle_minus_success`(투수 쪽)만 있고 타자 쪽 대칭 지표가 없었음. 타자가 상대한 투구들의 위험도 대비 성공률 패턴을 동일하게 반영 | `asof_batter_middle_rate - asof_batter_success_rate` | `asof_batter_*` 컬럼끼리의 뺄셈 |

#### D. 손잡이 매치업 (1개)

| 피처명 | 목적 / 가설 | 계산식 | 왜 누수 안전한가 |
|---|---|---|---|
| `same_hand_matchup` | 전형적인 platoon(투타 손잡이 상성) 신호. `pitcher_hand`/`batter_hand`는 이미 원본 컬럼으로 모델에 들어가지만 둘을 직접 비교한 피처는 없었음 | `(pitcher_hand == batter_hand)`, 정수(0/1) | 해당 행 자신의 두 원본 컬럼 비교 |

#### E. Cold-start 경험적 베이즈 Shrinkage (메커니즘 1개, 출력 컬럼 10개)

데이터 설명서(`docs/data_description.md`)에 "표본 수가 0인 경우 일부 rate 컬럼은 결측값일 수 있고, cold-start 처리는 참가자 자유"라고 명시되어 있음. 기존엔 이 NaN을 LightGBM의 네이티브 분기 처리에만 맡겼는데, 표본이 극히 적을 때(예: `asof_pitcher_n=1`) 원본 rate 값 자체가 통계적으로 불안정하다는 문제도 있어 아래 공식을 추가로 적용:

```
shrunk_r = (n * r + k * prior_r) / (n + k)      (k = 50)
```

- `prior_r`: 해당 rate 컬럼의 전역 평균, **학습 스플릿에서만** 계산 (`fit_shrinkage_priors`)
- `n=0`(cold start)이면 공식이 정확히 `prior_r`로 축소됨
- `k=50` 근거: train 기준 `asof_pitcher_n`/`asof_batter_n`의 1~5백분위수가 18~107이라, k=50이면 표본이 부족한 꼬리 구간만 유의미하게 보정하고 표본이 충분한 대다수 행은 원본 rate에 가깝게 유지됨
- 원본 `asof_*` 컬럼은 삭제하지 않고 그대로 유지 (LightGBM의 NaN 분기 처리가 "이 행이 cold-start였다"는 정보를 암묵적으로 담고 있어, `shrunk_*`와 원본이 상호보완적으로 공존)

| 원본 rate 컬럼 | 표본수 컬럼 | 출력 컬럼 |
|---|---|---|
| `asof_pitcher_success_rate` | `asof_pitcher_n` | `shrunk_pitcher_success_rate` |
| `asof_pitcher_reverse_rate` | `asof_pitcher_n` | `shrunk_pitcher_reverse_rate` |
| `asof_pitcher_middle_rate` | `asof_pitcher_n` | `shrunk_pitcher_middle_rate` |
| `asof_pitcher_ball_rate` | `asof_pitcher_n` | `shrunk_pitcher_ball_rate` |
| `asof_pitcher_strike_rate` | `asof_pitcher_n` | `shrunk_pitcher_strike_rate` |
| `asof_batter_success_rate` | `asof_batter_n` | `shrunk_batter_success_rate` |
| `asof_batter_middle_rate` | `asof_batter_n` | `shrunk_batter_middle_rate` |
| `asof_pitcher_fastball_rate` | `asof_pitcher_pitchmix_n` | `shrunk_pitcher_fastball_rate` |
| `asof_pitcher_breaking_rate` | `asof_pitcher_pitchmix_n` | `shrunk_pitcher_breaking_rate` |
| `asof_pitcher_offspeed_rate` | `asof_pitcher_pitchmix_n` | `shrunk_pitcher_offspeed_rate` |

**누수 안전성 검증 (실행 결과)**: 학습 스크립트 로그에서 `val_priors`(2019-2023만 사용)와 `final_priors`(2019-2024 전체)가 실제로 다르게 계산됨을 확인 — 예: `asof_pitcher_success_rate` 0.5402 → 0.5352, `asof_pitcher_reverse_rate` 0.2106 → 0.2152. 두 값이 다르다는 것 자체가 "매 스플릿마다 그 스플릿의 학습 데이터로만 다시 fit했다"는 증거 (검증/테스트 통계가 새어 들어갔다면 두 값이 우연히 같아지거나,애초에 분리할 필요가 없었을 것). 별도 스크립트로 `n=0`인 행에서 `shrunk_*` 값이 정확히 prior와 일치함도 확인함.

**결측치/이상값 점검**: `shrunk_*` 10개 컬럼 전부 NaN/inf 0건 (200,000행 샘플 검증). 새로 추가한 8개 파생 피처의 NaN 비율은 원본 소스 컬럼과 비슷한 수준 (예: `pitcher_success_under_pressure` 0.13% — `asof_pitcher_success_rate`/`li` 자체의 결측률과 일치, `pitcher_form_trend_isolated` 계열은 prev1/3/5 세 컬럼의 결측이 합쳐져 4.45%로 다소 높아짐 — LightGBM이 NaN을 네이티브로 처리하므로 문제 없음).

**검증되지 않은 채로 기각한 아이디어** (착수 전 리키지 위험으로 배제):
- 포수/심판 프레이밍·판정 성향 피처 — 공식 데이터에 포수 ID, 심판 ID 컬럼이 아예 존재하지 않음 (`docs/data_description.md` 전체 확인 완료). 없는 컬럼을 가정해 만들 수 없음.
- `pitcher_id`/`batter_id`/팀 단위 target encoding을 `train.csv`에서 fit해 적용 — `test.csv` 통계는 안 쓰지만, 이미 제공된 `asof_*` 행별 실시간 통계보다 정밀도가 떨어지고 금지된 "누적/빈도/target encoding" 패턴에 근접해 이번엔 배제.

### 모델 / 하이퍼파라미터

exp_001과 완전히 동일 (변경 없음 — 이번 실험은 피처 효과만 순수 측정하는 게 목적):
- `LGBMClassifier`, `objective="binary"`, `n_estimators=2000`(+ early stopping patience 100), `learning_rate=0.03`, `num_leaves=63`, `subsample=0.8`, `subsample_freq=1`, `colsample_bytree=0.8`, `min_child_samples=200`
- 범주형 3개(`top_bottom`, `game_type`, `base_state`)는 `OrdinalEncoder` 정수 인코딩 후 `categorical_feature`로 지정

### 시드

42

### 피처 개수

공식 47개 + 파생 23개(exp_001 15개 + exp_002 8개) + shrinkage 10개 = **총 80개**

### Brier Score

**0.248043** (exp_001: 0.248237, exp_000: 0.248769)

### 공식 로컬 스코어

`max(0, 100000*(1-brier/r(1-r)))`, 기준선 r(1-r) = 0.249807

**706.28** (exp_001 628.51 대비 **+77.77, 약 +12.4%**)

### best_iteration

134 (조기종료, patience 100 — exp_001의 173보다 빨리 수렴. 피처가 늘면서 각 트리가 더 적은 라운드로 같은 정보를 학습한 것으로 추정)

### 실행 시간

검증용 학습 11.4초 + 전체(2019-2024) 최종 재학습 11.1초 (exp_001과 비슷한 수준 — 피처 8개+10개 추가가 실행 시간에 미친 영향은 미미함)

### 예측값 통계

mean 0.4970 / min 0.3433 / max 0.6518 (exp_001: mean 0.4972 / min 0.3500 / max 0.6403 — 범위가 소폭 더 넓어짐, 극단 케이스에 대한 분별력이 조금 더 생긴 것으로 보임)

### 주요 피처 중요도 top 15

`season`, `asof_pitcher_n`, `pitcher_id`, `asof_pitcher_prev3_game_success_rate`, `asof_pitcher_prev5_game_success_rate`, `asof_pitcher_prev1_game_success_rate`, **`same_hand_matchup`**, **`shrunk_pitcher_success_rate`**, `asof_pitcher_ball_rate`, **`shrunk_pitcher_ball_rate`**, **`shrunk_pitcher_reverse_rate`**, **`shrunk_batter_success_rate`**, `asof_pitcher_reverse_rate`, `game_month`, `pitcher_team_id`

exp_002 신규 피처 중 **5개**(`same_hand_matchup`, `shrunk_pitcher_success_rate`, `shrunk_pitcher_ball_rate`, `shrunk_pitcher_reverse_rate`, `shrunk_batter_success_rate`)가 top 15에 진입 — shrinkage 계열이 특히 잘 먹힘. Family A(압박 상황 상호작용)와 Family B(추세/변동성)는 top 15엔 없었음 (하위권 기여로 추정, 다음 실험에서 feature importance 전체를 덤프해 정확히 확인 필요).

### 관찰 / 오류 분석

구간별 Brier / 실제 성공률 vs 평균 예측값 (2024 검증셋, `src/train_lgbm.py`가 자동 출력):

| 구간 | n | Brier | 실제 성공률 | 평균 예측 |
|---|---|---|---|---|
| two_strike=1 | 72,965 | 0.248510 | 0.4880 | 0.4950 |
| two_strike=0 | 180,542 | 0.247854 | 0.4853 | 0.4978 |
| is_close_game=1 | 113,660 | 0.248083 | 0.4921 | 0.5017 |
| is_close_game=0 | 139,847 | 0.248010 | 0.4812 | 0.4932 |
| cold_start (n<50) | 3,980 | 0.246804 | 0.4560 | 0.4812 |
| warm (n>=50) | 249,527 | 0.248062 | 0.4866 | 0.4973 |

- **접전(`is_close_game=1`)**과 **cold-start(`asof_pitcher_n<50`)** 구간에서 실제 성공률보다 평균 예측이 눈에 띄게 높음(각각 +0.0096, +0.0252) — 모델이 압박 상황/경험 부족 투수의 제구 저하를 아직 충분히 반영하지 못하고 있다는 신호. Family A(압박 상호작용)와 shrinkage를 넣었는데도 완전히 해소되진 않음 — k=50이 아직 부족하거나, `li`/`is_close_game`과의 상호작용이 더 필요할 수 있음.
- cold-start 구간(n=3,980, 전체의 1.6%)의 Brier 자체는 오히려 warm 구간보다 살짝 낮게(0.246804 vs 0.248062) 나왔는데, 이는 이 구간이 정확해서가 아니라 표본이 작고 실제 성공률(0.4560)과 평균 예측(0.4812) 모두 base rate 근처로 수렴해 있어 우연히 낮게 나왔을 가능성이 있음 — 오분류 방향성(과대예측)은 여전히 존재하므로 "이 구간을 잘 맞춘다"고 해석하면 안 됨.
- shrinkage prior가 스플릿별로 다르게 fit된 것을 로그로 확인 (누수 안전성 검증, 위 "피처 목록 E" 참고).

### 다음 가설

**목표(1115점) 대비 솔직한 평가**: exp_000→exp_001의 +212.94점(+51%) 점프는 피처 추가와 모델 교체(RF→LightGBM)를 동시에 바꿔서 나온 결과라 어느 쪽 기여가 얼마인지 분리되지 않았었다. 이번 exp_002는 모델을 고정하고 피처만 정교화해 **순수 피처 효과 +77.77점(+12.4%)**을 확인했는데, 이는 실험 원칙상 정직하고 의미 있는 결과이지만 1115점까지 남은 갭(+408.72, 현재 대비 +58%)을 이 방식(asof_* 정교화)만으로 채우긴 어려워 보인다. 다음 우선순위:

1. **`trackman_history.csv` 조인** (exp_002 범위에서 의도적으로 제외한 부분) — 구속/회전수/무브먼트 등 원시 물리 측정치는 현재 쓰고 있는 `asof_*` 집계보다 "제구"라는 타겟에 훨씬 더 직접적으로 연관될 가능성이 높음. `pitcher_id`↔`pitcher_trackman_id` 매핑 검증부터 필요 (exp_001에서도 이미 지적됨).
2. **압박 상황 처리 재검토**: 위 오류 분석에서 `is_close_game=1`/cold-start 구간의 과대예측이 여전히 남아있음 — `li` 구간별(예: 상위 10%만) 별도 상호작용, 또는 shrinkage의 `k` 값 튜닝(현재 50, 더 크게 해서 cold-start를 더 강하게 보정하는 것도 시도해볼 만함).
3. 모델 교체/앙상블(XGBoost 등)과 하이퍼파라미터 튜닝은 이번에도 보류 — exp_001의 "다음 가설"에서 이미 지적된 항목으로, trackman 조인 이후 별도 실험으로 분리해서 기여도를 각각 확인할 것.
4. 팀 회의에서 "asof_* 정교화만으로는 1115 목표에 부족하다"는 이 결론을 공유하고, trackman 조인 작업을 다음 실험(exp_003)으로 배정할지 논의 필요.

### 코드 구조 변경 (참고)

이번 실험과 함께 `submission/script.py`가 피처 로직을 손으로 복붙하던 것을 `src/features.py` 직접 import로 바꿨다 (파생 피처가 늘어날수록 손 동기화 누락 위험이 커지기 때문). Dacon 공식 zip 구조(`model/`, `script.py`, `requirements.txt`만 최상위)를 그대로 지키기 위해, `features.py`는 zip 루트가 아니라 `model/` 폴더 안에 넣도록 `src/package_submission.py`를 수정함 — `model/` 폴더 내부 파일 구성 자체는 공식 규격에 제약이 없음. 격리된 폴더에서 `submit.zip`을 풀어 `script.py`를 새 프로세스로 실행해 정상 동작 확인 완료 (5행 샘플, `row_id` 순서 일치, NaN/inf 없음, `[0,1]` 범위 확인).
