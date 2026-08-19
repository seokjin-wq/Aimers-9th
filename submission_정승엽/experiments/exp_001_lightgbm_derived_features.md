# exp_001 — 파생 피처 + LightGBM (1차 팀 회의용 제출)

## 실험 개요

- **실험 ID**: exp_001
- **날짜 / 담당자**: 2026-08-07 / (설정 필요)
- **가설**: 기존 47개 공식 피처에 안전한(리키지 없는) 행 단위 파생 피처를 추가하고, 모델을 얕은 RandomForest에서 LightGBM으로 바꾸면 예측 분포가 넓어지고 Brier Skill Score가 개선된다.
- **기준(baseline)**: exp_000 (공식 베이스라인 재현, 415.57)
- **이번에 바꾸는 것**: (참고: 이번엔 시간 제약상 두 가지를 동시에 바꿈 — 피처 15개 추가 + 모델 교체. 정상적인 실험 원칙(한 번에 하나만 변경)에는 어긋나지만, 오늘 팀 회의 전 "동작하는 개선된 파이프라인"을 빠르게 확보하는 게 목적이라 의도적으로 묶었음. **다음 실험에서는 반드시 분리해서 어느 쪽이 얼마나 기여했는지 확인할 것.**)
- **검증 방법**: season 2019-2023 학습 / season 2024 검증 (베이스라인과 동일)
- **누수 위험 검토**: 추가한 15개 파생 피처는 모두 해당 행에 이미 존재하는 공식 컬럼(카운트, 점수차, 주자상황, `asof_*`)만으로 계산한 행 단위 연산 (`src/features.py` 참고) — 다른 행 정보나 사후 정보 없음. CLAUDE.md 규칙과 충돌 없음.

## 결과

- **피처 목록**: 공식 47개 + 파생 15개 = 62개 (`src/features.py`의 `DERIVED_COLS` — 카운트 상태, 스코어마진/접전 여부, 득점권 주자 여부, 투수-타자 성공률 차이, 투수 최근 폼 변화, 경험치 로그스케일, 구종 다양성 지수 등)
- **모델**: LightGBM (`n_estimators=2000` + early stopping, `learning_rate=0.03`, `num_leaves=63`, `subsample=0.8`, `colsample_bytree=0.8`, `min_child_samples=200`), 범주형 3개는 `OrdinalEncoder` 정수 인코딩 후 `categorical_feature`로 지정
- **시드**: 42
- **best_iteration**: 173 (조기종료, patience 100)
- **Brier Score**: 0.248237 (exp_000: 0.248769)
- **기준선 r(1-r)**: 0.249807
- **공식 로컬 스코어**: **628.51** (exp_000 대비 +212.94, 약 +51%)
- **실행 시간**: 학습 9.6초 + 최종 재학습 8.3초 (RandomForest 76초 대비 훨씬 빠름)
- **예측값 통계**: mean 0.4972 / min 0.3500 / max 0.6403 (exp_000: 0.41~0.62 → 범위가 넓어짐, 더 많은 신호를 반영하는 것으로 보임)
- **주요 피처 중요도 top 5**: `asof_pitcher_n`, `season`, `asof_batter_success_rate`, `asof_pitcher_reverse_rate`, `asof_pitcher_prev5_game_success_rate` — 투수의 표본 수와 최근 성공률이 가장 중요. 파생 피처 중에서는 `pitcher_recent_form_delta`, `pitchmix_diversity`가 상위권에 듦.

### 발견한 버그 (다른 실험에도 영향 줄 수 있음)

`LGBMClassifier`(sklearn 래퍼)를 `joblib.dump`로 저장한 뒤 **다른 프로세스**에서 `joblib.load`로 불러와 예측하면, 이 환경(Windows, lightgbm 4.7.0)에서 `access violation` 네이티브 크래시가 100% 재현됨 (같은 프로세스 안에서는 문제없이 동작 — 프로세스 경계를 넘을 때만 발생). 원인은 Booster의 C 핸들이 unpickle 시 제대로 복원되지 않는 것으로 추정.

**해결**: `booster_.save_model(path)` / `lgb.Booster(model_file=path)` — LightGBM 자체 텍스트 포맷으로 저장/로드하면 문제없이 동작. 이후 이 프로젝트에서 LightGBM 모델은 전부 이 방식을 쓸 것 (`src/train_lgbm.py`, `submission/script.py` 참고). **팀원들도 LightGBM 쓸 때 이 이슈 주의.**

### 제출 패키징

- `submission/model/{lgbm_booster.txt, lgbm_meta.pkl}` + `submission/script.py` + `submission/requirements.txt`(`lightgbm==4.7.0`만 추가 — 나머지는 평가 서버 사전 설치 버전과 일치)
- 로컬에서 zip 압축 해제 → 격리된 폴더에서 재실행까지 검증 완료 (5행 샘플 정상 동작)
- zip 내부 경로 구분자를 슬래시(`/`)로 명시 (Windows `Compress-Archive` 기본값은 백슬래시라 Linux 평가 서버에서 풀릴 때 문제될 수 있어 수동으로 고침)
- **아직 확인 못한 것**: 실제 평가 규모(245,789행)에서의 추론 시간 — 5행 샘플로는 시간 측정 의미 없음. 대용량으로 한 번 더 시간 재보는 걸 권장 (10분 제한).

## 다음 가설 (→ 회의 안건)

1. 피처 추가 효과와 모델 교체 효과를 분리해서 각각 측정 (RandomForest+파생피처, LightGBM+원본피처만 따로 실험)
2. `trackman_history.csv` 조인 가능성 검증 — `pitcher_id`/`pitcher_trackman_id`가 같은 ID 공간인지부터 확인 필요 (리키지 위험 있어 신중하게 설계)
3. XGBoost와 비교, 앙상블 여부 검토
4. 하이퍼파라미터 튜닝 (현재 값은 대표적인 기본값 수준, 최적화 안 함)
