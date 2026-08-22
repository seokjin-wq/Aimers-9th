# exp_017 — LightGBM 하이퍼파라미터 개선 후 CatBoost 블렌드 재시도

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_017
- **날짜 / 담당자**: 2026-08-21 / (Claude, 사용자 요청 — `dacon-score-push-round2`, 목표 로컬 1000/LB 1100)
- **가설**: exp_013에서 LightGBM은 기본 하이퍼파라미터로만 학습해
  CatBoost보다 48점이나 약했고, 그래서 블렌딩 이득도 +2.02에 그쳤다.
  LightGBM은 이 환경에서 CatBoost(~200s)보다 훨씬 빠르게(~15-30s)
  학습되므로, 저비용으로 5종 설정(leaves/lr/regularization)을 시도해
  더 강한 LightGBM을 찾으면 블렌드 이득이 exp_013보다 커질 수 있는지
  확인한다.
- **기준(baseline)**: exp_013의 CatBoost+LightGBM(기본) 블렌드
  (+2.02), exp_010 챔피언(749.58).
- **이번에 바꾸는 것**: LightGBM `num_leaves`/`learning_rate`/
  `min_child_samples`/`subsample`/`colsample_bytree`/`reg_lambda` 5종
  조합 비교 후 최선을 CatBoost와 블렌드.
- **검증 방법**: season 2019-2023 학습 / 2024 검증 (공식 정책 그대로).
- **누수 위험 검토**: 하이퍼파라미터만 바뀜 — 신규 누수 위험 없음.

## 결과 (실행 후에 작성)

실행: `src/train_exp017_lgbm_tuned_blend.py` (전체 로그
`experiments/exp017_run_log.txt`, 1차 실행은 세션 종료로 유실되어
2차 실행에서 완주).

| LightGBM 설정 | score |
| --- | --- |
| baseline(exp_013과 동일) | 694.97 |
| deeper_leaves(255) | 632.75 |
| slow_lr(0.01) | **705.38**(최선) |
| strong_reg | 684.50 |
| deep_slow | 653.63 |

CatBoost 단독: 740.86. **CatBoost+최선 LightGBM(slow_lr) 블렌드**:
가중치 cb=0.76/lgb=0.24, **score=744.99**.

**결과: 기각.** 가설(LightGBM을 제대로 튜닝하면 블렌드 이득이 커질
것)이 정확히 반대로 나옴 — 5종 설정 중 어느 것도 exp_013의 기본
설정(694.97)조차 확실히 못 넘음(slow_lr만 근소하게 +10, 나머지 4개는
오히려 더 나쁨), 여전히 CatBoost보다 35~110점 약함. 블렌드 결과도
744.99로 **exp_010 챔피언(749.58)보다 -4.59 낮음** — exp_013의
+2.02보다도 못한 결과. LightGBM이 이 84+5피처/1.2M행 데이터에서
CatBoost를 따라잡지 못하는 격차는 하이퍼파라미터 몇 개 조정으로
메워지는 수준이 아니라는 것을 재확인. **아카이브 안 함.**

**세션 최종 결론**: exp_010(749.58)이 이번 라운드(exp_010~017, 8개
실험) 전체의 확정 챔피언으로 유지됨.
