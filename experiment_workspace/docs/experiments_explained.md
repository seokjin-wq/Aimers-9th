# 실험 설명

`EXP_001` ~ `EXP_130`이 **무엇을 바꿔 봤는지**를 풀어 쓴 문서다.
문장은 쉽게 쓰되, 모델·파라미터·피처 이름은 원래 표기를 유지한다.
정확한 점수와 TOML은 각 실험의 `decision.md`를 보면 된다.

매번 **한 가지만** 바꾸고, 2019~2023으로 학습한 뒤 2024 holdout으로 채점한다.
좋아지면 남기고, 아니면 되돌린다.

- **채택** (`adopt`): 이번 변경을 다음 실험의 control로 삼는다.
- **유지** (`keep_control`): 이전 설정이 더 낫다.
- **기각** (`reject`): 이번 변경이 없거나 해롭다.
- **보류** (`inconclusive`): 조금 오르지만 본선에 바로 넣지 않는다.
- **규정 위반**: 점수가 좋아도 제출할 수 없다.

---

## 이 대회에서 모델이 하는 일

한 투구마다 `control_success` 확률을 0~1로 예측한다.
Accuracy보다 **Brier** (확률을 얼마나 잘 맞췄는지)가 점수다.

볼 수 있는 것: 투구하기 **전** 상황 (count, 주자, asof 성적 등).
보면 안 되는 것: 현재 투구의 코스·구종, test 다른 행.

---

## 전체 줄거리

```text
1. CatBoost가 잘 맞더라.
2. count, 현재 시즌 성적 같은 피처를 넣으니 올랐다.
3. 성공률이 해마다 떨어져서, 예측 확률을 shift로 조금 낮추니 올랐다.
4. 모델을 여러 개 blend하니 더 올랐다.
5. 직전 N투구 rolling은 test 행을 이어 붙여야 해서 규정 위반. (034~053)
6. 규칙을 지키면서 다시 쌓고, count별 season trend 보정을 더했다. (054~130)
```

---

## 1장. 모델 고르기 (001~007)

### EXP_001 — RandomForest vs CatBoost

같은 raw 피처로 두 모델을 비교했다.
**CatBoost가 훨씬 나아서** 이후 기본 모델이 됐다.

### EXP_002 — 피처 묶음 ablation

쓰던 피처를 달력 / 상태 / context로 나눠 한 묶음씩 제거했다.
빼도 크게 안 좋아져서 **원래 묶음 유지**.
피처를 많이 넣는 게 좋은지 처음 확인한 실험이다.

### EXP_003 — row-local 파생 14개

`count_diff`, same-hand 같이 **한 행 안에서만** 계산한 파생 14개를 넣었다.
점수가 올라서 **채택**. 이후 custom feature의 출발점.

### EXP_004 — native categorical

`top_bottom`, `game_type` 같은 범주를 ordinal encoding 하지 않고
CatBoost native categorical로 넘겼다. **채택**.

### EXP_005 — categorical 범위를 넓히기

선수 ID, team, hand까지 categorical로 넣어 봤다.
기본 3개(`top_bottom`, `game_type`, `base_state`)만 쓰는 편이 나아서 **유지**.

### EXP_006 — depth / iterations

CatBoost `depth`와 `iterations`만 바꿨다. 기본값이 나아서 **유지**.

### EXP_007 — CatBoost vs LightGBM vs XGBoost

같은 피처로 boosting 모델 세 가지를 비교했다. **CatBoost 유지**.

---

## 2장. 상황 피처 (008~023)

### EXP_008 — EDA 제안 피처를 묶음으로

결측, smoothing, context, **count**를 각각 추가했다.
**count 묶음만 채택** (full count, 3-ball 등).

### EXP_009 — smoothing × 결측 조합

008에서 떨어진 묶음을 pairwise로 넣어 봤다. count만 있는 편이 나아서 **유지**.

### EXP_010 — 직전 시즌 target history

직전 시즌 투수·타자 성공률 피처를 추가했다.
이미 있는 asof 누적과 겹쳐서인지 **유지**.

