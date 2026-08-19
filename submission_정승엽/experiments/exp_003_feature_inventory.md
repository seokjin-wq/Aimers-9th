# exp_003 최종 피처 구성 정리 (원본 47개 + 파생 37개 = 84개)

트랙맨 분석을 시작하기 전, "지금까지의 EDA + 피처엔지니어링 + CatBoost"로
만들 수 있는 현재까지의 최선 모델(exp_003)이 정확히 어떤 컬럼을
쓰고 있는지 팀 공유용으로 정리한 문서. 코드상 진짜 소스는
[`src/features.py`](../src/features.py)이고, 이 문서는 그걸 사람이
읽기 좋게 옮긴 것 — 코드와 이 문서가 다르면 코드가 맞다.

**한 줄 요약**: 공식 원본 컬럼 47개는 **단 1개도 삭제하지 않고 전부
그대로** 모델에 넣었고, 그 위에 37개 파생 컬럼을 얹었다. 총 84개
피처.

---

## 0. 숫자로 보는 전체 구조

| 구분 | 개수 | 비고 |
|---|---|---|
| 원본 컬럼 (그대로 사용) | 47 | `test.csv`의 `row_id` 제외 전부 — 공식 baseline과 동일한 피처 집합 |
| 원본 컬럼 (삭제) | **0** | 중복 후보는 있었지만 실제로 뺀 건 없음 (§2 참고) |
| 파생 컬럼 — exp_001 | 15 | 카운트/점수/이닝 상황 플래그, 투수-타자 비교, 로그 변환 |
| 파생 컬럼 — exp_002 | 8 | 압박 상황 상호작용, 최근 폼 추세 분리, 손잡이 매치업 |
| 파생 컬럼 — exp_003 | 3 | 손잡이×구종 상호작용, 3볼×득점권주자 |
| 파생 컬럼 — shrinkage(exp_002 도입, exp_003 일부 강도 조정) | 10 | cold-start 보정된 asof_* 비율 |
| 파생 컬럼 — post-shrinkage(exp_003) | 1 | 투수×타자 품질 매치업 |
| **합계** | **84** | `src/features.py`의 `ALL_FEATURES` |

---

## 1. 원본 컬럼 47개 — 전부 그대로 사용

담당 그룹별로 나눠 정리했다(1~5번은 팀 EDA 분담 기준, `reports/eda_group1~5`
와 동일). "처리 방식" 열은 모델에 들어갈 때 범주형으로 인코딩되는지,
정수/실수 그대로 들어가는지를 뜻한다.

### 그룹1 — 시간·경기 정보, 손 유형·팀 ID, 선수 ID (12개)

| 컬럼 | 공식 설명 | 처리 방식 |
|---|---|---|
| `season` | 시즌 연도 | 숫자 그대로 |
| `game_month` | 경기 월 | 숫자 그대로 |
| `game_dayofweek` | 경기 요일 (월=0~일=6) | 숫자 그대로 |
| `inning` | 투구 직전 이닝 | 숫자 그대로 |
| `top_bottom` | 초(T)/말(B) 구분 | **범주형 인코딩**(CAT_COLS) |
| `game_type` | 경기 유형 코드 | **범주형 인코딩**(CAT_COLS) |
| `pitcher_id` | 투수 익명 ID | 숫자 그대로(정수 코드 자체를 피처로 사용) |
| `batter_id` | 타자 익명 ID | 숫자 그대로 |
| `pitcher_hand` | 투수 좌우 유형 코드 | 숫자 그대로 |
| `batter_hand` | 타자 좌우 유형 코드 | 숫자 그대로 |
| `pitcher_team_id` | 투수 소속 팀 ID | 숫자 그대로 |
| `batter_team_id` | 타자 소속 팀 ID | 숫자 그대로 |

### 그룹2 — 투구 직전 카운트 및 점수 상황 (8개)

| 컬럼 | 공식 설명 | 처리 방식 |
|---|---|---|
| `balls_before` | 투구 직전 볼 카운트 | 숫자 그대로 |
| `strikes_before` | 투구 직전 스트라이크 카운트 | 숫자 그대로 |
| `outs_before` | 투구 직전 아웃 카운트 | 숫자 그대로 |
| `run_top_before` | 투구 직전 초 공격팀 점수 | 숫자 그대로 |
| `run_bot_before` | 투구 직전 말 공격팀 점수 | 숫자 그대로 |
| `run_total_before` | 투구 직전 양팀 합산 점수 | 숫자 그대로 (§2 — 사실 100% 중복이지만 안 뺐음) |
| `score_diff_home` | 홈팀 기준 점수차 | 숫자 그대로 (§2 — 사실 100% 중복이지만 안 뺐음) |
| `score_diff_pitcher_team` | 투수팀 기준 점수차 | 숫자 그대로 |

