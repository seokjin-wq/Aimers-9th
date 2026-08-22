# Trackman 정제 + train 매칭 키 생성 (Phase 1)

`src/trackman_clean.py`의 `clean_trackman()`/`build_train_match_keys()`를
실행해 원본 `data/trackman_history.csv`(1,793,078행×30컬럼)와
`data/train.csv`(1,475,092행×49컬럼)는 그대로 둔 채, 매핑 재구성(Phase 2)
준비용 정제 결과를 새 파일로 생성한다. 실행 코드는
[`run_clean.py`](run_clean.py)(재실행: `python reports/trackman_clean/run_clean.py`,
실행 로그 원본은 [`clean_run_log.txt`](clean_run_log.txt)). 이 문서의
모든 수치는 그 로그에서 그대로 가져왔다 — 추정치는 없음.

원본 `trackman_history.csv`를 남겨둔 이유: 이후 별도 실험으로 원본 값
기반 코사인 유사도 매칭을 다시 시도할 계획이 있어서다(사용자 요청).

---

## 1. 구종 라벨 정제 (`tagged_pitch_type_clean` / `auto_pitch_type_clean`)

**목적**: `tagged_pitch_type`/`auto_pitch_type`의 대소문자·오탈자 흔들림을
정규화하되, 원본 컬럼과 `pitch_type_group`(기본 분류 축)은 그대로 보존한다.

**방법**: 컬럼별 `value_counts()`를 직접 확인해(추정 없음) 같은 뜻의 변형을
그 컬럼 내 다수 표기로 통일하는 매핑 딕셔너리 작성. 두 컬럼은 서로 다른
원천 시스템(수동 태깅 vs 자동 분류)이라 다수 표기가 컬럼마다 다를 수
있어(실제로 다름), 컬럼별로 별도 매핑을 둠.

**결과**:
- `tagged_pitch_type`: 17종 → 13종. 병합: `Changeup`(225건)→`ChangeUp`
  (170,859건이 다수), `SInker`(38건)→`Sinker`, `Undefined#`(1건)/
  `Undefind`(1건)→`Undefined`.
- `auto_pitch_type`: 11종 → 10종. 병합: `ChangeUp`(90,324건)→`Changeup`
  (185,311건이 다수) — tagged와 반대 방향으로 다수 표기가 갈렸다(실제
  값 기준, 추정 아님).
- `Fastball`/`Four-Seam`(auto_pitch_type)은 오탈자가 아니라 2022년부터
  자동분류 시스템이 패스트볼을 세분화하기 시작한 실제 시즌 트렌드
  (`reports/eda_trackman/README.md` §5)이므로 **병합하지 않고 그대로
  유지**했다.

**시사점**: 세분류 구종 컬럼이 필요한 후속 실험이 있으면 `_clean` 컬럼을
바로 쓸 수 있다. 기본 분류 축은 여전히 결측 0건인 `pitch_type_group`.

---

## 2. 팀 tier / 프랜차이즈 정체성 (trackman 쪽)

**목적**: `pitcher_team`/`batter_team`(26개 코드)을 1군/2군/특수로
나누고, 개명된 팀(리브랜딩)까지 같은 프랜차이즈로 묶는다.

**방법**: `MIN_` 접두사 → `minor`, `KBO_`/`ACE_` 접두사 → `other`,
나머지 → `major`(순수 문자열 규칙, 도메인 지식 불필요). 이어서 시즌별
`SK_WYV`/`SSG_LAN`, `MIN_SKW`/`MIN_SSG` 등장 여부를 교차표로 확인.

**결과**:
- tier 분포(pitcher_team_tier): major 1,189,400 / minor 576,848 /
  other 26,830.
- **`SK_WYV`는 2019~2020에만, `SSG_LAN`은 2021~2024에만 등장**(교차표
  상 두 시즌대가 전혀 겹치지 않음) — 실제 SK 와이번스 → SSG 랜더스
  구단 매각·개명(2021년)과 정확히 일치. `MIN_SKW`/`MIN_SSG`도 동일
  패턴. 이를 근거로 `pitcher_team_franchise` 컬럼에서 두 코드를 하나의
  프랜차이즈로 묶었다(KBO 도메인 지식 기반 — 공식 문서 근거 아님,
  `CLAUDE.md` Ground Truth priority 5).
- 26개 코드가 10개 프랜차이즈(major+minor 쌍) + 3개 특수 코드
  (`KBO_ARM`, `KBO_POL`, `ACE_MEX`) + `MIN_HAW`(major 짝을 못 찾은
  소표본 코드, 292건)로 정리됨. major↔minor 짝짓기는 접두사만으로는
  안 풀림(예: `DOO_BEA`↔`MIN_DOO`는 도시 약자로 짝지어지는데
  `KIW_HER`↔`MIN_HER`는 마스코트 약자로 짝지어짐 — 소스 시스템 명명
  규칙이 일관적이지 않음) → 수작업 KBO 지식 기반 딕셔너리로 처리,
  가설로 표시.

**시사점**: tier 컬럼(구조적 규칙, 확실)과 franchise 컬럼(도메인 지식
기반, 가설)을 분리해 신뢰도를 구분했다. Phase 2에서 tier는 train의
`game_type`과 바로 교차검증 가능.

---

## 3. train 쪽 team tier — `pitcher_team_id`는 tier가 아니라 조직 ID였다

**목적**: trackman의 team tier와 비교 가능한 축을 train 쪽에서도 만든다.

