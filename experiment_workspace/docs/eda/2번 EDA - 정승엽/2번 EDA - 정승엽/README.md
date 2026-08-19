# Group 2 EDA — 투구 직전 카운트 및 점수 상황

담당자 EDA 결과 정리. 실행 코드는 [`run_eda.py`](run_eda.py) (재실행:
`python reports/eda_group2/run_eda.py`, 실행 로그 원본은
[`eda_run_log.txt`](eda_run_log.txt)). 이 문서의 모든 수치는 그 로그와
`tables/*.csv`에서 그대로 가져왔다 — 추정치는 없음.

데이터: `data/train.csv` (2019~2024, 1,475,092행). `test.csv`는 사용하지
않았고, 여기 나온 어떤 값도 test.csv 피처 생성에 직접 대입하지 않는다
(CLAUDE.md 누수 규칙 6번 참고).

---

## 1. 담당 컬럼

| 컬럼 | 설명 |
|---|---|
| `balls_before` | 투구 직전 볼 카운트 |
| `strikes_before` | 투구 직전 스트라이크 카운트 |
| `outs_before` | 투구 직전 아웃 카운트 |
| `run_top_before` | 투구 직전 초 공격 팀의 점수 |
| `run_bot_before` | 투구 직전 말 공격 팀의 점수 |
| `run_total_before` | 투구 직전 양 팀 합산 점수 |
| `score_diff_home` | 투구 직전 홈 팀 기준 점수 차 |
| `score_diff_pitcher_team` | 투구 직전 투수 소속 팀 기준 점수 차 |

---

## 2. 데이터 품질

- Shape: `(1,475,092, 49)` 중 담당 8개 컬럼 + `control_success` + 검증용
  `season`/`top_bottom` 사용.
- **결측치 0건** (8개 컬럼 전부), dtype 전부 `int64`.
- 범위/unique 개수 (전체: [`00_quality_summary.csv`](tables/00_quality_summary.csv)):

| 컬럼 | min | max | unique |
|---|---|---|---|
| `balls_before` | 0 | 3 | 4 |
| `strikes_before` | 0 | 2 | 3 |
| `outs_before` | 0 | 2 | 3 |
| `run_top_before` | 0 | 30 | 30 |
| `run_bot_before` | 0 | 26 | 25 |
| `run_total_before` | 0 | 37 | 38 |
| `score_diff_home` | -27 | 20 | 47 |
| `score_diff_pitcher_team` | -27 | 27 | 52 |

- **야구 규칙 범위 검사** ([`02_legal_range_check.csv`](tables/02_legal_range_check.csv)):
  `balls_before∈[0,3]`, `strikes_before∈[0,2]`, `outs_before∈[0,2]` 모두
  **범위 이탈 0건** — 비정상값 없음.

### 파생 관계 검증 ([`01_derived_relationships.csv`](tables/01_derived_relationships.csv))

전 행(n=1,475,092)에 대해 세 관계 모두 **100.000% 일치**:

| 관계 | 일치 | 불일치 | 일치율 |
|---|---|---|---|
| `run_total_before == run_top_before + run_bot_before` | 1,475,092 | 0 | 100.000% |
| `score_diff_home == run_bot_before - run_top_before` | 1,475,092 | 0 | 100.000% |
| `score_diff_pitcher_team == (top_bottom=='T' ? score_diff_home : -score_diff_home)` | 1,475,092 | 0 | 100.000% |

반대 부호 가설(`top_bottom=='T' ? -score_diff_home : score_diff_home`)은
25.571%만 일치해 기각 — `top_bottom=='T'`(초, 원정팀 공격 = 홈팀 투구)일
때 `score_diff_pitcher_team == score_diff_home`가 정확한 관계임을 데이터로
확인했다 (야구 규칙과도 일치: 초에는 홈팀이 수비/투구).

**결론**: `run_total_before`, `score_diff_home`, `score_diff_pitcher_team`
3개 컬럼은 `run_top_before`, `run_bot_before`, `top_bottom` 3개로부터
결정론적으로 100% 재구성 가능 — 수학적으로 중복 (§8, §11에서 다룸).

---

## 3. 단변량 분석

