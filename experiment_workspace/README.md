# LG Aimers experiment workspace

팀 저장소인 `../Aimers-9th`를 수정하지 않고 실험을 수행하는 독립
워크스페이스입니다. 현재 기준선은 팀 저장소의
`submission_허원준` 후보를 코드 기준으로 재현합니다.

## 절대 원칙

- 대회 문제와 제출 환경은 [`docs/COMPETITION_OVERVIEW.md`](docs/COMPETITION_OVERVIEW.md)를
  기준으로 확인한다.
- 점수 산식과 제출 ZIP 규격은 [`docs/COMPETITION_EVALUATION.md`](docs/COMPETITION_EVALUATION.md)를
  기준으로 확인한다.
- 팀·데이터·모델·코드/PPT 규칙은 [`docs/COMPETITION_GENERAL_RULES.md`](docs/COMPETITION_GENERAL_RULES.md)를
  기준으로 확인한다.
- 대회 추론 규칙은 [`docs/COMPETITION_RULES.md`](docs/COMPETITION_RULES.md)를
  실험보다 먼저 적용한다.
- `../Aimers-9th`는 읽기 전용 참고 자료다.
- 원본 데이터 `../open`은 수정하지 않는다.
- 비교 실험에서는 검증 프로토콜을 고정하고 한 종류의 설정만 바꾼다.
- 모든 실행은 resolved config, 환경, 데이터 지문, fold별 예측과 지표를 남긴다.
- `runs/`와 모델은 Git에 넣지 않고, 재생성 가능한 설정과 요약 리포트만 관리한다.

## 현재 채택 후보

- provenance: `Aimers-9th` commit `349498b`
- experiment: `EXP_130 / triple_count_trend_ols` (규칙 준수 후보)
- feature set: `main78_history_reliability` (78개)
- model: CPU CatBoost 50% + GPU CatBoost 35% + ExtraTrees 15%
- primary validation: 2019~2023 학습 → 2024 고정 홀드아웃
- validation Brier Skill Score: `945.4411`
- correction: 2023→2024 OOT count residual + count별 OLS season trend
- final training: 2019~2024 전체 학습 → 2025 행 독립 추론
- final package: `output/final/submit.zip` (독립성 검사 최대 차이 `< 1e-12`)

## 구조

```text
experiments/
├── index.csv                    # 전체 실험 진행표
├── BASELINE_001_main55/         # 공통 모델·피처·프로토콜·출처 설정
├── rule_invalid/                # 규칙 위반 판정 실험의 읽기 전용 격리 기록
├── EXP_001/
│   ├── experiment.toml          # 질문, 가설, 변경 범위, 계보
│   ├── study.toml               # control과 variants
│   ├── state.json               # draft/running/completed/decided
│   ├── history.jsonl            # 시간순 이벤트 기록
│   ├── runs/RUN_NNN/             # 실행 시점의 완전한 설정 snapshot
│   │   ├── summary.json          # compact 실행 결과
│   │   ├── resolved_config.json  # 코드가 읽는 전체 해석 설정
│   │   ├── protocol.toml         # 실제 검증 설정
│   │   ├── ablation_diff.json    # control 대비 정확한 변경값
│   │   └── variants/*/           # variant별 model/features TOML과 피처 목록
│   ├── decision.md               # 사람이 읽는 최신 최종 판단
│   └── decision.json             # 자동화가 읽는 최신 최종 판단
└── EXP_NNN/
src/aimers_exp/                  # 실행·기록 자동화 코드
tests/                           # 설정·피처·기록 규칙 테스트
runs/                            # 예측 포함 원본 산출물 (Git 제외)
output/                          # 모델과 제출 ZIP (Git 제외)
```

## 실행

Conda 환경은 기존 `lgaimers`를 사용합니다.
대회 데이터는 `experiment_workspace/data/`에 두며 Git에는 포함하지 않습니다.

```bash
cd /home/chanheo/lgaimers/Aimers-9th/experiment_workspace
conda activate lgaimers

# 전체 실험 진행 상황
python run.py exp-list

# EXP_002의 가설과 실제 설정 차이 확인
python run.py exp-plan EXP_002

# 실행하고 RUN_NNN, 결과표, 이력을 자동 기록
python run.py exp-run EXP_002

# 한 실험의 최신 결과와 최종 판단 확인
python run.py exp-show EXP_002

# 필요할 때만 과거 이벤트 이력까지 확인
python run.py exp-show EXP_002 --history

# 완료 결과에 사람의 판단 기록
python run.py exp-decide EXP_002 \
  --decision keep_control \
  --reason "제거 variant 모두 평균 Brier가 악화되어 main55를 유지"

# 현재 baseline의 final 설정으로 제출 ZIP 생성
python run.py build \
  --config experiments/BASELINE_001_main55/final.toml

# ZIP을 임시 디렉터리에서 독립 실행 검증
python run.py validate-package --zip-path output/final/submit.zip

# 빠른 테스트
python -m pytest -q
```

`runs/`에는 검증 예측까지 포함한 무거운 원본이 생성되고 Git에서 제외됩니다.
동시에 `experiments/EXP_NNN/runs/RUN_NNN/`에는 실행 순간의 모든 TOML,
전체 resolved config, 정확한 ablation diff, 결과표와 보고서가 남아 Git으로
보존됩니다. Brier는 낮을수록
좋으며 `delta_brier_vs_control`이 음수면 개선입니다.

## 새 ablation 추가

```bash
python run.py exp-new \
  --title "새 피처 묶음 ablation" \
  --hypothesis "새 피처가 평균 Brier를 개선한다" \
  --scope features \
  --based-on EXP_003 \
  --reference-variant main55_control \
  --ablation "EXP_003 대비 새 피처 묶음만 추가"
```

명령이 다음 `EXP_NNN`과 그 안의 `study.toml` 템플릿을 만듭니다.

1. 새 `EXP_NNN/study.toml`의 TODO variant를 수정한다.
2. 필요한 새 모델·피처 정의만 `BASELINE_001_main55` 아래에 추가한다.
3. `exp-plan EXP_NNN`으로 실제 변경 필드와 준비 상태를 확인한다.
4. `exp-run EXP_NNN`으로 실행과 기록을 함께 수행한다.
5. `exp-show EXP_NNN`으로 가설부터 결과까지 확인한다.
6. `exp-decide`로 채택·기각 이유를 기록한다.

최종 후보를 고른 뒤에만 seed 반복, 하이퍼파라미터 및 calibration study를
진행합니다. 피처 선별 단계에서는 calibration을 적용하지 않습니다.

모든 ablation의 채택 기준은 2024 홀드아웃 Brier입니다. 2022~2023
backtest는 calibration 값을 과거 데이터만으로 만들거나 최종 후보의 안정성을
진단할 때만 사용하며 primary leaderboard에는 섞지 않습니다. 2025 제출용
최종 calibration은 2022~2024에서 확정할 수 있지만, 2024 검증 예측을
보정할 때는 2024 결과를 보정값 계산에 사용하면 안 됩니다.
