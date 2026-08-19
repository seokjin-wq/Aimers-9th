# exp_004 — 피처 단순화 시도 (기각됨, 변경 없음)

---

## 실험 개요

- **실험 ID**: exp_004
- **날짜 / 담당자**: 2026-08-19 / Claude(대화 세션)
- **가설**: exp_003 CatBoost 모델의 실제 feature importance(84개 전체)를
  보니 (1) `run_total_before`/`num_runners_on`/`asof_pitcher_pitchmix_n`/
  `away_win_expectancy`/`score_diff_home` 등 EDA에서 이미 "100% 수학적
  중복"으로 확인된 원본 컬럼과 (2) `top_bottom`/`runner_on_1b`/
  `runner_on_2b`(importance 정확히 0.000)를 모델 입력에서 빼고, 동시에
  EDA에서 검증됐지만 아직 피처로 안 만든 후보 5개(`pitcher_team_win_expectancy`,
  `three_ball_zero_outs`, `pitcher_cold_start`, `batter_cold_start`,
  `bases_loaded`)를 추가하면 exp_003(723.17)보다 같거나 나은 점수를
  유지하면서 피처 수는 줄일 수 있을 것이다.
- **기준(baseline)**: exp_003 (CatBoost, local score 723.17, Brier 0.248000).
- **결과 요약: 가설 기각.** 테스트한 4가지 조합 전부 exp_003보다
  낮은 점수를 기록했다 — **`src/features.py`는 변경 없이 exp_003
  상태 그대로 유지한다.**
- **검증 방법**: season 2019-2023 학습 / 2024 검증 (기존과 동일).
- **누수 위험 검토**: exp_003과 동일한 season-aware shrinkage(학습
  스플릿의 최근 2개 시즌만 prior로 사용) 그대로 사용 — 새로 추가/
  검토한 피처는 전부 행 단위(row-local) 계산이라 누수 위험 없음.

---

## 실행한 4가지 조합과 결과

CatBoost만 사용(LightGBM은 이 환경에서 여전히 크래시 — exp_003 문서
참고), 하이퍼파라미터는 exp_003과 동일. 원 계획(plan)대로 "제거만",
"추가만"으로 나눠 개별 기여도를 분리했고, 추가로 "추가 중 importance
0인 피처만 뺀 버전"까지 한 번 더 확인했다.

| 실행 | 구성 | 로컬 점수 | exp_003(723.17) 대비 |
|---|---|---|---|
| exp_003 (기준) | 원본 47개 + 파생 26개 + shrinkage 10개 + post-shrinkage 1개 = 84개 | **723.17** | — |
| 전체 번들 | 원본 8개 제거 + 신규 5개 추가 (80개) | 715.71 | **-7.46** |
| 제거만 | 원본 8개만 제거, 신규 피처 추가 없음 (75개, `three_ball_x_risp`는 코드에서 이미 빠져있어 자동 제외) | 717.24 | **-5.93** |
| 추가만 | 원본 47개 전부 유지 + 신규 5개 추가 (88개) | 721.32 | **-1.85** |
| 추가만(죽은 피처 2개 제외) | 원본 47개 유지 + `pitcher_cold_start`/`batter_cold_start` 뺀 신규 3개만 (86개) | 716.07 | **-7.10** |

(전체 로그: `experiments/exp004_run_log.txt`,
`experiments/exp004_ablation_removal.txt`,
`experiments/exp004_ablation_addition.txt`,
`experiments/exp004_ablation_addition_pruned.txt`)

---

## 관찰 — 왜 기각했는가, 그리고 배운 점

1. **"100% 수학적 중복" 컬럼도 실제로는 도움이 되고 있었다.**
   `run_total_before`, `num_runners_on` 등은 다른 컬럼으로부터 정보
   손실 없이 재구성 가능하다는 게 EDA에서 확실히 검증됐지만, 그걸
   모델 입력에서 빼자 점수가 5.93점이나 떨어졌다. CatBoost 같은
   트리 모델은 같은 정보라도 "어느 축으로 분할하느냐"에 따라 트리
   구조/학습 난이도가 달라질 수 있다는 각 그룹 EDA 리포트의 경고
   (예: `reports/eda_group2` §8)가 정확히 들어맞은 사례 — **수학적
   중복 ≠ 모델 입력으로서 무가치**라는 걸 실측으로 확인했다.