전체 통계 ([`03_univariate_stats.csv`](tables/03_univariate_stats.csv)):

| 컬럼 | mean | std | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|
| `balls_before` | 0.898 | 0.970 | 0 | 1 | 2 | 3 |
| `strikes_before` | 0.872 | 0.825 | 0 | 1 | 2 | 2 |
| `outs_before` | 0.981 | 0.817 | 0 | 1 | 2 | 2 |
| `run_top_before` | 2.558 | 2.914 | 0 | 2 | 4 | 30 |
| `run_bot_before` | 2.357 | 2.766 | 0 | 1 | 4 | 26 |
| `run_total_before` | 4.915 | 4.501 | 1 | 4 | 7 | 37 |
| `score_diff_home` | -0.201 | 3.469 | -2 | 0 | 1 | 20 |
| `score_diff_pitcher_team` | 0.060 | 3.475 | -2 | 0 | 2 | 27 |

- 카운트형 3개(balls/strikes/outs) 모두 우측으로 완만하게 감소하는
  분포 — 0이 가장 흔하고 값이 커질수록 표본이 줄어듦 (막대그래프:
  `figures/01_bar_*.png`).
- `run_top_before`/`run_bot_before`는 전형적인 득점 분포(0~1점이 최빈,
  긴 우측 꼬리, 최대 26~30점의 극단적 블로아웃 존재).
- `score_diff_home`(평균 -0.20)과 `score_diff_pitcher_team`(평균 +0.06)은
  거의 대칭이고 중앙값 0 — 관점만 다를 뿐 분포 모양은 사실상 동일(§2의
  부호 반전 관계 때문에 당연한 결과).
- 히스토그램(`02_hist_*`), 1~99% 확대 히스토그램(`03_hist_zoom_*`),
  박스플롯(`04_box_*`) 전부 `figures/`에 저장.

---

## 4. Count 분석 (`balls_before × strikes_before`)

표: [`05_count_bxs_success_rate.csv`](tables/05_count_bxs_success_rate.csv),
[`05_count_bxs_n.csv`](tables/05_count_bxs_n.csv). 히트맵:
`figures/05_heatmap_count_success_rate.png`,
`figures/06_heatmap_count_sample_size.png`.

- **볼카운트(`balls_before`)가 늘수록 성공률이 낮아지는 패턴이
  strikes 값과 무관하게 일관되게 나타남**: strikes=0일 때
  0.527→0.525→0.519→0.507, strikes=1일 때 0.534→0.528→0.522→0.504,
  strikes=2일 때 0.519→0.524→0.521→0.500 — 세 줄 모두 `balls=3` 열이
  최저.
- `strikes_before` 자체의 효과는 약하고 비단조적(전체 평균: 0스트라이크
  52.49%, 1스트라이크 52.76%(최고), 2스트라이크 51.80%(최저)).

### 특정 카운트 (§5b, [`05_flagged_counts.csv`](tables/05_flagged_counts.csv))

전체 평균 52.38% 대비:

| 카운트 | n | 성공률 | 전체 대비 |
|---|---|---|---|
| 0-0 | 380,996 | 52.66% | +0.28%p |
| 0-2 | 89,281 | 51.85% | -0.52%p |
| 3-0 | 18,060 | 50.73% | -1.65%p |
| 3-1 | 35,425 | 50.44% | -1.94%p |
| **3-2 (풀카운트)** | 70,538 | **49.96%** | **-2.42%p** |

풀카운트(3-2)가 5개 중 성공률이 가장 낮음 — 야구 직관(가장 압박된
카운트)과 일치.

### 시즌별 비교 (§5d, [`05_flagged_counts_by_season.csv`](tables/05_flagged_counts_by_season.csv))

| season | 0-0 | 0-2 | 3-0 | 3-1 | 3-2 |
|---|---|---|---|---|---|
| 2019 | 57.13% | 53.48% | 54.46% | 56.17% | 55.67% |
| 2020 | 53.27% | 53.20% | 50.50% | 51.07% | 50.55% |
| 2021 | 53.64% | 53.16% | 52.12% | 50.93% | 51.42% |
| 2022 | 53.16% | 52.18% | 50.62% | 50.95% | 50.17% |
| 2023 | 50.29% | 50.18% | 48.78% | 48.03% | 46.56% |
| 2024 | 48.63% | 49.23% | 48.20% | 45.91% | 45.70% |

