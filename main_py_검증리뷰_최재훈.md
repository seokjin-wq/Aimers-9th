# LG Aimers `main.py.ipynb` 독립 실행 검증 리뷰

- 검증 대상: `main.py.ipynb`
- 검증 목적: 모델 학습부터 제출 파일 생성·독립 추론까지 정상 작동하는지 확인
- 검증 범위: 로컬 실행 및 약 25만 행 규모 모의 추론
- 참고: 실제 DACON 평가 서버 제출 및 리더보드 평가는 수행하지 않음

## 1. 최종 의견

> **독립 실행 검증 통과 — 제출 전 일부 안정성 보완 권장**

`main.py.ipynb`를 임시 환경에서 처음부터 실행한 결과, 데이터 로드, 피처 생성, CatBoost 학습, 2024년 홀드아웃 검증, 전체 데이터 재학습, 모델 저장 및 제출 ZIP 생성까지 오류 없이 완료되었다. 생성된 `script.py`도 5행 샘플과 253,507행 규모의 모의 test에서 독립적으로 정상 실행되었다.

코드 실행을 막는 중대한 오류는 확인되지 않았다. 다만 최종 제출의 안정성과 재현성을 높이기 위해 `sample_submission.csv` 순서 반영, Cold-start 스무딩 결측 처리, 로컬 데이터 경로 설정을 보완하는 것이 좋다.

## 2. 실행 검증 결과

| 검증 항목 | 결과 | 확인 내용 |
|---|:---:|---|
| Notebook 실행 | 통과 | Cell 0~21을 임시 환경에서 순차 실행, 제출 ZIP 생성까지 완료 |
| 데이터 로드 | 통과 | train 1,475,092행, test·sample_submission 각 5행 로드 |
| 피처 생성 | 통과·주의 | 14개 파생변수 생성, 총 55개 피처 사용. Cold-start 파생변수에 일부 결측 발생 |
| CatBoost 학습 | 통과 | 2019~2023년 1,221,585행 학습 완료 |
| 2024년 검증 | 통과 | 253,507행 예측, Brier 0.247997, Local Score 724.41 |
| 전체 재학습 | 통과 | 2019~2024년 전체 1,475,092행 학습 완료 |
| 모델 저장 | 통과 | `model/rf.pkl` 저장 및 재로딩 확인 |
| 제출 ZIP 구조 | 통과 | `model/rf.pkl`, `script.py`, `requirements.txt`만 포함 |
| 5행 독립 추론 | 통과 | 분리된 임시 폴더에서 `script.py` 실행 및 제출 파일 생성 |
| 25만 행 모의 추론 | 통과 | 2024 시즌 253,507행을 test 형식으로 변환해 추론 완료 |
| 제출 파일 형식 | 통과 | 컬럼·행 수·중복·결측·확률 범위 검사 통과 |
| Git 저장소 영향 | 없음 | 검증 과정에서 원본 파일 수정, commit 및 push 미수행 |

## 3. 주요 실행 결과

- 검증 학습 시간: 약 24.7초
- 2024년 검증 Brier Score: `0.247997`
- 2024년 Local Score: `724.41`
- 전체 데이터 재학습 시간: 약 33.5초
- 5행 샘플 추론 시간: 약 2.63초
- 253,507행 모의 추론 시간: 약 4.31초
- 대용량 모의 추론 결과: 253,507행 모두 생성, 결측 예측 없음
- 예측 확률 범위: `0.324810~0.648707`
- 예측 확률 평균: `0.488032`

대용량 모의 추론은 실제 평가 데이터와 비슷한 행 수에서 실행 안정성을 확인하기 위한 검사다. 검증 PC는 평가 서버와 CPU·Python 버전이 다르므로, 위 시간은 참고값이며 실제 서버 실행 시간을 보장하지는 않는다.

## 4. 확인된 보완 사항

### 4.1 `sample_submission.csv` 순서 반영

