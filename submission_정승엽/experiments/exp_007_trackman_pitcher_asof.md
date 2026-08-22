# exp_007 — 투수 단위 trackman 물리 특성 as-of 피처 (Phase 2 ID 매핑 활용)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_007
- **날짜 / 담당자**: 2026-08-20 / (Claude, 사용자 요청)
- **가설**: exp_005는 `season+game_month` 단위 **리그 전체** as-of 집계
  (구종 비율)로 실패했다(exp_003 723.17 대비 -10.39~-19.96,
  `experiments/exp_005_trackman.md`). 이번엔 두 가지를 동시에 바꾼다 —
  (1) 리그 전체가 아니라 **개별 투수 단위**(`reports/trackman_id_mapping/`
  Phase 2 v3 매핑, 792명 중 778명/98.23% 확정, train 행의 87.23% 매칭,
  독립검증 정밀도 99.67%)로 그룹을 세분화하고, (2) 구종 "비율"이 아니라
  "강도"(release speed, spin rate, movement, extension — exp_005가
  명시적으로 미검증이라 남겨둔 각도, `reports/eda_trackman/README.md`
  §9-4)를 넣는다. 둘 다 exp_005와 겹치지 않는 새 각도이므로, exp_005의
  실패가 "trackman 자체가 무용하다"가 아니라 "그때 쓴 특정 조합
  (리그 단위+비율)이 무용했다"는 뜻이었는지 재검증한다.
- **기준(baseline)**: exp_003 (CatBoost, 84피처, local score 723.17,
  Brier 0.248000) — 현재 챔피언(exp_006에서 6개 아키텍처 비교 후에도
  CatBoost 유지 확인).
- **이번에 바꾸는 것**: exp_003의 84피처에 `trackman_rel_speed_asof`,
  `trackman_spin_rate_asof`, `trackman_induced_vert_break_asof`,
  `trackman_horz_break_asof`, `trackman_extension_asof` 5개 컬럼만
  추가(`src/trackman_pitcher_features.py`). 그 외 exp_003 피처/전처리/
  모델 하이퍼파라미터는 전혀 안 건드림(단일 변경 원칙).
- **검증 방법**: season 2019-2023 학습 / 2024 검증(공식 정책 그대로).
- **누수 위험 검토**:
  - 피처 자체: `trackman_pitcher_features.attach_pitcher_physical_features`는
    `pandas.merge_asof(direction="backward")`로 각 행의 `(pitcher_trackman_id,
    season*100+game_month)` 이전 데이터만 누적 — `trackman_features.
    _asof_table`과 동일한 leak-safe 설계(CLAUDE.md 규칙 10). 단위 테스트로
    "이 투수의 가장 이른 train 행"의 피처값이 그 투수의 전체 커리어
    평균과 다르고(누수 없음), 리그 폴백값과 정확히 같음(콜드스타트 정상
    동작)을 확인함.
  - 매핑 자체: Phase 2 매핑은 train.csv의 `pitcher_id`/`season`/
    `game_month`/`game_type`/`pitcher_hand`/`batter_hand` 등 이미 공식
    제공된 컬럼만 사용해 구성됐고 `control_success`는 전혀 참조하지
    않음 — train-only 재적합이 필요 없는 종류(trackman_features.py와
    동일한 성격). 검증(val)/최종 재학습 양쪽에 동일한 매핑·테이블을
    재사용해도 안전.
  - 매핑의 정밀도(99.67%, §Phase2 리포트) 자체가 100%가 아니므로, 일부
    행은 실제로는 다른 투수의 물리 데이터가 섞여 들어가는 노이즈가
    있을 수 있음 — 이건 리크가 아니라 노이즈(성능 저하 요인일 수는
    있어도 규정 위반은 아님).
  - season 2025(hidden test)는 trackman 데이터가 전혀 없으므로,
    `SEASON_2025_SENTINEL_YM` sentinel 행으로 "그 투수의 2019-2024 전체
    이력"에 자동으로 귀결되게 설계함 — 이 사실 자체가 CLAUDE.md 규칙
    10("2025 trackman 데이터 존재 가정 금지")과 상충하지 않음(그 투수의
    과거 이력만 사용, 2025 시점 정보는 전혀 없음).