0-0 대비 3-2 격차가 2019년 1.46%p → 2024년 2.93%p로 확대되는 경향
(§7에서 다시 다룸).

---

## 5. Outs 분석

([`06_outs_summary.csv`](tables/06_outs_summary.csv))

| outs_before | n | 성공률 | 전체 대비 |
|---|---|---|---|
| 0 | 505,924 | 52.14% | -0.24%p |
| 1 | 490,634 | 52.39% | +0.01%p |
| 2 | 478,534 | 52.61% | +0.24%p |

`outs_before` **단독 효과는 매우 작음**(0.5%p 범위 이내).

### balls × strikes × outs 3-way ([`06_count_outs_3way.csv`](tables/06_count_outs_3way.csv))

36개 조합 모두 표본 500건 이상(최소 n=5,972) — 표본 부족 조합 없음.
전체 대비 편차가 가장 큰(낮은) 3개 조합:

| balls | strikes | outs | n | 성공률 | 전체 대비 |
|---|---|---|---|---|---|
| 3 | 1 | 0 | 11,711 | 48.98% | **-3.40%p** |
| 3 | 0 | 0 | 5,991 | 49.19% | -3.19%p |
| 3 | 2 | 0 | 23,441 | 49.18% | -3.19%p |

흥미로운 점: 카운트만 봤을 땐(§4) 3-2(풀카운트)가 가장 낮았지만,
`outs_before`까지 함께 보면 **"3볼 + 무사(0아웃)" 조합이 strikes 값과
무관하게 가장 낮다** (3-1-0, 3-0-0, 3-2-0이 상위 3개 최저 조합을
모두 차지, outs=1·2에서는 3볼 페널티가 훨씬 완화됨 — 예: 3-1-1은
-1.90%p, 3-1-2는 -0.56%p). 즉 `outs_before`는 단독 신호는 약하지만
카운트와 상호작용할 때는 신호가 커짐.

---

## 6. Score 분석

Raw 값별 그룹은 [`07_score_diff_pitcher_team_raw.csv`](tables/07_score_diff_pitcher_team_raw.csv) /
[`07_score_diff_home_raw.csv`](tables/07_score_diff_home_raw.csv) 참고 —
단, `|score_diff| > 15` 구간은 표본이 급감(n<100, 일부 n<5)해서 성공률이
매우 불안정하다 (예: `score_diff_pitcher_team=-26`는 n=2, 성공률 0% —
사실상 노이즈, 해석 금지).

### 구간화 (단순 기준, 최적화 아님)

`score_diff_pitcher_team` 기준 5구간
(큰 열세 ≤-4 / 열세 -3~-1 / 동점 0 / 리드 1~3 / 큰 리드 ≥4),
[`07_score_diff_pitcher_bins.csv`](tables/07_score_diff_pitcher_bins.csv),
그림 `figures/07_score_bins_success_rate.png`:

| 구간 | n | 성공률 | 전체 대비 |
|---|---|---|---|
| 큰 열세(≤-4) | 178,321 | 51.04% | -1.33%p |
| 열세(-3~-1) | 359,384 | 52.25% | -0.12%p |
| **동점(0)** | 377,192 | **53.01%** | **+0.63%p (최고)** |
| 리드(1~3) | 373,161 | 52.56% | +0.18%p |
| 큰 리드(≥4) | 187,034 | 52.26% | -0.12%p |

**동점 상황이 성공률이 가장 높고, 큰 열세가 가장 낮다.** 주목할 점은
비대칭성 — 큰 열세(-1.33%p)가 큰 리드(-0.12%p)보다 훨씬 큰 폭으로
성공률을 낮춘다. 열세와 큰 리드는 편차 크기가 거의 같다(-0.12%p대).

### EDA 전용 파생 후보

- `score_state` (leading/tied/trailing, [`07_score_state.csv`](tables/07_score_state.csv)):
  tied 53.01%(+0.63%p) > leading 52.46%(+0.08%p) > trailing 51.85%(-0.52%p).