### 그룹3 — 주자 상황 및 경기 중요도 (8개)

| 컬럼 | 공식 설명 | 처리 방식 |
|---|---|---|
| `runner_on_1b` | 1루 주자 여부 | 숫자 그대로 |
| `runner_on_2b` | 2루 주자 여부 | 숫자 그대로 |
| `runner_on_3b` | 3루 주자 여부 | 숫자 그대로 |
| `num_runners_on` | 출루 주자 수 | 숫자 그대로 (§2 — 사실 100% 중복이지만 안 뺐음) |
| `base_state` | 주자 배치 코드(`___`~`123`) | **범주형 인코딩**(CAT_COLS) |
| `home_win_expectancy` | 홈팀 기대 승률(0~100) | 숫자 그대로 |
| `away_win_expectancy` | 원정팀 기대 승률(0~100) | 숫자 그대로 (§2 — home과 거의 완전 보완관계지만 안 뺐음) |
| `li` | 상황 중요도(leverage index) | 숫자 그대로 |

### 그룹4 — 투수 과거 제구/구종 이력 (10개)

| 컬럼 | 공식 설명 | 처리 방식 |
|---|---|---|
| `asof_pitcher_n` | 투수 누적 투구 수 | 숫자 그대로 |
| `asof_pitcher_success_rate` | 투수 누적 제구 성공률 | 숫자 그대로(원본) — shrinkage 보정판도 별도로 추가(§4) |
| `asof_pitcher_reverse_rate` | 투수 누적 의도반대 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가 |
| `asof_pitcher_middle_rate` | 투수 누적 가운데/위험코스 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가 |
| `asof_pitcher_ball_rate` | 투수 누적 볼성 결과 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가 |
| `asof_pitcher_strike_rate` | 투수 누적 스트라이크성 결과 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가 |
| `asof_pitcher_pitchmix_n` | 구종 비율 계산용 표본 수 | 숫자 그대로 (§2 — `asof_pitcher_n`과 100% 동일하지만 안 뺐음) |
| `asof_pitcher_fastball_rate` | 투수 fastball 계열 사용 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가 |
| `asof_pitcher_breaking_rate` | 투수 breaking 계열 사용 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가 |
| `asof_pitcher_offspeed_rate` | 투수 offspeed 계열 사용 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가 |

### 그룹5 — 투수 최근 폼 추세 + 타자 상대 과거 기록 (9개)

| 컬럼 | 공식 설명 | 처리 방식 |
|---|---|---|
| `asof_pitcher_prev1_game_success_rate` | 직전 1경기 제구 성공률 | 숫자 그대로 |
| `asof_pitcher_prev3_game_success_rate` | 직전 3경기 제구 성공률 | 숫자 그대로 |
| `asof_pitcher_prev5_game_success_rate` | 직전 5경기 제구 성공률 | 숫자 그대로 |
| `asof_pitcher_prev1_game_middle_rate` | 직전 1경기 가운데/위험코스 비율 | 숫자 그대로 |
| `asof_pitcher_prev3_game_middle_rate` | 직전 3경기 가운데/위험코스 비율 | 숫자 그대로 |
| `asof_pitcher_prev5_game_middle_rate` | 직전 5경기 가운데/위험코스 비율 | 숫자 그대로 |
| `asof_batter_n` | 타자 상대 누적 투구 수 | 숫자 그대로 |
| `asof_batter_success_rate` | 타자 상대 제구 성공률 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가(k=150, §4) |
| `asof_batter_middle_rate` | 타자 상대 가운데/위험코스 비율 | 숫자 그대로(원본) — shrinkage 보정판도 별도 추가(k=150) |

---

## 2. "중복 후보"였지만 실제로는 안 뺀 컬럼 5개

각 그룹 EDA에서 "다른 컬럼으로 100% 재구성 가능(=수학적으로 중복)"
이라고 확인된 컬럼들이다. 그런데도 **아직 하나도 삭제하지 않았다** —
이유는 아래 표 참고. 전부 "삭제하지 말고 validation ablation으로
검증"이 원칙이었고(각 그룹 리포트 §중요 원칙), 시간상 그 ablation을
아직 안 돌렸다.

