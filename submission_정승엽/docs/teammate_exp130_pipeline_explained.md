# 허찬 EXP_130 파이프라인 총정리 (팀원 저장소 재현본)

`experiment_workspace/experiments/EXP_130` — 허찬(`github.com/seokjin-wq/Aimers-9th`,
로컬 경로 `/home/chanheo/lgaimers/`)의 130개 실험 중 최종 채택
버전(`triple_count_trend_ols`)입니다. 원 저장소 기록상 로컬 검증(2019-2023
학습/2024 홀드아웃) **945.44**, 실제 LB **~1045**로 추정됩니다.

**실제로 제출까지 완료했습니다**: `submission/archive/teammate_exp130_cpu_repro/submit.zip`
(725MB, 팀원 자체 격리검증 통과) — 2026-08-22 16:53:42 제출,
**LB 1043.6552481052**. 원래 추정치("~1045")와 -1.34 차이로 거의
일치해, GPU→CPU 대체가 결과에 준 영향은 미미했음이 확인됐습니다.
우리 자체 챔피언(exp_030, LB 1006.62)보다 **+37.03 높음** — 원인
분석은 `docs/teammate_score_gap_analysis.md` 참고. 기본
`submission/submit.zip`은 그대로 exp_030을 가리키는 채로 유지 중입니다.

---

## 0. 재현본이라는 것의 의미 — 원본과 다른 점

이 머신에 GPU가 없어서, 원본의 GPU CatBoost 성분(`task_type="GPU"`)만
**동일 하이퍼파라미터로 CPU 모드로 대체**해서 다시 학습했습니다. 그 외
피처(78개)·CPU CatBoost·ExtraTrees·보정 로직은 전부 원본과 100% 동일한
설정입니다. 따라서:

- 이 재현본이 원본과 **정확히 같은 945.44**를 낼지는 미확인(GPU↔CPU
  학습 결과가 완전히 같지 않을 수 있음).
- 팀원 자체 검증 도구(`run.py validate-package`)로 row-independence
  체크(단일행/셔플/행추가 등)는 전부 통과 — 대회 규정 위반은 없음.
- 우리 프로젝트 표준 격리 테스트(임시 폴더에서 새 프로세스 실행)는
  아직 별도로 안 함.

---

## 1. 전체 파이프라인 흐름

```
공식 train.csv (2019-2024, season decay 가중치 적용)
      │
      ▼
① 피처 엔지니어링 — 78개 (main78_history_reliability)
      │
      ▼
② 3개 모델을 각각 학습
      ├─ CPU CatBoost  (weight 0.50)
      ├─ GPU CatBoost  (weight 0.35)  ← 이 재현본은 CPU로 대체
      └─ ExtraTrees    (weight 0.15)
      │
      ▼
③ 가중 평균 blend (0.50 / 0.35 / 0.15) + 성분별 affine 보정
      │
      ▼
④ 1차 보정 — count-state별 OOT 잔차 보정 (group_shrinkage=500)
      │
      ▼
⑤ 2차 보정 — count-state별 season 추세 보정 (OLS, strength=1.0)
      │
      ▼
최종 확률 (0~1 clip)
```

우리 exp_030과 뼈대(이번시즌 상태 피처 + count-state 보정)는 같은
계열이지만, **모델을 3종 이종 앙상블로 섞고**, **학습 자체에 시즌
recency 가중치를 준다**는 점이 가장 큰 구조적 차이입니다(8번 비교표
참고).

---

## 2. 피처 — 78개 (`main78_history_reliability`)

**구성 방식**: 공식 원본 컬럼을 전부 포함(`include_all_raw = true`)한
뒤 6개만 제외하고, 자체 파생 32개를 더합니다.

### 2-1. 제외한 원본 컬럼 6개

```
run_total_before, score_diff_home, asof_pitcher_pitchmix_n,
asof_pitcher_strike_rate, asof_pitcher_fastball_rate,
asof_pitcher_prev5_game_success_rate
```
자체 실험(팀원 EXP_002/105류)에서 중요도가 낮거나 다른 피처와
중복돼 빼는 게 오히려 나았던 컬럼들입니다.