- `is_lopsided` (`|score_diff_pitcher_team|>=4`, [`07_is_lopsided.csv`](tables/07_is_lopsided.csv)):
  0(접전) 52.61%(+0.23%p) vs 1(블로아웃) 51.66%(-0.71%p) — 블로아웃
  상황에서 성공률이 낮음.

### run_top/run_bot/run_total_before

원점수 계열은 득점 자체보다 "경기 진행도"에 가까운 스케일 변수로
보인다 — `run_total_before`는 0점(53.27%, +0.89%p)에서 시작해 총점이
커질수록 대체로 감소하는 완만한 하향 추세를 보이나(10점대 대부분
-0.5~-1%p), 25점 이상 구간은 표본이 급감해(n<100, 일부 한 자릿수)
해석하지 않는다.

---

## 7. 시즌별 안정성 (Season Drift) — **가장 중요한 발견**

([`08_season_overall.csv`](tables/08_season_overall.csv), 그림
`figures/08_season_overall_trend.png`)

| season | n | 성공률 | 전체 대비 |
|---|---|---|---|
| 2019 | 237,413 | **56.47%** | +4.09%p |
| 2020 | 244,087 | 53.27% | +0.89%p |
| 2021 | 247,088 | 53.28% | +0.90%p |
| 2022 | 247,472 | 52.89% | +0.52%p |
| 2023 | 245,525 | 50.00% | -2.38%p |
| 2024 | 253,507 | **48.61%** | -3.77%p |

**전체 제구 성공률이 2019년 56.47%에서 2024년 48.61%까지 6개 시즌
동안 거의 단조적으로 7.85%p 하락**한다. 이는 이번 그룹의 어떤 단일
변수 효과(가장 큰 게 풀카운트 -2.42%p)보다도 훨씬 큰 폭이다.

### 시즌별 score-bin 추이 ([`08_season_score_bin.csv`](tables/08_season_score_bin.csv), `figures/09_season_score_bin_trend.png`)

5개 구간 모두 함께 하락하며, **동점 구간이 대부분의 시즌에서 최고
순위, 큰 열세 구간이 대부분의 시즌에서 최저 순위를 유지** — 절대
수준은 시즌마다 이동해도 구간 간 상대적 순서는 비교적 안정적.

### 시즌별 카운트 효과

§4에서 본 것처럼 0-0 대비 3-2 격차가 2019년 1.46%p → 2024년 2.93%p로
확대 — 전체 하락과는 별개로 **풀카운트의 상대적 페널티 자체가
최근 시즌에 커지고 있을 가능성**(확정 아님, 통계적 재검증 필요).

**중요**: 전체 기간 평균만 보고 어떤 효과를 "이 정도 크기"라고
단정하면 안 된다 — 시즌 자체가 크게 이동하고 있어서, 특히 2025년
예측 시 2024년보다도 더 낮은 기저율을 가정하는 게 안전할 수 있다.

---

## 8. 중복 변수

§2에서 확인한 대로 `run_total_before`, `score_diff_home`,
`score_diff_pitcher_team` 3개는 `run_top_before`, `run_bot_before`,
`top_bottom` 으로부터 100% 결정론적으로 재구성된다 — 정보량 관점에서
완전 중복. 단, 트리 기반 모델은 어느 축으로 분할하느냐에 따라 학습
난이도가 달라질 수 있어(예: "총점 7점 이하" 분할은 `run_total_before`
하나로 되지만 `run_top_before`+`run_bot_before` 조합으로는 표현이
복잡해짐), **삭제를 지금 결정하지 않는다** — §11 참고.

---

## 9. 주요 발견 (요약)

- 시즌 전체 하락 추세(-7.85%p, 2019→2024)가 이번 그룹에서 관측된
  가장 큰 신호이며, 어떤 개별 카운트/점수차 효과보다 크다.
- 볼카운트가 늘수록(특히 3볼) 성공률이 낮아지는 패턴이 일관됨;
  스트라이크 단독 효과는 약하고 비단조적.
