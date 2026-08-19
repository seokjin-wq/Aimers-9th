# LG Aimers 9기 평가 데이터 행 독립성 규칙

대회의 문제 정의와 코드 제출 환경은
[`COMPETITION_OVERVIEW.md`](COMPETITION_OVERVIEW.md)를 참고한다.
점수 산식과 정확한 제출 구조는
[`COMPETITION_EVALUATION.md`](COMPETITION_EVALUATION.md)를 참고한다.
팀 구성, 외부 데이터·API, 모델 라이선스 및 사후 코드 제출 규칙은
[`COMPETITION_GENERAL_RULES.md`](COMPETITION_GENERAL_RULES.md)를 참고한다.

## 공식 근거

- 데이콘 공지: [평가 데이터(test.csv) 행 독립 추론 관련 안내](https://dacon.io/competitions/official/236743/talkboard/417123?page=1&dtype=recent)
- 확인일: 2026-08-18 (Asia/Seoul)
- 이 문서는 공지를 실험·제출 코드 관점에서 요약한 내부 체크리스트다.
  공지와 이 문서가 다르면 데이콘 원문을 우선한다.

## 절대 원칙

평가 데이터의 각 행은 독립적으로 예측해야 한다.

행 `A`의 예측은 다음 정보에만 의존할 수 있다.

1. 행 `A` 자체에 포함된 입력 변수
2. 행 `A`의 변수만으로 계산한 파생변수
3. 주최 측 공식 학습 데이터
4. 공식 학습 데이터만으로 미리 계산한 통계·매핑·모델·파생변수

이를 식으로 쓰면 다음과 같다.

```text
prediction(A) = f(official_train, A)
```

`test.csv`의 다른 행 `B`가 함수 입력에 들어가면 안 된다. `B`가 시간상 더
과거처럼 보이는 경우도 동일하다.

## 금지 사항

- 평가 데이터 행끼리 `groupby`, `diff`, `shift`, `lag` 수행
- 평가 데이터 행끼리 `rolling`, expanding, EWMA 수행
- 평가 데이터 전체의 평균·표준편차·분포·빈도·순위 사용
- 평가 데이터에서 선수·팀·월·경기·타석 단위 통계 생성
- 앞선 평가 행의 입력이나 예측을 다음 평가 행에 전달
- 평가 데이터에서 계산한 값으로 확률 scale·shift·calibration 수행
- 시점상 과거로 보인다는 이유로 다른 평가 행을 현재 행에 사용

## 허용 사항

- 한 행 안의 카운트, 주자, 이닝, 손잡이 등으로 만드는 행 단위 연산
- 공식 학습 데이터에서만 계산해 모델과 함께 저장한 통계
- 공식 학습 데이터만으로 학습한 인코더, 결측 대체값, calibration
- 현재 평가 행의 `asof_*` 값 자체를 그대로 사용하거나 그 행 안에서 변환
- 현재 행과 공식 학습 데이터의 사전 저장 값만 비교해 만드는 피처

마지막 항목도 다른 평가 행을 참조하지 않아야 한다.

## 필수 독립성 테스트

모든 최종 후보는 아래 두 예측이 부동소수점 허용 오차 안에서 같아야 한다.

```python
p_single = predict(test.loc[[row]])
p_batch = predict(test).loc[row]
assert abs(p_single - p_batch) <= 1e-12
```

추가로 다음 순열·중복 불변성도 검사한다.

- test 행 순서를 섞어도 각 `row_id`의 예측이 동일하다.
- 다른 test 행을 추가하거나 제거해도 대상 행의 예측이 동일하다.
- 같은 test 행을 중복해도 원래 행의 예측이 동일하다.
- 한 행씩 반복 호출한 결과와 batch 호출 결과가 동일하다.

## 현재 워크스페이스 판정

- `EXP_034`~`EXP_053`은 평가 fold 내부의 다른 행을 이용한 순차·rolling
  피처를 포함하므로 `experiments/rule_invalid/`로 격리했으며 제출 후보로
  사용할 수 없다.
- BSS `1303.3916`을 기록한 `EXP_053`의
  `batter_team_recent200_middle`도 평가 행끼리 팀 통계를 만들기 때문에
  규칙 위반이다.
- 규칙 준수 실험 중 최고 후보는 `EXP_130`의 BSS `945.4411`이다. 공식 학습
  데이터로만 만든 2024 OOT count 보정과 count별 계절 추세를 사용한다.
- `output/final/submit.zip`은 `EXP_130`을 2019~2024 전체로 재학습한 패키지로
  덮어썼다. test 행에 대해서는 저장된 공식 학습 통계를 현재 행의
  `balls_before`, `strikes_before`, 선수별 as-of 값에 조회만 한다.
- 실제 ZIP 독립 실행에서 단일행, 순서 변경, 다른 행 추가, 동일 피처 복제의
  예측 최대 차이는 `1.11e-16`으로 허용 기준 `1e-12`를 통과했다.

## 앞으로의 실험 게이트

새 실험은 실행 전에 다음 항목을 확인한다.

- [ ] 피처가 `official_train + 현재 한 행`만으로 계산되는가?
- [ ] 평가 frame에 대한 `groupby/diff/shift/rolling/EWMA`가 없는가?
- [ ] test 분포로 보정하거나 통계를 계산하지 않는가?
- [ ] 단일 행 대 batch 예측 동일성 테스트가 있는가?
- [ ] 순서·추가·제거·중복 불변성 테스트를 통과하는가?
- [ ] 최종 ZIP을 독립 실행해 같은 테스트를 통과하는가?

하나라도 충족하지 못하면 점수가 높더라도 채택하거나 제출하지 않는다.
