# LG Aimers 9기 대회 평가 및 코드 제출 가이드

## 1. 리더보드 평가 지표

본 대회는 각 투구의 `control_success = 1`일 확률을 예측한다. 예측 확률이
실제 정답에 가까울수록 Brier Score는 낮아지고 Brier Skill Score는 높아진다.

### Brier Score

```text
Brier Score = mean((p_i - y_i)^2)
```

- `p_i`: i번째 투구의 제구 성공 예측 확률
- `y_i`: i번째 투구의 실제 정답 (`0` 또는 `1`)

### 평균 제구율 기준 Brier Score

```text
r = mean(y_i)
평균 제구율 Brier Score = r × (1 - r)
```

`r`은 전체 평가 데이터의 평균 제구 성공률이며 공개되지 않는다. 이 기준은
모든 투구에 평가 데이터의 평균 성공률을 예측하는 상수 모델의 Brier
Score와 같다.

### 최종 점수

```text
Score = max(0, 100000 × (1 - Brier Score / (r × (1 - r))))
```

- 기준 상수 모델과 같으면 이론상 `0점`
- 기준보다 Brier Score가 낮아야 양수 점수
- Brier Score가 작을수록 대회 점수는 높음
- 평가 데이터의 `r`이 비공개이므로 로컬 BSS와 리더보드 BSS는 직접 일치하지
  않을 수 있음

### Public·Private Score

- Public Score: 전체 테스트 데이터 100%로 계산
- Private Score: 대회 종료 시점의 Public Score

별도의 Public/Private 데이터 분할이 아니라 종료 시점에 Public 결과가 Private
평가로 전환되는 구조다.

## 2. 평가 및 진출 방식

### LG Aimers 수료 조건

- Phase 1 이수
- Phase 2 Public Score `549.51` 이상
- 기준 점수는 운영진 베이스라인 추론 코드를 운영진 평가 환경에서 실행한
  결과로 측정

### 1차 평가

- Private 리더보드 점수 100%
- 동점자는 데이콘의 기존 리더보드 순위 산정 방식 적용

### 2차 평가 및 Phase 3 진출

- Phase 3 진출 희망 팀은 코드 제출 후 코드 검증을 받아야 함
- Private 리더보드 상위 약 100명은 코드와 PPT 필수 제출 대상
- 코드·PPT 제출 및 검증을 통과한 상위 약 100명이 Phase 3에 진출

높은 리더보드 점수만으로 진출이 확정되지 않으며, 규칙을 준수하고 재현 가능한
코드 제출이 필수다.

## 3. 제출 ZIP 구조

제출 파일은 다음 최상위 구조와 이름을 정확히 따라야 한다.

```text
submit.zip
├── model/
│   └── 모델 가중치 파일
├── script.py
└── requirements.txt
```

- `script.py`: 평가 서버에서 자동으로 실행되는 추론 코드
- `requirements.txt`: `pip install -r requirements.txt`로 설치 가능한 형식
- 필요한 외부 패키지와 버전을 모두 명시
- 추가 최상위 파일이나 디렉터리를 넣지 않음
- ZIP 안에 `submit/` 같은 상위 디렉터리를 한 번 더 감싸지 않음

현재 워크스페이스의 기존 `submit.zip`은 추가 최상위 항목을 포함하며 행
독립성 규칙도 위반하므로 제출하면 안 된다.

## 4. 평가 서버가 추가하는 항목

평가 시 서버가 다음 항목을 추가한다.

```text
submit.zip 실행 환경
├── model/                 # 참가자 제출
├── script.py              # 참가자 제출
├── requirements.txt       # 참가자 제출
├── data/                  # 평가 데이터, 서버가 생성
└── output/
    └── submission.csv     # 참가자 코드가 생성
```

- `data/`는 읽기 전용이며 수정할 수 없음
- `script.py`는 `output/submission.csv`를 반드시 생성해야 함
- 출력 파일명과 경로를 정확히 지켜야 함

### 입력 경로 확인 필요

제공된 가이드의 구조 설명은 `data/`를 입력 경로로 표기하지만 마지막
유의사항에는 `open/` 데이터를 로드한다고 적혀 있다. 서로 다른 표기가 있으므로
최종 제출 전 최신 기본 가이드의 예제 `script.py`와 실제 평가 탭을 확인한다.
코드에 임의로 두 경로를 가정하지 않는다.