- 풀카운트(3-2)가 카운트 단독 기준으로는 최저지만, outs까지 보면
  "3볼+무사(0아웃)" 조합이 strikes 값과 무관하게 더 낮음 — outs와
  count의 상호작용 신호가 outs 단독보다 강함.
- 큰 점수차 열세가 큰 점수차 리드보다 제구에 더 크게(비대칭적으로)
  악영향 — 열세 압박이 리드 여유보다 효과가 큼.
- `run_total_before`/`score_diff_home`/`score_diff_pitcher_team`은
  수학적으로 100% 중복(재구성 가능).
- 8개 컬럼 각각의 marginal 효과는 대체로 ±2%p 이내로 작아, 단독보다
  `asof_*` 투수 이력 계열과의 상호작용에서 더 큰 힘을 발휘할 가능성.

---

## 10. Feature Engineering 후보

| 후보 | 야구적 의미 | EDA 근거 | 잠재적 중복성 | 누수 위험 | 검증 필요성 |
|---|---|---|---|---|---|
| `count_state` (balls,strikes 조합) | 카운트 상황 자체를 범주로 | §4 히트맵 — balls축 효과 뚜렷 | `src/features.py`의 `count_diff`/`count_total`과 정보 중복 가능 | 없음(행 단위) | validation에서 raw count_diff/total 대비 성능 비교 필요 |
| `is_full_count` (3-2) | 가장 압박된 카운트 | 3-2 성공률 -2.42%p (5개 중 최저) | **이미 `src/features.py`의 `full_count`로 존재** | 없음 | 신규 아님 — 그대로 유지 |
| `is_three_ball` (balls==3) | 볼넷 위기 상황 | balls=3에서 strikes 무관하게 일관된 최저 | `three_ball`(=strikes 무관 balls==3)로 **이미 존재** | 없음 | 신규 아님 |
| `balls_minus_strikes` | 카운트 압박 방향 | balls 효과가 strikes보다 뚜렷 (§4) | `count_diff = strikes-balls`로 **이미 존재**(부호 반대) | 없음 | 부호만 다름, 신규 불필요 |
| `abs_score_diff` | 점수차 크기(방향 무관) | §6 — 큰 점수차일수록 하락 | **`score_margin_abs`(=`abs(score_diff_pitcher_team)`)로 이미 존재** | 없음 | 신규 아님 |
| `score_state` (leading/tied/trailing) | 승부 흐름 방향 | tied > leading > trailing (§6) | 없음(범주 3분류는 신규) | 없음 | 3-way 범주 인코딩으로 validation 실험 가치 있음 |
| `is_lopsided` (\|diff\|>=4) | 블로아웃 여부 | 블로아웃 성공률 -0.71%p (§6) | 기존 `is_close_game`(\|diff\|<=1)의 반대 방향 개념 — **완전 신규는 아님** | 없음 | 임계값(1 vs 4)이 다르므로 어느 쪽이 더 나은지 ablation 필요 |
| `outs_before × is_three_ball` (신규 제안) | 무사 만루/무사 3볼 압박 | §5 — 3볼+0아웃 조합이 3-way 최저 | 없음 | 없음 | exp_003 후보로 검증 |

**중요**: EDA만으로 위 후보를 채택하거나 기각하지 않는다 — 2019-2023
학습/2024 검증에서 실제 비교해야 함.

---

## 11. 삭제 후보

| 컬럼 | 근거 | 처리 방침 |
|---|---|---|
| `run_total_before` | `run_top_before+run_bot_before`와 100% 일치 (§2) | 삭제하지 말고, baseline vs 컬럼 제거 ablation을 2019-2023 학습/2024 검증에서 별도 실험 |
| `score_diff_home` | `run_bot_before-run_top_before`와 100% 일치 (§2) | 상동 |
| `score_diff_pitcher_team` | `score_diff_home`와 `top_bottom`의 조합으로 100% 재구성 (§2) | 상동 — 단, 투수 관점 정보라 모델이 가장 직접적으로 활용할 축일 수 있어 3개 중 우선 순위가 가장 낮은 삭제 후보 |