### EXP_011 — season sample weight decay

2019 행은 약하게, 2023 행은 세게 (`decay` 1.0~0.25).
이 단계 피처에서는 **uniform이 더 나아서 유지**.
(피처가 바뀐 뒤 EXP_060에서 다시 해서, 그때는 decay 0.85가 채택)

### EXP_012 — CatBoost regularization

`l2_leaf_reg`, `random_strength`, `rsm`, `subsample`, `border_count`를 하나씩. **유지**.

### EXP_013 — Logloss vs squared-error

분류 Logloss와 회귀 squared-error를 비교했다. **Logloss 유지**.

### EXP_014 — 파생 피처 pruning

중요도 낮은 custom / count 중복을 묶음으로 제거. 안 빼는 편이 나아서 **유지**.

### EXP_015 — prediction shift

시즌이 갈수록 성공률이 떨어지는데 모델은 확률을 높게 부르는 경향이 있다.
예측에서 0.005~0.015를 빼 봤다. **shift −0.010 채택**.

### EXP_016 — seed ensemble

seed만 다른 CatBoost 3개·5개의 확률을 평균. 단일 seed와 비슷해서 **유지**.

### EXP_017 — count 피처를 하나씩

`count_state`, full count, 2-strike, 3-ball, 2-out을 따로 추가.
**count 관련 numeric을 모두 넣는 것이 채택**.

### EXP_018 — depth 4~6, iterations 100~400

더 작은 capacity를 세밀히 비교. 기존이 나아서 **유지**.

### EXP_019 — ID를 categorical로

pitcher / batter / team / hand를 하나씩만 native categorical로 추가.
**batter team만 채택**. 선수 개인 ID는 별로였다 (고유값이 많고, 2025 신인은 학습에 없음).

### EXP_020 — affine (scale / shift)

예측에 `scale`과 `shift`를 미세 조정. **채택**.

### EXP_021 — 시즌 내 pitch index

`row_id`로 올해 몇 번째 투구인지 만들었다. **유지**.
test 행 순서를 쓰면 규칙에 걸릴 수 있는 영역이기도 하다.

### EXP_022 — bootstrap / grow_policy

`bootstrap_type`, `boosting_type`, `grow_policy` 등. **유지**.

### EXP_023 — logistic, HistGradientBoosting, ExtraTrees 단독

CatBoost가 아닌 모델만으로 같은 피처를 학습.
여전히 **CatBoost가 나아서 유지.** ExtraTrees는 나중에 blend 재료로 쓴다.

---

## 3장. blend, GPU, 보정 (024~033)

### EXP_024 — CatBoost + ExtraTrees blend

두 모델 확률을 가중합. ExtraTrees 비중 15~35%.
**24% 채택.** 이종 앙상블의 시작.

### EXP_025 — learning_rate × iterations

천천히 많이 vs 빨리 적게. **채택** (소폭).

### EXP_026 — 직전 시즌 group residual

2019~2022로 학습해 2023을 맞춘 뒤, count별 잔차를 저장하고
2024 예측에 더한다. **count k500 채택.**
시즌 drift를 상황(balls/strikes)별로 맞추려 한 실험.

### EXP_027 — GPU CatBoost

GPU에서 `depth`·`iterations`·`learning_rate`를 비교. **채택.**
나중에 CPU 모델과 blend하는 재료가 된다.

### EXP_028 — EDA 파생을 하나씩

결측, smoothing, log, context 교차 12개를 **하나씩** 추가.
`scoring_position × li`만 이겼다. **채택**.

### EXP_029 — 이긴 피처 조합

028에서 괜찮았던 4개를 2-way / 전부. 조금 오르지만 **보류**.

### EXP_030 — 그 조합을 CPU에서 재검증

GPU에서 이긴 피처가 CPU에서도 되는지. **안 되어서 유지**.
한 환경에서만 좋은 피처를 걸러 낸 실험.

### EXP_031 — GPU CatBoost seed ensemble