2. **낮은/0인 feature importance가 "빼도 안전하다"는 신호는 아니었다.**
   `pitcher_cold_start`/`batter_cold_start`는 두 번의 독립된 실행
   (전체 번들, 추가만) 모두에서 importance가 정확히 0.000이었다 —
   즉 트리가 단 한 번도 이 두 컬럼으로 분할하지 않았다. 그런데 이
   둘을 "추가만" 조합에서 뺐더니(추가만-죽은피처제외) 점수가
   **721.32 → 716.07로 오히려 5점 넘게 더 떨어졌다.** 이건 두 피처
   자체가 유익했다기보다, CatBoost 학습 과정의 실행별 변동성(feature
   샘플링, early stopping 시점 차이 등)이 우리가 보고 있는 몇 점
   단위 차이보다 클 수 있다는 뜻이다 — **이 정도 스케일의 변경은
   importance 숫자 하나로 판단하면 안 되고, 검증 점수를 직접 재는
   수밖에 없다**는 걸 확인했다(이번 실험 자체가 그 교훈을 보여주는
   좋은 사례).
3. **신규 피처 3개(`three_ball_zero_outs`, `pitcher_team_win_expectancy`,
   `same_hand_x_offspeed_rate`)는 개별적으로는 실제로 쓰였다.** exp_004
   전체 번들 재학습 결과 각각 importance 0.299 / 0.161 / 1.044로,
   exp_003의 실패작이었던 `three_ball_x_risp`(0.007)보다는 훨씬
   낫다. 다만 전체 조합 수준에서는 원본 컬럼 제거의 손실을 상쇄하지
   못했다.

**결론**: 이번 라운드에서 "제거"와 "추가" 둘 다 순이익을 내지
못했다 — `src/features.py`는 exp_003 상태로 그대로 둔다(코드
diff 없음, 검증만 하고 되돌림). `model/`도 exp_004로 덮어썼던 걸
exp_003 아카이브(`submission/archive/exp003_catboost/model/`)에서
복원했고, `submission/submit.zip`은애초에 exp_004로 재빌드한 적이
없어 계속 exp_003 그대로다(md5 해시로 확인 완료) — **제출물은
변경 없음.**

---

## 다음 가설

1. 이 정도 규모(1~수십 개 피처, 4분 CatBoost 학습)의 변경에서
   ±2~5점 수준 차이는 잡음(run-to-run variance)에 가려질 수 있다 —
   앞으로 이런 "빼기/더하기" 류 실험은 시드를 2~3개 바꿔 평균을
   보거나, 더 확실한 신호(예: 20점 이상 차이)가 날 때만 채택 여부를
   판단하는 게 안전할 수 있다.
2. `pitcher_team_win_expectancy`, `three_ball_zero_outs`처럼 단독으론
   실제로 쓰이는(importance > 0) 신규 피처를, **원본 컬럼 제거 없이
   그냥 추가만** 해보는 실험은 아직 정확히 분리해서 안 해봤다(이번
   "추가만"은 5개를 한꺼번에 넣었음). 여유가 되면 이 3개만 따로
   추가하는 실험을 해볼 수 있으나, 우선순위는 낮다 — 트랙맨 실험이
   훨씬 큰 잠재 이득을 갖고 있으므로 그쪽에 시간을 쓴다.
3. **다음 우선순위는 예정대로 `data/trackman_history.csv` 조인.**
   이번 exp_004 결과(±수 점 단위 미세조정)는 exp_003이 이미 보여준
   "피처엔지니어링만으로는 706→790 수준을 크게 못 벗어난다"는 결론을
   다시 한번 확인해준다.

> 이 문서의 모든 수치는 `experiments/exp004_run_log.txt`와
> `experiments/exp004_ablation_*.txt` 로그에서 그대로 가져왔다 —
> 추정치 없음. exp_003(723.17)은 `experiments/exp003_run_log.txt`
> 기록값을 참고값으로 인용.