## 5. 용량 및 시간 제한

| 항목 | 제한 |
|---|---:|
| 제출 ZIP 크기 | 10GB 이하 |
| 압축 해제 후 크기 | 32GB 이하 |
| 패키지 설치 | 10분 이하 |
| 추론 코드 실행 | 10분 이하 |
| 평가 샘플 | 245,789개 |

## 6. 평가 서버 환경

| 항목 | 환경 |
|---|---|
| OS | Ubuntu 22.04.5 LTS |
| Python | 3.11.15 |
| CPU | 6 vCPU |
| RAM | 28GB |
| GPU | NVIDIA L4, VRAM 22.4GiB |
| CUDA | 12.8 |
| 인터넷 | 패키지 설치 외 비활성화 |

패키지 설치가 끝난 뒤 외부 서버에서 모델이나 파일을 다운로드하는 코드는
실행할 수 없다.

## 7. 평가 서버 기본 Python 패키지

가급적 아래 기본 버전을 그대로 사용하고, 이미 설치된 패키지는 불필요하게
`requirements.txt`에 다시 넣지 않는다. 다른 버전을 강제로 설치하면 의존성
충돌이나 설치 오류가 발생할 수 있다.

```text
torch==2.7.1+cu128
pandas==2.0.3
numpy==1.26.4
scipy==1.15.3
scikit-learn==1.8.0
joblib==1.5.3
threadpoolctl==3.6.0
narwhals==2.21.2
transformers==4.46.3
accelerate==1.9.0
sentencepiece==0.1.99
regex==2023.12.25
tqdm==4.66.4
loguru==0.7.2
pyyaml==6.0.1
rich==13.7.1
```

## 8. 평가 서버 기본 시스템 패키지

```text
git
build-essential
python3.11
python3.11-dev
python3.11-venv
python3-pip
libffi-dev
libblas3
liblapack3
libomp-dev
tzdata
unzip
p7zip-full
gfortran
libatlas-base-dev
default-jre-headless
cmake
pkg-config
ninja-build
libgl1
libglib2.0-0
```

## 9. 오류 유형

### 설치 오류

- ZIP 내부 구조 불일치
- 패키지 설치 실패
- 일일 제출 횟수에 반영되지 않음

### 제출 오류

- `script.py` 실행 후 발생하는 모든 오류
- 입력 데이터 로드 실패
- 모델 로드 또는 추론 실패
- `output/submission.csv` 생성 실패
- 일일 제출 횟수에 반영됨

## 10. 최종 제출 게이트

- [ ] ZIP 최상위가 `model/`, `script.py`, `requirements.txt`만 포함하는가?
- [ ] Python 3.11.15에서 모델과 전처리 객체를 불러올 수 있는가?
- [ ] 기본 numpy·pandas 버전에서 실행되는가?
- [ ] 입력 경로가 최신 공식 예제와 일치하는가?
- [ ] `output/submission.csv`를 정확히 생성하는가?
- [ ] 245,789개 행을 10분 이내에 추론하는가?
- [ ] RAM 28GB와 6 vCPU 제한을 만족하는가?
- [ ] 인터넷 없이 실행되는가?
- [ ] 출력 확률이 모두 `[0, 1]` 범위인가?
- [ ] sample submission의 행과 순서를 보존하는가?
- [ ] [`COMPETITION_RULES.md`](COMPETITION_RULES.md)의 행 독립성 테스트를
  모두 통과하는가?

하나라도 통과하지 못하면 리더보드 점수와 관계없이 제출하지 않는다.

## 문서 관계

- 문제 정의와 참가·실행 환경:
  [`COMPETITION_OVERVIEW.md`](COMPETITION_OVERVIEW.md)
- 평가 데이터 행 독립성 규칙:
  [`COMPETITION_RULES.md`](COMPETITION_RULES.md)
- 팀·데이터·모델·사후 제출 일반 규칙:
  [`COMPETITION_GENERAL_RULES.md`](COMPETITION_GENERAL_RULES.md)
- 실험 실행 및 기록 방법: [`../README.md`](../README.md)