3-seed 평균이 이겼다. **채택.** 나중에 triple blend로 대체된다.

### EXP_032 — 상황별로 모델을 쪼개 학습

`game_type`, `top_bottom`, `pitcher_hand`로 데이터를 나눠 각각 학습.
global 한 모델이 나아서 **유지**. 쪼개면 표본이 줄어든다.

### EXP_033 — 2023 예측으로 calibration

mean-shift, affine, Platt, beta, isotonic을 비교.
안 하는 편이 나아서 **유지**. (비슷한 보정은 나중에 count residual로 다시)

---

## 4장. 규정 위반 (034~053)

이 구간은 점수가 좋아도 제출 불가라 `experiments/rule_invalid/`에 격리했다.

공통: 투수/타자의 **직전 투구**를 train·val의 **다른 행을 이어 붙여** 계산했다.

규칙: 평가(2025)의 각 행은 **그 행만** 보고 예측해야 한다.
옆 행을 보면 직전 5구 성공률 같은 rolling을 만들 수 있지만, 그건 다른 test 행을 보는 것이다.

비유: 시험 3번을 풀 때 2번 답을 보면 안 된다.

### EXP_034

asof 누적 차분으로 직전·최근 3·5·10투구 성공을 복원.

### EXP_035

rolling window. 투수 recent 20~50, 타자 recent 2~8.

### EXP_036

투수 reverse의 최근 rolling.

### EXP_037

middle·ball rolling도 같은 방식.

### EXP_038

직전 투구와의 간격, 같은 PA 여부, PA 내 pitch number.
이것도 행과 행을 이어야 한다.

### EXP_039 ~ 041

위 sequential 피처를 넣은 채 CatBoost capacity, ExtraTrees, `random_strength` 등.
피처가 반칙이면 이 튜닝도 제출 불가.

### EXP_042

lag 2·3·5와 최근 3구 성공/실패 패턴.

### EXP_043 ~ 046

같은 sequential 피처를 CPU에서 재현, window 정리, EWMA, 다른 boosting.

### EXP_047 ~ 049

투수 단위가 아니라 **리그 전체** 최근 투구 평균 (global rolling).
window 75~400.
“오늘 리그 제구가 어떤 날인지”를 보려 한 것이지만, 역시 다른 행을 본다.

### EXP_050 ~ 051

그 global 피처 위에서 capacity, global reverse rolling.

### EXP_052

최고 예측을 저장해 affine 보정 가능 범위를 진단.

### EXP_053

경기·팀별 recent 200 성공률. 역시 행을 모아야 한다.

**합법인 비슷한 정보**: 주최가 행마다 넣어 준
`asof_pitcher_prev1/3/5_game_success_rate`.
옆 행을 안 봐도 된다. 다만 직전 5**구**가 아니라 직전 5**경기**다.

---

## 5장. 규칙 준수로 다시 (054~070)

034~053을 버린 뒤, **024 blend**부터 다시 쌓는다.

### EXP_054 — 024를 규칙 준수 엔진에서 재현

같은 설정을 규칙 검사하는 코드로 다시 실행. **유지.**
이후 피처는 row-local인지 더 엄격히 본다.

### EXP_055 — official-train-only target encoding

투수·타자·team의 과거 성공률을 공식 train만으로 만들어 붙였다.
val 행은 안 썼지만 점수가 안 올라 **기각**.

### EXP_056 — 현재 시즌 누적 상태 (가장 큰 피처 이득)

커리어 전체가 아니라 **이번 시즌 asof 성적**.
한 행의 season·ID와 train label만 쓰면 되므로 합법.
점수가 크게 올라 **채택**. 이후 핵심 피처.

왜 먹혔나: 제구 성공률이 해마다 떨어지므로, 2019 커리어보다
**현재 시즌 숫자**가 2024와 더 가깝다.

### EXP_057 — 056 피처에서 ExtraTrees blend 다시

CatBoost 단독 vs ExtraTrees 15~32%. **24% 채택.**