### 2-2. 파생 피처 32개 — 야구적 해석

| 피처(그룹) | 야구적 해석 |
|---|---|
| `pitcher_season_n`, `pitcher_season_{success,reverse,middle,ball,strike}_rate_k20`, `batter_season_n`, `batter_season_{success,middle}_rate_k20` | **이번 시즌만의** 상태 — 우리 exp_027과 동일한 발상(커리어 누적이 아니라 최근 폼) |
| `pitcher_gap_prev1_career`, `_prev3_career`, `_prev5_career` | 최근 N경기 성적과 커리어 평균의 "격차" — 지금 폼이 평소보다 좋은지/나쁜지 직접 수치화 |
| `same_hand_matchup`, `same_hand_x_{fastball,breaking,offspeed}` | platoon(좌우 매치업) 신호 — 우리도 동일한 3구종 버전을 씀(exp_028에서 이식) |
| `pressure_x_recent_form`, `late_inning_x_recent_form` | 압박 상황/후반 이닝일수록 최근 폼이 성공률에 미치는 영향이 달라짐 |
| `runners_x_li`, `reverse_rate_x_li`, `offspeed_x_li` | 레버리지 인덱스(`li`, 그 상황이 승패에 미치는 중요도)와 주자 상황/투구 성향의 상호작용 |
| `win_expectancy_dist50` | 승리 기대확률이 50%(박빙)에서 얼마나 떨어져 있는지 — 경기 긴장도 대리 지표 |
| `count_diff`, `count_total`, `count_state`, `is_full_count`, `has_two_strikes`, `has_three_balls`, `has_two_outs` | 카운트/아웃 상황 — 우리 프로젝트와 거의 동일한 발상 |
| `middle_rate_x_count_diff` | 투수의 "가운데로 몰리는 습관"이 카운트 유불리에 따라 어떻게 변하는지 |
| `batter_success_rate_shrunk` | 콜드스타트 보정된 타자 성공률(우리 `SHRINKAGE_SPECS`와 동일한 발상) |
| `pitcher_history_reliability_k100`, `batter_history_reliability_k100`, `{pitcher,batter}_success_x_reliability`, `pitcher_{reverse,middle}_x_reliability` | 표본 신뢰도(`n/(n+100)`) — 우리도 exp_028에서 이식했지만 우리 쪽에선 노이즈 수준이라 기각, 이 파이프라인에선 채택된 6개 |

### 2-3. 범주형 처리 7개

`top_bottom`, `game_type`, `base_state`(공식 3개) + `batter_team_id`,
`count_state`, `pitcher_hand`, `batter_hand` — CatBoost native
categorical로 직접 넘김(원-핫/순서 인코딩 없이). 우리는 baseline대로
`OrdinalEncoder` 계열을 쓰는데, 이쪽은 CatBoost가 범주형을 직접
처리하게 맡기는 방식입니다.

---

## 3. 모델 — CPU CatBoost + GPU CatBoost + ExtraTrees, 50:35:15

가장 큰 구조적 차이입니다. 우리(exp_030)는 **같은 CatBoost를 시드만
바꿔 2개** 평균 내는 반면, 이쪽은 **아예 다른 편향을 가진 모델 3개**를
섞습니다.

| 성분 | 가중치 | 주요 하이퍼파라미터 |
|---|---|---|
| CPU CatBoost | **0.50** | `iterations=300, depth=8, learning_rate=0.035, l2_leaf_reg=3.0, subsample=0.8` |
| GPU CatBoost (이 재현본은 CPU로 대체) | **0.35** | `iterations=600, depth=7, learning_rate=0.025, bootstrap_type=Bayesian, bagging_temperature=1.0, border_count=128` — CPU보다 얕고 느린 학습률로 더 많이 도는 설정, GPU라 원래는 훨씬 빠르게 도는 걸 전제로 함 |
| ExtraTrees | **0.15** | `n_estimators=300, min_samples_leaf=20, max_features=0.7` |