현재 자동 생성되는 `script.py`는 `test.csv`의 행 순서대로 새 제출 DataFrame을 만든다. 로컬 배포본에서는 test와 sample_submission의 `row_id` 순서가 같아 정상 작동했지만, 최종 제출의 안정성을 위해 공식 baseline처럼 sample_submission을 기준으로 병합하는 방식이 더 안전하다.

권장 방식:

```python
test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
sub = pd.read_csv(os.path.join(DATA_DIR, "sample_submission.csv"))

X = build_features(test)
preds = model.predict_proba(X)[:, 1]

preds_df = pd.DataFrame({ID_COL: test[ID_COL], TARGET_COL: preds})
submission = sub[[ID_COL]].merge(preds_df, on=ID_COL, how="left")
```

병합 후에는 예측값 결측 여부와 행 수를 추가로 확인하는 것이 좋다.

### 4.2 Cold-start 스무딩 결측 처리

`asof_batter_n == 0`인 신규 타자에서는 `asof_batter_success_rate`가 결측일 수 있다. 현재 계산은 `NaN * 0` 결과도 `NaN`이기 때문에, 의도한 global prior 대신 후속 중앙값 대치가 적용된다.

검증 데이터에서는 해당 결측이 830건 확인되었으며 모델 Pipeline의 `SimpleImputer`가 처리하므로 실행 오류는 발생하지 않았다. 다만 스무딩 의도를 명확하게 반영하려면 다음처럼 처리하는 것이 적절하다.

```python
n = df["asof_batter_n"].fillna(0)
rate = df["asof_batter_success_rate"].fillna(GLOBAL_SUCCESS_RATE)

df["batter_success_rate_shrunk"] = (
    rate * n + GLOBAL_SUCCESS_RATE * SHRINKAGE_K
) / (n + SHRINKAGE_K)
```

### 4.3 로컬 데이터 경로 설정

Notebook의 `DATA_DIR`이 특정 사용자 경로로 고정되어 있어 다른 팀원이 실행하려면 직접 수정해야 한다. 평가용 `script.py`는 상대경로를 사용하므로 제출 실행 자체의 문제는 아니지만, 팀 협업과 재현성을 위해 환경변수 또는 상대경로를 사용하는 것이 좋다.

```python
DATA_DIR = os.environ.get(
    "DATA_DIR",
    "../data" if os.path.exists("../data/train.csv") else "data",
)
```

### 4.4 로컬 검증 prior 분리

현재 `GLOBAL_SUCCESS_RATE`는 2019~2024년 전체 타깃 평균이다. 2024년을 validation으로 사용할 때는 학습 구간인 2019~2023년 평균을 사용하는 것이 검증 원칙상 더 적절하다.

누수 차단 방식으로 재계산한 결과 Local Score는 `724.41`에서 `727.26`으로 소폭 상승하여, 현재 prior가 점수를 과도하게 높인 정황은 확인되지 않았다. 다만 향후 모델 비교의 일관성을 위해 validation 단계에서는 학습 구간 prior를, 최종 전체 학습 단계에서는 전체 train prior를 각각 사용하는 것을 권장한다.

## 5. 제출 코드 관점의 결론

- 모델링 및 제출 파이프라인은 로컬 환경에서 정상 실행되었다.
- 제출 ZIP의 최상위 구조와 필수 파일 구성도 정상이다.
- 5행 샘플뿐 아니라 실제 평가 데이터와 유사한 253,507행에서도 독립 추론이 완료되었다.
- 중대한 실행 오류는 확인되지 않았으며, 확인된 사항은 제출 안정성·재현성을 높이기 위한 보완 항목이다.
- 실제 평가 서버의 패키지 설치 여부와 리더보드 성능은 최종 DACON 제출을 통해 별도로 확인해야 한다.

따라서 현재 코드는 **기본 실행 검증을 통과한 상태**로 판단하며, 가능하다면 `sample_submission` 기준 정렬과 Cold-start 스무딩 처리를 반영한 후 최종 제출하는 것을 권장한다.
