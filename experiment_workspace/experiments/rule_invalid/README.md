# Rule-invalid experiment quarantine

이 폴더는 데이콘의 평가 행 독립성 규칙을 위반하는 것으로 사후 판정된 실험
기록을 보존한다.

## 격리 범위

- `EXP_034`~`EXP_053`, 총 20개 실험
- 최초 위반 계보: `EXP_034`
- 최고 기록이지만 제출 불가: `EXP_053`, 로컬 BSS `1303.3916`

## 격리 이유

이 실험들은 2024 validation fold의 다른 행을 이용해 `diff`, `lag`, `rolling`,
EWMA 또는 선수·팀·경기 집계를 만들었다. 검증 행을 실제 test 행과 동일한
독립 예측 대상으로 보면 데이콘 규칙을 위반한다.

## 보존 원칙

- 폴더 내부의 당시 설정, 결과, 판단, history는 수정하지 않는다.
- 성능 근거나 제출 후보로 사용하지 않는다.
- 활성 `experiments/index.csv`에 포함하지 않는다.
- `manifest.csv`를 격리 판정의 기준으로 사용한다.
- 새 실험 번호에 과거 번호를 재사용하지 않는다. 다음 실험은 `EXP_054`다.

공식 규칙과 상세 판정은
[`../../docs/COMPETITION_RULES.md`](../../docs/COMPETITION_RULES.md)를 참고한다.