**왜 두 CatBoost를 다르게 튜닝했나**: 같은 알고리즘이라도
depth/learning_rate가 다르면 서로 다른 국소 최적점에 수렴해 오차가
어느 정도 다른 방향으로 남습니다 — 진짜 다른 모델(ExtraTrees)만큼은
아니지만 시드만 바꾸는 것보다는 더 큰 다양성을 노린 설계로 보입니다.

**블렌딩 후 추가 보정(affine)**: `cat_scale=1.06, cat_shift=-0.0095,
extra_shift=-0.01` — CatBoost 블렌드 성분에는 살짝 확대(scale>1)한
뒤 아래로 이동, ExtraTrees 성분에는 그냥 아래로 이동. 각 성분이
평균적으로 살짝 과신하는 경향을 미세 조정하는 단계(팀원 EXP_020/100/101/119).

**학습 시 시즌 가중치(`season_decay=0.85`)**: 우리는 학습 후
사후보정(Platt)만 하는데, 이 파이프라인은 **학습 자체에서** 오래된
시즌(2019) 행에 낮은 가중치, 최근 시즌에 지수적으로 높은 가중치를
줍니다. 감쇠율 0.85 → 한 시즌 전 데이터는 가중치가 0.85배, 5시즌
전이면 0.85⁵≈0.44배로 줄어듭니다. **"모델이 처음부터 최근 패턴을 더
중요하게 보도록" 만드는 것** — 우리의 사후보정 방식과는 완전히 다른
접근으로 시즌 드리프트를 다룹니다.

---

## 4. 보정 — 2단계, 둘 다 count-state(볼-스트라이크) 기준

### 4-1. 1차: count-state별 OOT(out-of-time) 잔차 보정

```
잔차 = 실제 라벨 − 모델의 out-of-time 예측
잔차_중앙화 = 잔차 − 전체 평균 잔차   (전역 성분 제거)
offset[count_state] = Σ잔차_중앙화 / (그룹표본수 + 500)   ← group_shrinkage=500
최종확률 += offset[이 행의 count_state]
```

각 count-state(예: "2볼-1스트라이크")마다 "모델이 평균적으로 실제보다
얼마나 더 높게/낮게 예측했는가"를 구해서 그만큼 되돌려주는 보정입니다.
`group_shrinkage=500`이 커서, 표본이 아주 많은 그룹만 유의미하게
보정되고 작은 그룹은 보정폭이 약하게 억제됩니다.

### 4-2. 2차: count-state별 시즌 추세 보정

이건 지난 대화에서 이미 자세히 설명한 것과 완전히 동일한 로직입니다
(`docs/current_best_pipeline.md` §5-2 참고) — 라벨을 시즌평균으로
중앙화한 뒤 count-state별 OLS 기울기를 구해 다음 시즌으로 외삽.
`trend_strength=1.0, trend_shrinkage=0.0`(count-state가 12개뿐이라
표본이 이미 충분해서 축소 없음), `trend_method="ols"`.

**중요한 차이점**: 이 두 보정 모두 **count-state "간의" 상대적 차이만
만들 뿐 전역 상수로 전체를 미는 단계가 없습니다** — 우리가 exp_023/026에서
실패했던 "전역 외삽 shift"에 해당하는 단계 자체가 이 파이프라인에는
아예 없습니다. `calibration_shift=0.0`이 이걸 명시적으로 확인해줍니다.

---

## 5. 야구적 해석 — 실제 feature importance 기준

재현 빌드의 `feature_importance.csv` 상위 항목:

| 순위 | 피처 | importance | 해석 |
|---|---|---|---|
| 1 | `game_type` | 12.37% | 정규시즌/포스트시즌 등 경기 성격 자체가 가장 강한 단일 신호 |
| 2 | `pitcher_season_success_rate_k20` | 9.90% | **이번 시즌 상태 피처가 압도적 2위** — 우리 exp_027이 최대 개선이었던 것과 정확히 같은 결론 |
| 3 | `season` | 8.37% | 시즌 자체(연도)를 원본 피처로 직접 줌 — 모델이 트리 분할로 시즌별 드리프트 일부를 스스로 학습할 기회 |
| 4 | `batter_season_success_rate_k20` | 3.72% | 타자 쪽 이번 시즌 상태도 상당한 기여 |
| 5 | `batter_team_id` | 2.95% | 타자 소속팀(구장 특성, 팀 컬러) |
| 6 | `pitcher_season_reverse_rate_k20` | 2.57% | 이번 시즌 "반대 방향 투구" 경향 |
| 7 | `same_hand_x_fastball` | 2.31% | 손 매치업×패스트볼 비율 상호작용 |

