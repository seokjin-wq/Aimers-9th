# exp_009 — CatBoost 하이퍼파라미터 탐색 (exp_008 피처셋 위)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_009
- **날짜 / 담당자**: 2026-08-21 / (Claude, 사용자 요청 — `dacon-score-push-round2`)
- **가설**: exp_003 이후 CatBoost 하이퍼파라미터(depth=6, l2_leaf_reg=3.0,
  learning_rate=0.03)는 exp_006 모델 비교 때 한 번도 별도로 튜닝된 적이
  없다(비교 대상은 baseline 노트북과 맞춘 고정값). 이 데이터셋은 점수
  민감도가 극단적으로 높아서(Brier 0.0006 감소로 점수 +260 상승 수준,
  `dacon-score-push-round2` 메모리 참고) 작은 정칙화/용량 조정만으로도
  눈에 띄는 점수 변화가 있을 수 있다.
- **기준(baseline)**: exp_008(승자 확정 시 그 설정, 아니면 exp_007)의
  CatBoost 기본 파라미터로 이 실행에서 재현한 점수.
- **이번에 바꾸는 것**: `depth`, `l2_leaf_reg`, `learning_rate`,
  `random_strength`, `bagging_temperature`(Bayesian bootstrap),
  `grow_policy=Lossguide`를 각각 baseline 대비 하나씩만 바꾼
  coordinate-wise 그리드(`src/train_exp009_hpo.py`의 `CONFIGS`). 피처
  집합/시드/조기종료는 전부 고정.
- **검증 방법**: season 2019-2023 학습 / 2024 검증(공식 정책 그대로).
- **누수 위험 검토**: 하이퍼파라미터만 바뀌고 피처/데이터 파이프라인은
  exp_008과 완전히 동일 — 신규 누수 위험 없음.

## 결과 (실행 후에 작성)

실행: `src/train_exp009_hpo.py`, 전체 로그 `experiments/exp009_run_log.txt`.

| 설정 | Brier | 공식 local score | Δ vs baseline | best_iter |
|---|---:|---:|---:|---:|
| **baseline(exp_007과 동일, 채택)** | **0.247956** | **740.86** | **0.00** | 695 |
| l2_leaf_reg=8 | 0.247962 | 738.42 | -2.44 | 545 |
| random_strength=5 | 0.247976 | 733.13 | -7.73 | 941 |
| depth=8 | 0.247983 | 729.96 | -10.90 | 365 |
| learning_rate=0.02, iterations=3000 | 0.247990 | 727.37 | -13.49 | 738 |
| l2_leaf_reg=1 | 0.247998 | 724.11 | -16.74 | 473 |
| grow_policy=Lossguide, max_leaves=64 | 0.248029 | 711.70 | -29.16 | 303 |
| depth=4 | 0.248058 | 700.10 | -40.76 | 699 |
| bagging_temperature=2(Bayesian) | 0.248103 | 681.99 | -58.87 | 497 |

**가설 기각 — 9개 설정 전부 baseline보다 낮음.** exp_003 이후 한 번도
바뀌지 않았던 CatBoost 기본값(depth=6, l2_leaf_reg=3.0,
learning_rate=0.03, 나머지 CatBoost 기본값)이 이 피처셋에서는 이미
로컬 최적점에 가깝다는 뜻으로 해석됨. 특히 `bagging_temperature=2`가
가장 크게 나빠졌는데(-58.87), 이는 Bayesian bootstrap을 켜는 것
자체가(baseline은 기본 부트스트랩 방식) 이미 노이즈가 큰 이 데이터셋의
분산을 더 키운 것으로 보임 — exp_010(시드 배깅)이 정반대 방향(분산을
"평균으로 줄이는" 방향)이라 이 결과와 상충하지 않고 오히려 exp_010의
동기를 강화함.

**결론**: CatBoost 하이퍼파라미터는 exp_007/exp_003 값 그대로 유지.
새 챔피언 없음 — 여전히 exp_007(local 740.86 / LB 863.05).

- **다음 가설**: 단일 모델 하이퍼파라미터 공간에서는 개선 여지가 거의
  없어 보이므로, 분산 감소(시드 배깅, exp_010) 또는 새로운 정보원
  (행단위 LUPI 증류, exp_011) 쪽으로 방향 전환.

## 아카이브 (2026-08-21)

baseline은 exp_007과 하이퍼파라미터가 완전히 동일한 모델이라 별도
아카이브 없음(`submission/archive/exp007_trackman_pitcher_asof/`와 100%
중복). "로컬이 낮아도 LB는 다를 수 있으니 남겨두라"는 사용자 정책에
따라, baseline과 가장 근접했던(Δ-2.44) `l2_leaf_reg=8` 설정만 전체
2019-2024로 재학습해 별도 후보로 패키징함
(`src/train_exp009_final.py l2reg8` → `experiments/exp009_final_l2reg8_log.txt`,
검증 재확인 Brier=0.247962/score=738.42로 exp_009 로그와 정확히 일치).
`submission/archive/exp009_l2reg8/`에 격리 프로세스 추론 테스트까지
통과(row_id 순서 일치, 확률 5개 모두 [0,1] 범위, NaN 없음). 나머지
7개 설정(depth=4, bagging_temperature=2 등, 로컬 Δ -7.73~-58.87)은
로컬 손실 폭이 커서 이번엔 아카이브하지 않음 — 필요 시 동일한 방식
(`train_exp009_final.py <config_name>`)으로 언제든 추가 가능.
