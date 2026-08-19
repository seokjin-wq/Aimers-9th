# submission_202103116

개인 private 작업 레포에서 팀에 공유할 가치가 있는 부분만 선별해 옮긴
스냅샷입니다. 전체 데이터/모델 아티팩트는 대회 규정(`data/` 원본, 학습된
모델 바이너리 재배포 금지)에 따라 제외했습니다.

## 구성

- **`src/`** — 피처 엔지니어링 및 학습 코드
  - `features.py`: 공식 `train.csv`/`test.csv` 컬럼 기반 파생 피처 생성
    (cold-start shrinkage 포함)
  - `trackman_features.py`: `trackman_history.csv` 기반 `(season, game_month)`
    as-of 누적 조인 인프라 (검증됨, 현재 어떤 학습 스크립트도 사용하지 않음
    — 아래 exp_005 참고)
  - `train_exp003.py`, `train_lgbm.py`: 학습 스크립트
  - `package_submission.py`: 제출용 zip 패키징 스크립트

- **`experiments/`** — 실험 기록 (`TEMPLATE.md` 양식, exp_000~exp_005)
  - `exp_000_baseline_repro.md`: 공식 baseline 재현
  - `exp_001_lightgbm_derived_features.md`: LightGBM 전환 + 파생 피처
  - `exp_002_asof_refinement.md`: asof_* 피처 정교화 + cold-start shrinkage
  - `exp_003_*.md`: CatBoost 전환 + EDA 기반 피처 추가
  - `exp_004_feature_simplification.md`: 피처 단순화 시도 (기각)
  - `exp_005_trackman.md`: 트랙맨 파생 피처 4종 시도 (전부 기각 — 조인
    메커니즘 자체는 문제 없었으나 검증 성능은 하락)
  - `SUBMISSION_LOG.md`: 리더보드 제출 기록
  - `exp*_run_log.txt`, `exp*_ablation_*.txt`: 각 실험의 실행 로그 원본
    (md에서 인용하는 수치의 출처)

- **`reports/eda_trackman/`** — `trackman_history.csv`(1,793,078행×30컬럼,
  2019~2024) 기본 EDA. 데이터 품질, 시간 커버리지, 선수/팀 ID 공간,
  구종 분류, 수치형 특성 분포, 결측치, train.csv와의 연결 가능성을
  섹션별 목적/방법/결과/시사점으로 정리했고 그리드 시각화 8종 포함.
  `README.md`가 진입점이며, `figures/`·`tables/`는 그 안에서 참조됩니다.

## 핵심 결론 요약

- `trackman_history.csv`와 `train.csv`는 **선수/팀 단위 직접 조인 키가
  없습니다** (ID 값 범위 자체가 다른 익명화 공간 — `reports/eda_trackman/README.md`
  §8 참고).
- `season`+`game_month` 기준 as-of 조인은 구현·검증까지 마쳤지만, 이걸로
  만든 4개 파생 피처는 실제 검증 점수를 오히려 낮췄습니다(`exp_005`).
  다음에 트랙맨을 다시 시도한다면 원시 비율값이 아니라 더 강하게
  정칙화된 형태, 또는 팀 단위(아직 안 다뤄본 각도)를 검토해볼 만합니다.