**방법**: 원래 계획은 "각 `pitcher_team_id`(13개 숫자 코드)가
`game_type='R'`으로 나타나는 비율"로 major/minor를 경험적으로 라벨링하는
것이었다. 그런데 실제 교차표를 보니 이 가정 자체가 틀렸다는 게 드러나서
방법을 수정했다.

**결과** (`pitcher_team_id` × `game_type` 교차표, `clean_run_log.txt` 참고):
- 10개 코드(12,13,14,15,16,17,18,19,20,21)는 모두 130,574~208,662행의
  큰 표본이고, **R과 F 행이 둘 다 존재**한다(R 비율 61.9%~96.9%로
  코드마다 다름).
- 3개 코드(22,23,25)는 각각 676/4,437/292행의 작은 표본이고 **R 행이
  0건, 전부 F**다.

즉 train의 `pitcher_team_id`는 major/minor를 나누는 축이 아니라
**KBO 조직(구단) 식별자**이고(10개 = 10개 실제 프랜차이즈로 보임, 3개는
1군이 없는 특수 조직 — 상무/경찰청 등 퓨처스 전용 군 팀일 가능성이
높으나 공식 문서 근거는 없어 가설로만 표시), **major/minor 구분은 이미
`game_type`(R/F) 컬럼이 행 단위로 직접 갖고 있다.** trackman처럼 팀
코드 자체가 major/minor로 나뉘어 있는 게 아니었다.

**시사점**: 당초 계획의 "R-rate 기반 팀 tier 추정" 단계는 불필요해졌다
— `build_train_match_keys()`는 `team_tier = game_type.map({'R':'major',
'F':'minor'})`로 단순화했다(더 직접적이고 근거도 확실함). `pitcher_team_id`
13개는 대신 franchise 축에 가깝다는 것을 확인했으므로, 필요하면 나중에
trackman의 `pitcher_team_franchise`(10개+특수코드)와 개수를 맞춰 비교할
후보가 된다(이번 범위에는 포함하지 않음).

---

## 4. 카운트 규칙 위반 행 — 삭제하지 않고 플래그만

**목적**: `balls_before`/`strikes_before`/`outs_before`가 야구 규칙상
불가능한 값을 가진 행을 찾되, 곧바로 지우지 않고 표시만 한다.

**결과**:
- trackman: 97행(0.0054%) 플래그됨. `outs_before`가 3(83건)/4(12건)인
  경우가 대부분(95/97) — 유효 범위(0~2)를 벗어난 원인의 대다수.
  `balls_before`=4인 행 1건, `strikes_before`=3인 행 1건도 포함.
- 27명의 서로 다른 `pitcher_trackman_id`에 걸쳐 있고, **2022년 4월에
  73건이 몰려 있다**(전체 97건 중 75%). 나머지도 2022~2023년의 특정
  월들에 소수씩 분포.
- **train.csv는 동일 기준으로 위반 행이 0건**(1,475,092행 전수 확인).

**시사점**: train 쪽엔 이런 위반 행이 아예 없으므로, 이 97건이 실제로
대응되는 train 행을 찾을 가능성은 낮아 보인다(반쪽 이닝 종료 후 남는
후속 이벤트 로그의 잔재일 가능성 — 가설). 다만 계획대로 지금 단계에서
지우지 않고 `is_illegal_count` 플래그만 남겨, Phase 2 매칭 단계에서
실제로 대응 후보가 없는지 확인한 뒤 최종적으로 제외 여부를 결정한다.

---

## 5. `game_date` 파싱 + situational_key

**목적**: 시즌별 포맷이 다른 `game_date`를 안전하게 파싱하고, 매칭용
상황 키(`situational_key`/`count_state_code`)를 만든다.

**결과**:
- 시즌별 분기 파싱(2019-2021: `%m/%d/%Y`, 2022-2024: `%Y-%m-%d`) 적용
  결과 파싱 실패(NaT) 0건, 파싱된 월과 공식 `game_month` 일치율
  100.0000%(`reports/eda_trackman/README.md` §2와 동일하게 재확인됨).
- `situational_key`(season/game_month/game_dayofweek/inning/
  top_bottom/count_state_code 조합) 기준, 같은 투수(`pitcher_trackman_id`)
  안에서 이 키가 중복되는 행의 비율이 **25.66%** — 즉 4행 중 1행 정도는
  같은 투수·같은 시즌월요일·같은 카운트 상황이 한 번 이상 더 있다는
  뜻이다.

**시사점**: Phase 2의 투구(행) 단위 매칭에서, situational_key만으로는
전체 행의 약 1/4을 유일하게 특정할 수 없다는 것을 미리 확인했다 — 계획된
행 순서 정합(오름차순 위치 매칭) 단계가 형식적 보험이 아니라 실제로
필요한 단계임이 정량적으로 뒷받침됨.

---

## 산출물

- `data/processed/trackman_clean.csv` (1,793,078행 × 45컬럼)
- `data/processed/train_match_keys.csv` (1,475,092행 × 22컬럼)
- 원본 `data/trackman_history.csv`, `data/train.csv`는 재로드 shape
  비교로 미변경 확인함(`clean_run_log.txt` 마지막 절).

## 다음 단계

Phase 2(`src/trackman_id_mapping.py`, 아직 미착수) — 투수 단위 시즌
지문 매칭 → 투구(행) 단위 situational_key + 순서 정합 매칭. §3의 발견
(train `pitcher_team_id`가 조직 ID라는 것)과 §5의 발견(situational_key
단독으로는 25.66%가 모호)을 그대로 반영해서 설계한다.
