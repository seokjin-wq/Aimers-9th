# CatBoost + EDA 기반 피처 선별

[Colab에서 바로 열기](https://colab.research.google.com/github/seokjin-wq/Aimers-9th/blob/main/submission_%ED%97%88%EC%9B%90%EC%A4%80/catboost_feature_ablation.ipynb)

기존 RandomForest 기준에서 모델과 피처를 한꺼번에 바꾼 결과만 남기지 않고, 아래 순서로 차이를 분리해 확인했다.

1. 제공 피처 47개를 그대로 두고 RandomForest와 CatBoost를 비교했다.
2. 제공 피처를 기초 관측·식별 17개, 행 단위 파생 11개, 과거 기록 파생 19개로 구분했다.
3. 시즌 순서 검증에서 과거 기록과 새 파생 피처의 추가 효과를 확인했다.
4. 중복되거나 복원 실험에서 불필요했던 제공 피처 6개를 제외했다.
5. 최종 55개 피처로 전 시즌을 학습하고, 과거 검증 시즌에서 정한 확률 보정값을 적용했다.

## Colab에서 실행

필요한 데이터 파일은 다음 세 개다.

- `train.csv`
- `test.csv`
- `sample_submission.csv`

가장 간단한 방법은 세 파일이 들어 있는 `open.zip`을 Google Drive의 아래 위치에 두는 것이다.

```text
내 드라이브/LG Aimers 9기/release data/open.zip
```

Colab 노트북을 연 뒤 위에서부터 모든 셀을 실행하면 저장소 복제, 라이브러리 설치, 데이터 압축 해제, 최종 학습, 제출 ZIP 생성, 5개 행 실행 검증까지 진행된다. 다른 위치를 쓸 때는 데이터 설정 셀의 `DRIVE_ZIP_PATH`만 바꾸면 된다.

최종 결과는 다음 위치에 생성된다.

```text
/content/Aimers-9th/submission_허원준/output/submit.zip
```

CPU 기준 실행을 전제로 하며 GPU는 필요하지 않다. 전체 학습에는 환경에 따라 수 분이 걸릴 수 있다.

## 최종 피처 55개

| 출처 | 개수 | 포함 내용 |
| --- | ---: | --- |
| 제공 기초 관측·식별 | 17 | 이닝, 초·말, 경기 유형, 볼·스트라이크·아웃, 득점·주자, 선수·손 유형·팀 ID |
| 제공 행 단위 파생 | 9 | 시즌·월·요일, 투수 팀 기준 점수차, 주자 수·상태, 기대 승률, LI |
| 제공 과거 기록 파생 | 15 | 투수·타자의 과거 표본 수와 성공률, 최근 1·3경기 비율, 구종군 비율 |
| 새 파생 | 14 | 누적 대비 최근 차이, 카운트, 손 유형 일치, LI·최근 비율·구종 비율 상호작용, 타자 성공률 축소 추정 |
| 합계 | 55 | `src/features.py`의 `main55_fixed`가 실제 학습 목록의 기준 |

제공된 47개 입력 중 다음 6개는 제외했다.

| 제외 피처 | 이유 |
| --- | --- |
| `run_total_before` | 두 팀 득점으로 재구성 가능 |
| `score_diff_home` | 두 팀 득점으로 재구성 가능 |
| `asof_pitcher_pitchmix_n` | `asof_pitcher_n`과 동일 |
| `asof_pitcher_strike_rate` | `1 - asof_pitcher_ball_rate`로 재구성 가능 |
| `asof_pitcher_fastball_rate` | 다른 구종군 비율로 재구성 가능 |
| `asof_pitcher_prev5_game_success_rate` | 복원 실험에서 2024 Brier 악화 |

최종 모델은 제공 47개에 새 피처 14개를 무조건 더한 61개 구성이 아니다. 제공 피처 41개를 선택하고 새 파생 14개를 더한 55개 구성이다.

## 핵심 검증 결과

2024 검증에서 제공 47개를 그대로 사용했을 때 RandomForest의 BSS는 416.18, CatBoost의 BSS는 662.86이었다. 이 비교는 모델 변경 효과를 분리한다. 같은 CatBoost에서 최종 55개는 724.76으로 개선됐다.

시즌 순서 검증의 평균 Brier는 다음과 같다. Brier는 낮을수록 좋다.

| 구성 | 피처 수 | 2022 | 2023 | 2024 | 3개 시즌 평균 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 제공 피처 전체 | 47 | 0.243461 | 0.253242 | 0.248151 | 0.248285 |
| 선택 제공 피처 | 41 | 0.243488 | 0.253075 | 0.248153 | 0.248239 |
| 제공 47 + 새 파생 | 61 | 0.243402 | 0.252744 | 0.248026 | 0.248057 |
| 선택 제공 41 + 새 파생 | 55 | 0.243405 | 0.252779 | 0.247996 | 0.248060 |

61개와 55개의 평균 Brier 차이는 약 0.0000028로 실질적으로 동률이었다. 같은 수준의 성능에서 중복 피처를 줄일 수 있어 55개를 최종 선택했다. 모든 EDA 후보를 합친 81개 구성은 2024 BSS가 714.99로 최종 55개보다 낮았으므로 사용하지 않았다.

확률 보정은 테스트 데이터의 성공률이나 분포를 사용하지 않았다. 2022~2024의 시간 순서 검증에서 이전 시즌의 예측 편향만 누적해 최종 이동값 `-0.010462037831246366`을 고정했다.

상세 수치는 [`results/`](results/)에 저장되어 있다.

데이콘 제출 화면에 입력할 문구는 [`SUBMISSION_MEMO.md`](SUBMISSION_MEMO.md)에 정리했다.

## 폴더 구성

```text
submission_허원준/
├── catboost_feature_ablation.ipynb  # 팀원이 실행할 Colab 노트북
├── run.py                    # 로컬/Colab 공통 실행 명령
├── requirements-colab.txt    # Colab 설치 목록
├── src/
│   ├── features.py           # 피처 출처, 선택 목록, 새 파생 계산
│   └── pipeline.py           # 검증, 최종 학습, ZIP 생성·실행 확인
└── results/                  # 이미 완료된 비교 결과 요약
```

생성되는 모델, 패키지, `submit.zip`은 `output/`에 저장되며 Git에는 포함하지 않는다.

## 로컬 실행

저장소 루트에서 실행한다.

```bash
python submission_허원준/run.py build --data-dir /path/to/data
python submission_허원준/run.py validate --data-dir /path/to/data
```

피처 비교를 다시 실행하려면 다음처럼 검증 시즌과 실험을 지정한다.

```bash
python submission_허원준/run.py experiment \
  --data-dir /path/to/data \
  --validation-seasons 2022 2023 2024 \
  --experiments raw47_catboost selected_provided41_only main55_fixed
```

검증 시즌보다 앞선 시즌만 학습에 사용하므로 미래 시즌 타깃이 학습에 섞이지 않는다.

## 제출 규정 관련 확인

- 제공된 학습·테스트 파일 외 외부 데이터나 외부 API를 사용하지 않는다.
- 테스트 전체 행을 집계해 새 피처를 만들지 않는다.
- 타깃을 사용하는 값은 학습 데이터 평균과 이전 검증 시즌의 예측 편향뿐이다.
- 최종 제출 패키지는 `script.py`, `features.py`, `requirements.txt`, `model/`만 포함한다.
