# exp_033 — 학습 시 시즌 가중치 감쇠 (season_decay)

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_033
- **날짜 / 담당자**: 2026-08-22 / (Claude, 사용자 요청 —
  `docs/teammate_score_gap_analysis.md` 확신도 중간 후보)
- **가설**: `weight = decay ** (max_season - row_season)`를 CatBoost
  `.fit()`에 줘서 모델 자체가 최근 시즌 패턴에 더 최적화되도록 학습
  시점에 개입하면, 사후보정(Platt/count-trend)만으로는 못 잡는 이득이
  있다. 팀원 EXP_060/130은 decay=0.85를 채택.
- **기준(baseline)**: exp_030_repro, score=875.00(Brier 0.247621,
  `src/train_exp030_repro.py`).
- **이번에 바꾸는 것(한 가지로 한정)**: exp_030과 동일한 2시드
  CatBoost 아키텍처(105피처, 동일 하이퍼파라미터) 위에서
  `decay ∈ {0.80, 0.85, 0.90, 1.0}`만 스윕 — 피처/모델구조/보정
  체인 전부 동결. `1.0`은 가중치 없음(현재 exp_030과 동일)이라
  null case 역할.
- **검증 방법**: season 2019-2023 학습 / 2024 검증. `max_season`은
  **학습에 쓰이는 2019-2023 자체의 최댓값(2023)** — 2024나 2025로
  계산하면 안 됨(누수).
- **누수 위험 검토**: `weight`는 각 행 자신의 `season` 컬럼(이미
  공식 피처로 쓰이고 있음)에서 계산되는 순수 행-로컬 스칼라 —
  train split 밖 정보 미사용. CatBoost `sample_weight`는 손실함수
  가중치일 뿐 새로운 cross-row 의존성을 만들지 않음.

## 결과 (실행 후에 작성)

(실행 후 채움)
