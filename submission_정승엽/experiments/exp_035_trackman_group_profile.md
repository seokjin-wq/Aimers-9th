# exp_035 — 트랙맨 구종군별 물리특성 프로필

## 실험 개요 (시작 전에 작성)

- **실험 ID**: exp_035
- **날짜 / 담당자**: 2026-08-22 / (Claude, 사용자 요청 — "구종군으로
  나눠서 2025 예측에 활용" 아이디어를 공식 검증된 `pitch_type_group`
  컬럼으로 저위험하게 구현)
- **가설**: 기존 5개 트랙맨 물리특성(rel_speed/spin_rate/induced_vert_
  break/horz_break/extension)은 전체 구종을 뭉뚱그려 평균 낸다.
  `pitch_type_group`(fastball/breaking/offspeed, 공식 검증 91.63%
  일치)별로 나눠서 프로필을 만들면 더 날카로운 신호가 된다 —
  `reports/eda_trackman/README.md` §6에서 그룹별 물리특성이 실제로
  유의미하게 다름을 이미 확인(fastball 142.7km/h·2242rpm, breaking
  127.5km/h·2335rpm, offspeed 130.5km/h·1708rpm).
- **기준(baseline)**: exp_030_repro, score=875.00.
- **이번에 바꾸는 것(한 가지로 한정)**: 기존 105개 피처는 그대로 두고
  `trackman_{rel_speed,spin_rate,induced_vert_break,horz_break,
  extension}_{fastball,breaking,offspeed}_asof` 15개 신규 컬럼만 추가
  (`other`군은 1차 제외). 모델/보정 동결.
- **중요 — 반드시 명시**: 이건 "지금 이 투구가 무슨 구종일 때"의
  조건부 피처가 아니다(test 행 자체엔 미래 구종 정보가 없음) —
  "이 투수는 평소 패스트볼이 얼마나 빠른가" 같은 항상 붙어있는
  별개의 프로필 숫자 여러 개로, 기존 풀링 버전과 같은 프레이밍이다.
- **검증 방법**: season 2019-2023 학습 / 2024 검증. `src/trackman_
  pitcher_features.py`에 새 sibling 함수(`build_pitcher_physical_
  asof_tables_by_group`, `attach_pitcher_physical_features_by_group`)
  추가 — 기존 프로덕션 함수는 안 건드림.
- **누수 위험 검토**: 기존 풀링 버전과 완전히 동일한 메커니즘(순수
  과거 누적, 공식 검증된 `pitch_type_group` 컬럼, cross-row/test-row
  미사용) — 그룹 축만 추가됐을 뿐 누수 위험 논거는 변하지 않음.
  그룹별 league fallback을 그 그룹 자신의 평균으로 계산(풀링
  fallback을 쓰면 그룹 간 실제 차이 때문에 편향됨).
- **위험 신호**: 팀원 파이프라인은 트랙맨을 여러 번 시도했지만
  (EXP_068/074/106/107) 단독으론 이득이어도 최종 이종앙상블+보정에
  얹으면 사라졌음 — 이번엔 exp_030 단독으로 먼저 검증하고, 조립
  단계에서 다시 재검증 예정.

## 결과 (실행 후에 작성)

(실행 후 채움)