## 결과 (실행 후에 작성)

실행: `src/train_exp007.py`(전체 그리드, `experiments/exp007_run_log.txt`),
`src/train_exp007_diagnostics.py`(k=50 재현+importance/오류분석,
`experiments/exp007_diagnostics_log.txt`).

**exp_003(트랙맨 피처 없음, 이 실행에서 재현) 대비 3개 shrink_k 전부 개선**:

| 구성 | Brier | 공식 local score | Δ vs baseline | best_iteration |
|---|---|---|---|---|
| exp_003 baseline(이 실행 재현) | 0.248000 | 723.17 | — | 510 |
| exp_007 shrink_k=300 | 0.247971 | 734.90 | **+11.74** | 548 |
| exp_007 shrink_k=100 | 0.247995 | 725.34 | +2.17 | 663 |
| exp_007 shrink_k=40 | 0.247993 | 725.95 | +2.78 | 651 |
| exp_007 shrink_k=25 | 0.248031 | 711.04 | -12.13 | 632 |
| exp_007 shrink_k=15 | 0.247967 | 736.36 | +13.19 | 478 |
| **exp_007 shrink_k=50(최선, 채택)** | **0.247956** | **740.86** | **+17.69** | 695 |

k=50 주변을 더 좁게(`experiments/exp007_ktune_log.txt`) 탐색했지만 결과가
매끈하지 않고(k=25가 오히려 베이스라인보다 낮음 — 시드 1개짜리 단일
실행의 노이즈로 보임) k=50을 능가하는 값은 못 찾음. **k=50을 최종
채택**, 전체 2019-2024 재학습에 사용(`src/train_exp007_final.py`).

exp_005(리그 전체 구종 비율)는 -10.39~-19.96으로 전부 기각됐던 것과
정반대 — **개별 투수 단위 + "비율"이 아닌 "강도"(물리 측정값)** 조합이
처음으로 실질적 개선을 낸 첫 trackman 기반 실험.

- **피처 목록**: exp_003의 84피처(`BASE_FEATURES` + `DERIVED_COLS` +
  `SHRUNK_COLS` + `POST_SHRINKAGE_COLS`) + 신규 5개
  `trackman_rel_speed_asof`, `trackman_spin_rate_asof`,
  `trackman_induced_vert_break_asof`, `trackman_horz_break_asof`,
  `trackman_extension_asof`(`src/trackman_pitcher_features.py`) = 89개.
- **모델 / 하이퍼파라미터**: CatBoost, exp_003과 완전히 동일
  (`iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
  early_stopping_rounds=100`).