### EXP_058 — 시즌 − 커리어, 시즌 − 최근 폼 delta

차이를 별도 피처로. 원본 두 컬럼을 이미 보고 있어서인지 **유지**.

### EXP_059 — depth / iterations 다시

**depth 8, iterations 300 채택.**

### EXP_060 — season decay 재검증

011에서 실패했던 sample weight decay.
현재 시즌 피처가 생긴 뒤에는 **decay 0.85 채택.**

### EXP_061 — 시즌 rate shrinkage k

표본이 적을 때 prior로 당기는 강도. **유지.**

### EXP_062 — depth8 decay0.85 + ExtraTrees

Extra 18~30%. **18% 채택.**

### EXP_063 — 빼 둔 pitchmix / raw 컬럼 복구

조금 오르지만 **보류**.

### EXP_064 — count × hand, count × base 같은 교차 target 효과

상황별 성공률 통계를 train으로 만들어 붙였다. **기각.**
트리가 원본 피처로 이미 split 하고 있을 가능성이 크다.

### EXP_065 — 같은 교차를 leave-one-season-out으로

한 시즌을 통째로 빼고 통계를 다시 계산. 그래도 **유지**.

### EXP_066 — CatBoost vs HistGB vs LightGBM vs XGBoost

**CatBoost 유지**.

### EXP_067 — 2023 residual을 또 다른 CatBoost로

잔차 모델. **기각.** 2024에 안 맞을 수 있다.

### EXP_068 — Trackman 시즌 통계

pitcher ID가 안 맞아서 season·hand 같은 **그룹 평균**만 붙였다.
조금 오르지만 **보류**. 106에서 velocity만 다시 본다.

### EXP_069 — GPU 큰 CatBoost vs CPU depth8

**CPU 유지**. GPU는 “다른 오차”를 내는 재료로 070에서 쓴다.

### EXP_070 — CPU + GPU + ExtraTrees (현재 뼈대)

세 모델 blend 비중을 비교. **45 / 40 / 15 채택.**
이후 triple ensemble이라고 부르는 것의 시작.

---

## 6장. categorical, same-hand, calibration (071~104)

### EXP_071 — 선수 ID categorical 다시

triple 위에서도 개인 ID는 별로여서 **유지** (batter team만).

### EXP_072 — 커리어 상태 피처를 빼 보기

현재 시즌이 있으니 커리어를 빼도 되지 않을까.
**빼지 않는 편이 나아서 유지.** 둘 다 있으면 트리가 비교할 수 있다.

### EXP_073 — 현재 시즌 성공률 shrinkage k

표본 적은 선수를 prior 쪽으로 당기는 강도. **k=50 채택.**

### EXP_074 — Trackman pitcher linkage

공식 ID namespace가 달라서 연결을 시도. 안정적으로 못 붙여 **유지**.

### EXP_075 — 투수 k vs 타자 k

073을 투수·타자 따로. **둘 다 k=50 채택.**

### EXP_076 — 시즌 성공/실패 count

rate 말고 횟수 피처. **유지.**
이미 `n`과 rate가 있으면 count는 곱으로 나와 중복에 가깝다.

### EXP_077 — Logloss vs RMSE

Brier에 가까운 목표로 바꿔 봤다. **Logloss 유지**.

### EXP_078 — count와 hand를 categorical로

숫자 대신 `count_state`, pitcher/batter hand를 native categorical로.
**count + both hands 채택.** CPU에서 먼저 이김.

### EXP_079 — 그 categorical 조합

한 손만, same-hand만, 합성. 078 그대로가 나아서 **유지**.

### EXP_080 — 078을 triple에 promotion

CPU에서 이긴 categorical을 triple에도. **채택.**

### EXP_081 — count × hand × out 합성 categorical

따로 두는 078이 나아서 **유지**.

### EXP_082 — calendar / inning 등 categorical을 하나씩

078 옆에 하나만 더. 더하지 않는 편이 나아서 **유지**.

### EXP_083 — 직전 경기 weighted blend