공식 베이스라인은 `test.csv`의 모든 컬럼(row_id 제외)을 그대로 쓰는
것이 기준이므로(`CLAUDE.md` "Official Baseline"), 이 컬럼들을 빼는 건
베이스라인에서 벗어나는 변경이다 — **"중복이니 삭제"로 결론 내지 않고**,
반드시 baseline vs removal 비교 실험(가칭 exp_004)을 거쳐야 한다.

---

## 12. 추가 교차 분석 후보 (담당 범위 밖 — 코드 없이 후보만 정리)

| 후보 | 왜 필요해 보이는지 | 확인하려는 혼재효과 |
|---|---|---|
| `inning × score_diff_pitcher_team` | 이닝 후반 접전이 특히 중요할 수 있음 | 이닝 단계별로 점수차 효과 크기가 다른지 |
| `outs_before × runner situation`(`runner_on_*`, `base_state`) | §5에서 outs가 카운트와 상호작용함을 확인 | 득점권 주자 + 아웃수 조합의 압박 효과 |
| `count(balls×strikes) × li`(leverage index) | exp_002에서 이미 `pitcher_success_under_pressure` 등 li 상호작용 피처 사용 중 | 풀카운트 페널티가 고leverage 상황에서 더 커지는지 |
| `score_diff × inning` | 블로아웃 효과(§6)가 이닝 초반/후반에 다를 수 있음 | is_lopsided 효과가 이닝 단계별로 일관적인지 |
| `count × season` | §7에서 풀카운트 페널티가 최근 시즌에 커지는 경향 관측 | 통계적으로 유의한 추세인지, 표본수 재확인 |
| `count/score × asof_pitcher_*` | 8개 컬럼 단독 효과는 작음(§9) | 투수 이력과 결합 시 신호가 커지는지 |

---

## 13. 팀 회의용 핵심 결론

1. **관찰**: 전체 제구 성공률이 2019→2024 사이 꾸준히 하락한다.
   **근거**: 2019 56.47% → 2020 53.27% → 2021 53.28% → 2022 52.89% →
   2023 50.00% → 2024 48.61% (전체 평균 52.38%).
   **해석**: 시즌 자체의 기저율이 시간에 따라 우하향하는 뚜렷한
   패턴 — 원인은 데이터만으로 단정할 수 없음(연맹 규정/판정기준
   변화 등 여러 가설 가능).
   **다음 action**: 2025 예측 시 2024 수준 이하의 기저율을 가정하는
   것을 검토. exp_002의 shrinkage prior(현재 2019-2024 전체 평균
   기반)가 이 하락 추세를 반영 못할 가능성 — 최근 시즌 가중 방식을
   validation에서 비교.

2. **관찰**: 볼카운트가 늘수록(특히 3볼) 성공률이 낮아지고, 그 중
   풀카운트(3-2)가 카운트 단독 기준 최저다.
   **근거**: `balls_before` 0→3 성공률 52.76%→52.59%→52.08%→50.21%;
   3-2 카운트 49.96%(전체 대비 -2.42%p, 5개 특정 카운트 중 최저).
   **해석**: 투수가 불리해질수록 제구 난도가 높아진다는 야구 직관과
   일치.
   **다음 action**: 관련 피처(`full_count`, `three_ball`, `count_diff`)는
   이미 `src/features.py`에 있으므로 신규 추가보다 validation에서
   중요도·기여도 재확인.

3. **관찰**: `outs_before` 단독 효과는 미미하지만, 카운트와 결합하면
   "3볼+무사(0아웃)" 조합이 strikes 값과 무관하게 가장 낮다(풀카운트
   단독보다도 낮음).
   **근거**: outs 0/1/2 성공률 52.14%/52.39%/52.61%(0.5%p 이내); 3-way
   최저 3개 조합이 전부 "balls=3, outs=0"(3-1-0 -3.40%p, 3-0-0
   -3.19%p, 3-2-0 -3.19%p), 반면 3-1-1은 -1.90%p, 3-1-2는 -0.56%p로
   outs가 늘수록 페널티가 크게 완화됨.
   **다음 action**: `outs_before × is_three_ball`(또는 3-way 조합) 상호작용
   피처를 exp_003 후보로 검증.

