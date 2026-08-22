# TrackMan 투수 ID 매칭 — E00/E11

`train.csv`의 익명 `pitcher_id`와 `trackman_history.csv`의 익명
`pitcher_trackman_id`를 타깃 없이 연결하는 두 방법의 코드와 재현 결과다.

## 결과

| 항목 | E00 | E11 |
| --- | ---: | ---: |
| 대회 투수 후보 | 792명 | 792명 |
| 승인된 투수 | 751명 | 777명 |
| 투수 커버리지 | 94.82% | 98.11% |
| 고유 TrackMan ID | 751개 | 777개 |
| 중복 배정 | 0건 | 0건 |
| high / medium | 467 / 284명 | 609 / 168명 |

두 방법이 모두 승인한 투수는 749명이다. 그중 748명은 같은 TrackMan 투수를
선택해 쌍 일치율이 99.87%이고, 1명만 서로 다른 후보를 선택했다. E00만 승인한
투수는 2명, E11만 승인한 투수는 28명이다.

## E00 — 9개 상황 임베딩 cosine

각 투수를 아래 9개 상황 조합별 투구 수 벡터로 표현한다.

1. `season`
2. `game_month`
3. `game_dayofweek`
4. `inning`
5. `top_bottom`
6. `balls_before`
7. `strikes_before`
8. `outs_before`
9. `pitcher_hand`

벡터를 L2 정규화한 뒤 cosine 유사도를 구한다. 투수 손이 같은 후보만 비교하며
다음 조건을 모두 만족할 때 승인한다.

- cosine `>= 0.20`
- 1위와 2위의 차이 `>= 0.05`
- 대회 투수→TrackMan 투수와 TrackMan 투수→대회 투수가 서로 top-1

## E11 — 반복 행 우선 매칭

E00의 투수별 집계 대신 양쪽 데이터에 단 한 번씩 나타나는 세부 상황 행을 먼저
찾는다. E00의 9개 상황에 `batter_hand`를 추가하고, 기본 레인에서는 대회의
`game_type`과 TrackMan 팀 코드에서 만든 1군·2군 tier도 사용한다.

1. 양쪽에서 조합이 유일한 행끼리 직접 연결한다.
2. 대회 투수별 TrackMan ID 투표를 집계한다.
3. 최소 3표와 dominance 0.70 이상인 high/medium 후보를 승인한다.
4. 같은 TrackMan ID가 여러 투수에 배정되면 더 강한 후보 하나만 확정한다.
5. 확정된 양쪽 투수를 후보군에서 제외하고 최대 10라운드 반복한다.
6. tier 미사용 레인, 결정적 80/20 조합 분할, holdout 투표를 감사 정보로 붙인다.

정승엽 v3 원본 매핑은 778명이지만 동일 TrackMan ID 중복 배정이 2건 있었다.
여기 포함한 E11은 이 충돌을 라운드마다 해소하고 남은 후보를 다시 탐색한 결과로,
777명 모두 one-to-one이다.

## cutoff와 사용 범위

- 기본 cutoff는 2025이며 2019~2024 행만 사용한다.
- 두 방법 모두 `control_success`를 읽지 않는다.
- 과거 시즌 검증 시에도 반드시 목표 시즌보다 앞선 TrackMan 행만 사용한다.
- 매칭 커버리지가 높다는 사실만으로 실제 ID 정확도나 모델 점수 개선이 보장되지는 않는다.
- 현재 CatBoost 제출 ZIP에는 이 매칭이나 TrackMan 피처가 자동 포함되지 않는다.

## 실행

저장소 루트에서 실행한다.

```bash
python submission_허원준/run_trackman_linkage.py \
  --data-dir /path/to/data \
  --method both \
  --cutoff-season 2025
```

`--method`는 `both`, `e00`, `e11` 중 하나다. E00 임계값은
`--min-cosine`, `--min-margin`으로 바꿀 수 있다.

## 파일

- `E00_pitcher_mapping.csv`: E00 전체 후보와 승인 근거
- `E00_approved_pitcher_mapping.csv`: E00 승인 751쌍
- `E11_pitcher_mapping.csv`: E11 전체 후보와 교차검증 정보
- `E11_approved_pitcher_mapping.csv`: E11 승인 777쌍
- `E11_rounds.csv`: E11 레인별 반복 라운드 기록
- `summary.json`: 조건, 커버리지, 두 방법의 쌍 일치율

핵심 구현은 `submission_허원준/src/trackman_linkage.py`, 실행 진입점은
`submission_허원준/run_trackman_linkage.py`다.