| 컬럼 | 어떤 컬럼으로 100% 재구성되는지 | 왜 아직 안 뺐나 |
|---|---|---|
| `run_total_before` | `run_top_before + run_bot_before` | 트리 모델은 분할 축이 다르면 학습 난이도가 달라질 수 있어(그룹2 리포트 §8), 빼기 전에 성능 비교 필요 |
| `score_diff_home` | `run_bot_before - run_top_before` | 상동 |
| `num_runners_on` | `runner_on_1b+2b+3b`의 합 | 상동(그룹3 리포트 §8) |
| `asof_pitcher_pitchmix_n` | `asof_pitcher_n`과 완전 동일 | 상동(그룹4 리포트 §11 — 이 그룹에서 가장 안전한 삭제 후보로 지목됐으나 아직 미실행) |
| `away_win_expectancy` | `100 - home_win_expectancy`(상관계수 -0.9999998) | 상동(그룹3 리포트 §10) |

**중요**: 이 5개는 "지금 모델에 들어가 있다"는 것이지, "빼면 안 된다"는
뜻이 아니다. 다음 실험(트랙맨 이후든 언제든) 여유가 생기면 이 5개를
하나씩 빼보는 ablation을 해볼 가치가 있다 — 특히 `asof_pitcher_pitchmix_n`이
가장 유력한 삭제 후보.

---

## 3. 파생 피처 26개 (`DERIVED_COLS`) — 실험별로 구분

### exp_001에서 추가된 15개

| 피처 | 계산식 | 의미 |
|---|---|---|
| `count_diff` | `strikes_before - balls_before` | 카운트 압박 방향 |
| `count_total` | `strikes_before + balls_before` | 카운트 진행도 |
| `two_strike` | `strikes_before == 2` | 2스트라이크 여부 |
| `three_ball` | `balls_before == 3` | 3볼 여부 |
| `full_count` | `two_strike & three_ball` | 풀카운트 여부 |
| `late_inning` | `inning >= 7` | 후반 이닝 여부 |
| `score_margin_abs` | `abs(score_diff_pitcher_team)` | 점수차 크기(방향 무관) |
| `is_close_game` | `score_margin_abs <= 1` | 접전 여부 |
| `runners_scoring_position` | `runner_on_2b==1 or runner_on_3b==1` | 득점권 주자 여부 |
| `pitcher_minus_batter_success` | `asof_pitcher_success_rate - asof_batter_success_rate` | 투수-타자 제구 성공률 차 |
| `pitcher_middle_minus_success` | `asof_pitcher_middle_rate - asof_pitcher_success_rate` | 가운데 비율과 성공률의 차 |
| `pitcher_recent_form_delta` | `prev1_success_rate - prev5_success_rate` | 단순 최근-장기 폼 차 |
| `pitcher_experience_log` | `log1p(asof_pitcher_n)` | 투수 경험치(로그 압축) |
| `batter_experience_log` | `log1p(asof_batter_n)` | 타자 경험치(로그 압축) |
| `pitchmix_diversity` | `1 - (fastball²+breaking²+offspeed²)` | 구종 다양성 지수 |

### exp_002에서 추가된 8개

| 피처 | 계산식 | 의미 / EDA 근거 |
|---|---|---|
| `pitcher_success_under_pressure` | `asof_pitcher_success_rate * li` | 중요 상황×제구 성공률 상호작용 |
| `pitcher_reverse_under_pressure` | `asof_pitcher_reverse_rate * li` | 중요 상황×의도반대 비율 상호작용 |
| `pitcher_success_x_risp` | `asof_pitcher_success_rate * runners_scoring_position` | 득점권×제구 성공률 상호작용 |
| `pitcher_form_trend_isolated` | `prev1 - (5*prev5-3*prev3)/2` | 중첩 윈도우를 대수적으로 분리한 "진짜 최근 추세"(`reports/eda_group5` §6에서 재검증 완료) |
| `pitcher_middle_trend_isolated` | 상동(가운데 비율 버전) | 상동 |
| `pitcher_form_volatility` | `max(prev1,prev3,prev5) - min(prev1,prev3,prev5)` | 최근 폼 변동성 |
| `batter_middle_minus_success` | `asof_batter_middle_rate - asof_batter_success_rate` | 타자 쪽 대칭 피처 |
| `same_hand_matchup` | `pitcher_hand == batter_hand` | 손잡이 매치업(platoon 신호) |

### exp_003에서 추가된 3개

| 피처 | 계산식 | EDA 근거 |
|---|---|---|
| `same_hand_x_breaking_rate` | `same_hand_matchup * asof_pitcher_breaking_rate` | `reports/eda_final` §B — 손 유형 조합 안에서도 구종 성향에 따라 성공률이 46.82~56.41%로 벌어짐 |
| `same_hand_x_offspeed_rate` | `same_hand_matchup * asof_pitcher_offspeed_rate` | 상동 |
| `three_ball_x_risp` | `three_ball * runners_scoring_position` | `reports/eda_final` §D — 3볼 상황에서 득점권 주자 유무가 outs=0/1에서 방향성을 보임(가설 수준) |