**핵심 결론**: importance 1~7위 중 3개(`pitcher_season_success_rate_k20`,
`season`, `batter_season_success_rate_k20`)가 전부 "이번 시즌/연도"
관련 신호입니다 — **우리 exp_027이 발견한 것과 동일하게, 이 대회에서
가장 강력한 단일 신호는 "이 선수가 커리어 통틀어 어땠는가"가 아니라
"올해 어땠는가"**라는 게 서로 독립적으로 만든 두 파이프라인에서
동일하게 확인됩니다.

---

## 6. 우리 챔피언(exp_030)과의 비교

| 항목 | 우리 exp_030 | 허찬 EXP_130 |
|---|---|---|
| 피처 수 | 105 | 78 |
| 모델 | CatBoost 단일 아키텍처, 2시드 평균 | CatBoost(CPU) + CatBoost(GPU) + ExtraTrees, 3종 이종 앙상블 |
| 학습 시 시즌 가중치 | 없음(균등) | `season_decay=0.85` 지수 감쇠 |
| 시즌 상태 피처 | ✅ (exp_027, +77.93 최대 개선) | ✅ (동일 발상, importance 최상위권) |
| count-state 보정 | ✅ 추세 보정 1단계만(exp_029) | ✅ **잔차 보정 + 추세 보정 2단계** |
| 전역 시즌 보정 | Platt scaling(2024 가중) | 없음(count-state 보정만) |
| 전역 상수 외삽 | ❌ 제거함(exp_023/026 실패 교훈) | 애초에 없음 |
| 트랙맨 물리 특성 | ✅ (exp_007, 5개) | ❌ 없음(원 저장소는 ID 매핑을 못 풀어 포기, EXP_074/068) |
| 로컬 검증 | ~828 | 945.44 |
| LB | **1006.62(확인됨)** | ~1045(추정, 미확인) |

두 파이프라인이 "이번 시즌 상태"와 "count-state 국소 보정"이라는
핵심 축에서는 독립적으로 같은 결론에 도달했다는 게 가장 흥미로운
지점이고, 남은 격차는 주로 **① 이종 앙상블, ② 학습 시 시즌 가중치**
두 가지로 설명될 가능성이 높습니다(`docs/current_best_pipeline.md`
§8 "아직 안 써본 것"과 동일한 결론).

---

## 7. 현재 상태

- 빌드: `submission/archive/teammate_exp130_cpu_repro/submit.zip`
  (725MB, 팀원 자체 검증 통과)
- **제출 완료** — 2026-08-22 16:53:42, **LB 1043.6552481052**
  (`experiments/SUBMISSION_LOG.md`에 기록됨)
- 기본 `submission/submit.zip`은 여전히 exp_030(우리 자체 챔피언,
  1006.62)을 가리킵니다 — 이 EXP_130 재현본이 실제로 더 높게
  나왔지만(+37.03), 원인이 아직 완전히 분리 검증되지 않은 "남의
  파이프라인 그대로"이므로 기본값을 바꾸지는 않았습니다. 격차 원인
  분석과 다음 단계는 `docs/teammate_score_gap_analysis.md` 참고.

---

## 참고 원본

- `_teammate_repo/experiment_workspace/experiments/EXP_130/` — 원본 실험 기록
- `_teammate_repo/experiment_workspace/experiments/BASELINE_001_main55/final.toml` — 최종 레시피
- `_teammate_repo/experiment_workspace/docs/experiments_explained.md` — 130개 실험 전체 서사
- `submission/archive/teammate_exp130_cpu_repro/{README.md,build_metadata.json,feature_importance.csv}` — 이 재현본의 정확한 설정/검증 기록
- `docs/current_best_pipeline.md` — 우리 자체 챔피언(exp_030) 상세
