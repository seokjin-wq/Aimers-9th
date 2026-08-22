# exp_008 — trackman 투수 단위 as-of 물리 특성 확장 (5개 -> 8개)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_008
- **날짜 / 담당자**: 2026-08-21 / (Claude, 사용자 요청 — LB 863.05/57664등에서
  점수를 더 끌어올리기 위한 2라운드, `dacon-score-push-round2` 메모리 참고)
- **가설**: exp_007은 `trackman_history.csv`의 물리 컬럼 8개 중 5개
  (`rel_speed`, `spin_rate`, `induced_vert_break`, `horz_break`,
  `extension`)만 썼다. 나머지 3개(`rel_height`, `rel_side` — 릴리스
  포인트 위치, `zone_speed` — 스트라이크존 통과 시점 속도, rel_speed와
  달리 구질별 감속 차이를 반영하는 "체감 구속"에 더 가까움)도 투수마다
  고유하고 안정적인 신체/투구폼 특성이므로, exp_007과 같은 논리
  (개별 투수 단위 + "비율"이 아닌 "강도")로 추가 신호가 있을 것이다.
- **기준(baseline)**: exp_007 (CatBoost, 89피처 = exp_003 84 + trackman
  5, local score 740.86, Brier 0.247956) — 현재 챔피언.
- **이번에 바꾸는 것**: `src/trackman_pitcher_features.py`의
  `PHYSICAL_COLS`를 5개→8개로 확장(rel_height/rel_side/zone_speed
  추가), 나머지(매핑 테이블, shrinkage 공식, CatBoost 하이퍼파라미터)는
  exp_007과 동일. shrink_k는 exp_007에서 확정된 50과, 참고용으로 100도
  같이 비교(스케일이 다른 신규 컬럼이라 최적 k가 다를 가능성 확인).
- **검증 방법**: season 2019-2023 학습 / 2024 검증(공식 정책 그대로).
- **누수 위험 검토**: exp_007과 완전히 동일한 leak-safe 설계
  (`merge_asof(direction="backward")`, season 2025 sentinel 행) —
  새로 추가되는 3개 컬럼도 같은 `attach_pitcher_physical_features`
  함수를 그대로 통과하므로 별도 검토 불필요. 매핑 자체(Phase 2)도
  `control_success`를 전혀 참조하지 않는 컬럼만 사용해 구성됐음(기존
  검증 재사용).

## 결과 (실행 후에 작성)

실행: `src/train_exp008.py`, 전체 로그 `experiments/exp008_run_log.txt`.

| 구성 | Brier | 공식 local score | Δ vs A(baseline) | Δ vs B(exp_007) | best_iter |
|---|---:|---:|---:|---:|---:|
| A. exp_003 baseline(이 실행 재현) | 0.248000 | 723.17 | — | — | 510 |
| B. exp_007 5col k=50(이 실행 재현) | 0.247956 | 740.86 | +17.69 | — | 695 |
| C. exp_008 8col k=50 | 0.247998 | 724.19 | +1.02 | **-16.67** | 767 |
| C. exp_008 8col k=100 | 0.248052 | 702.65 | -20.51 | -38.21 | 485 |

**가설 기각.** `rel_height`/`rel_side`/`zone_speed` 3개를 추가하니
exp_007의 5개짜리 세트보다 오히려 크게 나빠짐(k=50에서 -16.67,
k=100에서는 exp_003 baseline보다도 낮은 -20.51). exp_003의 A와 거의
같은 수준(+1.02)으로 수렴한 것으로 보아, 이 3개 컬럼은 순수하게
노이즈를 추가해 트리 분할 예산을 갉아먹은 것으로 해석됨 — release
point(rel_height/rel_side)는 투수 개인 신체 특성상 매우 안정적이라
변별력이 거의 없거나(모든 투구에서 거의 동일값), zone_speed는
rel_speed와 상관관계가 매우 높아(둘 다 "속도" 지표) 사실상 중복
정보이면서 약간의 노이즈만 추가했을 가능성.

**결론**: `src/trackman_pitcher_features.py`의 `PHYSICAL_COLS`는
exp_007의 원래 5개로 되돌림(코드에 기각 사유 주석 추가). 챔피언은
여전히 exp_007(5col, k=50, local 740.86 / LB 863.05).

- **다음 가설**: pitch_type_group별로 세분화한 강도 피처(예: fastball
  전용 평균 구속)는 exp_007에서부터 미시도 상태로 남아있음 — 이번
  결과로 "컬럼 수를 무작정 늘리는 게 아니라 신호 대비 노이즈 비율이
  중요하다"는 게 재확인됐으므로, 시도한다면 반드시 개별 ablation으로
  검증할 것. 지금은 exp_009(하이퍼파라미터 튜닝)로 진행.