prev1에 더 큰 가중을 준 한 피처로 압축.
트리가 prev1 / prev3를 **따로** 보는 편이 나아서 **기각**.

### EXP_084 — same-hand × pitchmix

같은 손일 때 fastball / breaking / offspeed 비율.
한 행의 hand와 asof pitchmix만 곱하면 되므로 합법. **채택.**

### EXP_085 — history missing flag

직전 경기 rate가 비어 있는지를 피처로. **기각.**
이미 `n=0` 등으로 보일 수 있다.

### EXP_086 — 현재 시즌 성적을 train label 스냅샷으로

근사 계산 대신 official train label로 더 정확히.
타자 쪽만 이득이 있어 **채택**.

### EXP_087 — 084를 triple에

same-hand × pitchmix를 triple에도. **채택.**
CPU에서 이긴 피처가 ensemble에서도 이겼다. (028·030과 반대)

### EXP_088 — count group residual을 triple에

026과 비슷한 보정을 triple에. group을 hand·team 등으로도 바꿔 봄.
**count, shrinkage 500 채택.**

### EXP_089 — row_id로 season progress (합법 쪽)

진행도를 만들고, val 시작점은 train 마지막을 참고.
그래도 **기각**.

### EXP_090 — late inning × 투수 history

7회 이후 × 투수 최근 성적. **채택.**

### EXP_091 — 090을 triple에

조금 오르지만 **보류**. ensemble이 이미 비슷하게 흡수했을 수 있다.

### EXP_092 — full count × 투수 history

불리한 count에서 원래 제구가 좋은 투수인지. **채택.**

### EXP_093 — late inning vs full count 교차

둘을 따로 / 같이. **late inning × 투수 history가 더 낫다.**

### EXP_094 — 088 재현

같은 설정을 처음부터 다시. **재현되어 채택.**

### EXP_095 — same-hand × pitchmix 3개를 하나씩

fastball / breaking / offspeed. **세 개 다 있는 편이 채택.**

### EXP_096 — late-inning 교차를 하나씩

success / reverse / middle. **세 개 다 채택.**

### EXP_097 — late-inning 교차만 triple에 다시

넣지 않은 triple이 나아서 **유지**. CPU에서 이긴 피처가 ensemble에선 중복.

### EXP_098 — 최신 피처에서 depth / iterations

depth 5~8. **depth 8, iterations 300 유지.**

### EXP_099 — season decay 0.80~0.90

060의 0.85 근처만 다시. **0.85 유지.**

### EXP_100 — affine 미세 조정

shift를 조금 더 내리는 쪽이 **채택**.

### EXP_101 — triple 안에서 CatBoost 성분만 shift

**−0.0095 채택.**

### EXP_102 — blend 비중 다시

45/40/15 근처. **50 / 35 / 15 채택** (CPU를 조금 더).

### EXP_103 — residual_scale 0.5~2.0

count 보정을 얼마나 세게 더할지. **1.0 유지.**

### EXP_104 — residual group을 count 말고 다른 것으로

hand, inning, `base_state`. **count가 나아서 유지.**

---

## 7장. 마지막 피처와 현재 최고점 (105~130)

### EXP_105 — official-train context target 효과 4개

064와 비슷한 계열을 최신 CPU에. **유지.**

### EXP_106 — Trackman physics 분해

068을 velocity / movement / extension으로 쪼갬.
**velocity (rel_speed, zone_speed)만 채택.** spin·break는 별로.

### EXP_107 — 그 velocity를 triple에

CPU에서 이긴 Trackman velocity가 triple에서는 안 먹혀 **유지**.

### EXP_108 — 빼 둔 raw 컬럼을 하나씩 복구

`run_total_before`, `score_diff_home`, pitchmix_n 등. **유지**.

### EXP_109 — regularization을 하나만

`l2_leaf_reg`, `random_strength`, **`subsample`**, `rsm`.
**subsample 0.8 채택.**

### EXP_110 — subsample 0.75~0.90

**0.8 유지.**

### EXP_111 — subsample 0.8을 triple의 CPU에