---

## 4. Cold-start 보정 피처 11개 (`SHRUNK_COLS` 10 + `POST_SHRINKAGE_COLS` 1)

표본이 적은 투수/타자의 비율값을 "전체 평균(prior) 쪽으로 끌어당겨"
보정한 컬럼들. 공식은 공통으로 `보정값 = (n*원래값 + k*prior) / (n+k)`
(자세한 설명은 이전 대화 참고). **exp_002에서 이 메커니즘 자체를
도입**했고, exp_003에서 두 가지를 바꿨다: (1) 타자 관련 2개 컬럼의
`k`를 50→150으로 올림, (2) prior를 "학습 기간 전체 평균" 대신
**"학습 기간 중 가장 최근 2개 시즌 평균"**으로 바꿈(시즌 하락 추세
반영, 컬럼 자체 목록은 안 바뀌고 계산 방식만 바뀜).

| 보정 컬럼 | 원본 컬럼 | 표본수 컬럼 | k | k 변경 이력 |
|---|---|---|---|---|
| `shrunk_pitcher_success_rate` | `asof_pitcher_success_rate` | `asof_pitcher_n` | 50 | exp_002부터 그대로 |
| `shrunk_pitcher_reverse_rate` | `asof_pitcher_reverse_rate` | `asof_pitcher_n` | 50 | exp_002부터 그대로 |
| `shrunk_pitcher_middle_rate` | `asof_pitcher_middle_rate` | `asof_pitcher_n` | 50 | exp_002부터 그대로 |
| `shrunk_pitcher_ball_rate` | `asof_pitcher_ball_rate` | `asof_pitcher_n` | 50 | exp_002부터 그대로 |
| `shrunk_pitcher_strike_rate` | `asof_pitcher_strike_rate` | `asof_pitcher_n` | 50 | exp_002부터 그대로 |
| `shrunk_batter_success_rate` | `asof_batter_success_rate` | `asof_batter_n` | **150** | exp_002땐 50 → exp_003에서 150으로 상향 |
| `shrunk_batter_middle_rate` | `asof_batter_middle_rate` | `asof_batter_n` | **150** | exp_002땐 50 → exp_003에서 150으로 상향 |
| `shrunk_pitcher_fastball_rate` | `asof_pitcher_fastball_rate` | `asof_pitcher_pitchmix_n` | 50 | exp_002부터 그대로 |
| `shrunk_pitcher_breaking_rate` | `asof_pitcher_breaking_rate` | `asof_pitcher_pitchmix_n` | 50 | exp_002부터 그대로 |
| `shrunk_pitcher_offspeed_rate` | `asof_pitcher_offspeed_rate` | `asof_pitcher_pitchmix_n` | 50 | exp_002부터 그대로 |
| `shrunk_pitcher_x_batter_success` | (post-shrinkage, 아래 참고) | — | — | exp_003 신규 |

`shrunk_pitcher_x_batter_success = shrunk_pitcher_success_rate *
shrunk_batter_success_rate` — `reports/eda_final` §H에서 발견한
"투수·타자 품질 매치업이 거의 가법적이지만 약한 곱셈적 잔차가 있다"는
관찰을 반영한 exp_003 신규 피처. **CatBoost 학습 결과 전체 84개 피처
중 중요도 3위**를 기록해, 실제로 유효하게 쓰이고 있음이 확인됨
(`experiments/exp_003_eda_features_and_model.md` 참고).

---

## 5. 피처 목록은 아니지만 함께 알아둘 변경 사항

- **모델**: LightGBM(exp_001/exp_002) → **CatBoost**(exp_003). 팀
  의견 + 실제 검증(로컬 723.17) 둘 다 CatBoost 쪽 손을 들어줌. 단
  LightGBM은 이 로컬 환경에서 원인 불명의 크래시가 나서 정식으로
  머리 대 머리 비교는 못 했다(환경 문제, 이번 실험 코드와 무관 —
  자세한 내용은 `experiments/exp_003_eda_features_and_model.md`).
- **범주형 처리 방식**: LightGBM 땐 `OrdinalEncoder`로 정수 인코딩이
  필요했지만, CatBoost는 `top_bottom`/`game_type`/`base_state`
  원본 문자열을 그대로 받는다(`cat_features` 인자로 지정).

---

## 참고

- 코드 원본: [`src/features.py`](../src/features.py)
- 이번 실험 전체 기록: [`experiments/exp_003_eda_features_and_model.md`](exp_003_eda_features_and_model.md)
- 근거가 된 EDA: `reports/eda_group1~5/README.md`, `reports/eda_final/README.md`