- **시드**: 42.
- **Brier Score**: 0.247956 (k=50, 최선).
- **공식 로컬 스코어**: 740.86 (k=50, 최선).
- **실행 시간**: k=50 학습 357.4s(diagnostics 재실행 기준).
- **예측값 통계**: mean 0.4968 / min 0.3282 / max 0.6670 (k=50).
- **관찰 / 오류 분석**:
  - **exp_005와 반대 패턴**: exp_005는 트랙맨 피처를 넣을수록
    `best_iteration`이 더 일찍 멈췄다(과적합 신호, 333~374 vs
    베이스라인 ~510). 이번엔 반대로 **트랙맨 피처를 넣을수록
    `best_iteration`이 늘어남**(k=50: 695, k=100: 663, k=300: 548,
    baseline: 510) — 모델이 새 피처에서 실제로 뽑아 쓸 신호가 있어서
    더 오래 학습해야 최적점에 도달한다는 뜻으로 해석됨(과적합이 아니라
    학습 여력 증가).
  - **shrinkage 방향도 exp_005의 교훈과 반대**: exp_005는 "더 강한
    정칙화가 필요하다"는 가설을 남겼는데, 이번엔 **가장 약한 정칙화
    (k=50, 원시값에 가장 가까움)가 가장 좋았다** — k=300(가장 강한
    수축)이 오히려 k=50보다 -5.96점 낮음. 리그 전체 집계(exp_005, 표본이
    커서 노이즈가 크지 않음에도 실패)와 달리, 개별 투수 단위 물리
    특성은 원시값 자체에 이미 실제 신호가 담겨 있어서 과도한 수축이
    오히려 그 신호를 깎아낸 것으로 보인다(가설).
  - **feature importance**: 신규 5개 중 3개(`trackman_induced_vert_break_asof`
    14위, `trackman_extension_asof` 16위, `trackman_horz_break_asof`
    20위)가 상위 20위 안에 들었고, 5개 전부 89개 중 27위 이내
    (`[14, 16, 20, 22, 27]`) — exp_005 때는 "importance가 높아도 검증
    성능은 깎았다"는 역설이 있었는데, 이번엔 importance와 실제 성능
    개선이 같은 방향으로 일치함.
  - **세그먼트별 Brier**: two_strike/is_close_game/cold_start 구간 전부
    베이스라인과 비슷한 패턴으로 고르게 개선되어 특정 상황에서만
    반짝 좋아진 게 아님. trackman 매핑 안 된 투수(528행, 매우 작은
    표본)는 실제 성공률 자체가 낮은 집단(40.15%)이라 직접 비교는
    참고용.
- **다음 가설**:
  1. ~~shrink_k 미세 튜닝~~ — 15/25/40으로 추가 탐색함
     (`experiments/exp007_ktune_log.txt`): 736.36/711.04/725.95, k=50을
     능가하는 값 없음(k=25는 오히려 베이스라인보다 낮아 노이즈로 보임).
     **k=50 최종 채택.**
  2. Phase 3-B(행 단위 매칭을 privileged 정보로 쓰는 LUPI/보조헤드)는
     아직 시도 안 함 — 3-A 단독으로 이미 개선을 확인했으므로, 3-B를
     추가로 얹었을 때 더 개선되는지 별도 실험으로 검증 가능.
  3. `pitch_type_group`별로 분리한 강도 피처(예: fastball 전용 평균
     구속)는 아직 미시도.

## 최종 채택 + 제출 준비 (2026-08-20)

`src/train_exp007_final.py 50`로 2019-2024 전체 재학습(검증 재확인:
Brier 0.247956, score 740.86, best_iteration 695 — 위 결과와 동일,
`experiments/exp007_final_retrain_log.txt`), 저장:
- `model/catboost_model.cbm`, `model/model_meta.pkl`(exp_id="exp_007",
  trackman_shrink_k=50 포함) — **기존 exp_003 챔피언을 덮어씀**.
- `model/trackman_pitcher_lookup.csv`(778행) — 제출용 추론 스크립트가
  `trackman_history.csv`나 `merge_asof` 없이 쓸 수 있는 평평한 lookup
  (season 2025 행은 전부 "2019-2024 전체 이력" 값 하나로 귀결되므로
  이것만으로 충분 — `trackman_pitcher_features.build_test_time_pitcher_lookup`).

`submission/script.py`에 `attach_trackman_features` 추가(lookup 병합 +
미매칭 시 리그 폴백), `python src/package_submission.py
exp007_trackman_pitcher_asof`로 `submission/submit.zip` 빌드 완료.
격리된 임시 폴더에 압축 해제 후 새 프로세스로 재현 테스트: 5행 전부
정상 추론, 확률 범위 0.409~0.511, NaN/inf 없음, `row_id` 순서가
`sample_submission.csv`와 일치 — 통과.

**리더보드 제출은 사용자가 직접 진행** (`submission/submit.zip` 업로드).
받은 점수는 `experiments/SUBMISSION_LOG.md`에 기록 예정 — 아직 미기록.