**채택.**

### EXP_112 — history reliability

투구 3개의 100%와 투구 2000개의 55%는 의미가 다르다.
표본 수를 0~1 reliability로 바꾸고 rate에 곱했다.
**numeric reliability 6개 채택.** (크기 bucket categorical은 별로)
단일 CatBoost 기준 최고점에 가까운 피처 실험.

### EXP_113 — reliability 6개를 2개씩 제거

다 있는 편이 나아서 **유지**.

### EXP_114 — reliability 분모 k

k=50/100/200. **k=100 유지.**

### EXP_115 — reliability + late inning / full count history

112 위에 090·092를 다시. **더하지 않는 편이 나아서 유지.**

### EXP_116 — reliability를 triple에

078처럼 CPU에서 이긴 112를 ensemble에도. **채택.**

### EXP_117 — triple blend 비중 다시

**50 / 35 / 15 채택.**

### EXP_118 — reliability 피처에서 capacity 다시

**depth 8, iterations 300 유지.**

### EXP_119 — CatBoost 성분 shift 다시

**−0.0095 유지.**

### EXP_120 — categorical processing

`max_ctr_complexity`, `one_hot_max_size`. **기본값 유지.**

### EXP_121 — HistGB를 네 번째 모델로

ExtraTrees 자리를 2.5~5%만 HistGB로. **안 넣는 편이 나아서 유지.**

### EXP_122 — ball/strike·pitchmix에도 reliability

112를 다른 rate까지 확장. **유지**. 6개면 충분.

### EXP_123 — monotonic constraint

성공률이 높으면 예측도 높아지게 강제. 제약 없는 편이 나아서 **유지**.

### EXP_124 — ExtraTrees season decay (100 trees 스크리닝)

**decay 0.85가 좋아 보여 채택** (다음에서 본 확인).

### EXP_125 — ExtraTrees 300 trees에서 같은 decay

실제 ensemble 크기에서는 **uniform이 더 나아서 기각.**
작은 모델에서 이긴 설정이 큰 모델에서 실패하는 예.

### EXP_126 — 2023 OOT로 blend 비중을 학습

simplex 최적은 GPU-only가 나왔다.
2024에 적용하면 나빠져 **수동 50/35/15 유지.**
한 해에 맞춘 비중이 다음 해에 안 먹힌다.

### EXP_127 — count별 season trend

026·088이 “작년 residual만큼 밀기”라면,
127은 2019~2023 count별 성공률이 내려가는 **기울기**를 본다.
그 trend만큼 2024를 더 보정. **strength 1.0 채택.**
현재 최고점을 만든 축에 가깝다.

### EXP_128 — `trend_strength` 0.75~1.50

**1.0 유지.**

### EXP_129 — trend shrinkage

count 조합은 12개라 표본이 넉넉하다.
shrinkage 0이 미세하게 이겼다. **채택.**

### EXP_130 — trend 추정 방법

WLS (투구 수 가중) vs OLS (시즌 동등) vs 2019~2023 endpoint.
**OLS 채택.** 현재 제출 후보의 끝.

---

## 현재 모델이 하는 일

1. 상황 피처 + 현재 시즌 상태 + count/hand categorical + same-hand × pitchmix + reliability
2. CPU CatBoost + GPU CatBoost + ExtraTrees를 50:35:15로 blend
3. 학습 때 season decay 0.85
4. 예측에 affine shift
5. count별 season trend로 한 번 더 보정

test 행을 이어 붙인 rolling은 쓰지 않는다.

---

## 이 문서를 볼 때

- 점수가 왜 올랐는지 → **채택**된 실험만 읽으면 된다.
- 이런 거 안 해 봤는지 → 유지·기각에 비슷한 게 있는지 본다.
- rolling이 무엇인지 → 4장. 다른 행을 이어 최근 N개의 평균을 내는 것.

자세한 숫자와 설정은

`experiments/EXP_NNN/decision.md`  
`experiments/EXP_NNN/runs/RUN_001/report.md`
를 보면 된다.