4. **관찰**: 큰 점수차 열세가 큰 점수차 리드보다 제구에 더 크게
   (비대칭적으로) 악영향을 준다.
   **근거**: 큰 열세(≤-4) 51.04%(-1.33%p) vs 큰 리드(≥4) 52.26%
   (-0.12%p) — 열세 쪽 편차가 약 11배 큼. `is_lopsided`(블로아웃)도
   51.66%(-0.71%p)로 낮음.
   **해석**: 큰 점수차로 뒤지는 압박이 큰 리드의 여유보다 제구에
   더 강하게 작용하는 패턴("연관"이며 인과 단정 아님).
   **다음 action**: `score_state`, `is_lopsided`를 validation에서 검증.
   단 `is_lopsided`(|diff|≥4)는 기존 `is_close_game`(|diff|≤1)과
   방향은 다르지만 개념이 겹치므로, 신규 피처보다 임계값 비교
   실험으로 진행.

5. **관찰**: `run_total_before`, `score_diff_home`,
   `score_diff_pitcher_team` 3개 컬럼은 수학적으로 완전히 중복이다.
   **근거**: `run_total_before == run_top_before+run_bot_before`
   100.000% 일치(1,475,092/1,475,092); `score_diff_home ==
   run_bot_before-run_top_before` 100.000% 일치;
   `score_diff_pitcher_team`의 부호가 `top_bottom`에 따라 정확히
   재구성됨(100.000% 일치, 반대 부호 가설은 25.571%만 일치해 기각).
   **해석**: 5개 컬럼이 실질적으로 `run_top_before`,
   `run_bot_before`, `top_bottom` 3개의 정보로 환원 가능.
   **다음 action**: 지금 삭제하지 않는다. 2019-2023 학습/2024
   검증에서 baseline vs 컬럼 제거 ablation을 별도 실험(exp_004
   후보)으로 진행.

6. **관찰**: 카운트 효과의 시즌별 상대 순위는 대체로 유지되지만,
   풀카운트의 상대적 페널티 자체는 최근 시즌에 더 커지는 경향이
   있다.
   **근거**: 0-0 대비 3-2 격차가 2019년 1.46%p(57.13% vs 55.67%)에서
   2024년 2.93%p(48.63% vs 45.70%)로 확대.
   **해석**: 시즌 전체 하락과는 별개로 카운트 효과의 "크기" 자체가
   비정상적(non-stationary)일 가능성 — 확정 아님.
   **다음 action**: `count × season` 상호작용을 통계적으로 재검증
   (표본수 포함), 확정되면 count 관련 피처에 최근 시즌 가중을 고려.

7. **관찰**: 이번 그룹(카운트·점수) 8개 컬럼의 단독 효과는 대부분
   ±2%p 이내로, 시즌 효과(-7.85%p)나 `asof_*` 투수 이력 계열보다
   작다.
   **근거**: 그룹 내 최대 단일 효과는 풀카운트 -2.42%p; 시즌 효과는
   그 3배 이상.
   **해석**: 카운트/점수 정보 단독으로는 강한 신호가 아니며,
   `asof_pitcher_*` 계열(exp_001/exp_002에서 이미 feature importance
   상위권 차지)과 결합해야 실질적 힘을 발휘할 가능성이 높음.
   **다음 action**: `count/score × asof_pitcher_*` 상호작용 피처를
   §12 교차분석 후보에 포함해 exp_003 이후 우선 검증.

---

## 14. 중요 원칙 (본 EDA 전체에 적용)

- raw data(`data/train.csv`) 수정 없음, test data 기반 fitting/분포
  사용 없음, 미래 정보 사용 없음.
- EDA 결과만으로 컬럼을 채택·제거하지 않음 — 모든 후보는 validation
  ablation이 필요하다고 명시.
- 상관관계가 낮다는 이유만으로 제거 결정을 내리지 않음.
- 이 문서의 모든 수치는 `eda_run_log.txt`와 `tables/*.csv`에서 실제
  실행된 값만 사용 — 추정치 없음.
- 작은 차이(<1%p 수준)는 과도하게 해석하지 않음, 표현은 "연관"·
  "패턴"·"가설"로 한정 — 인과관계로 서술하지 않음.
