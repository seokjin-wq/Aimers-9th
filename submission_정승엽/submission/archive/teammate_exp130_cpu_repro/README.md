# 팀원(윤석진) 파이프라인 재현 — EXP_130 (GPU→CPU 대체)

**출처**: `github.com/seokjin-wq/Aimers-9th` (팀 저장소)의
`experiment_workspace`, EXP_130 (`triple_count_trend_ols`, 130개 실험
중 최종 채택 후보). 원본 저장소의 README에 기록된 로컬 검증(2019-2023
학습/2024 홀드아웃) 점수: **945.44** (실제 LB ~1045로 추정, 사용자
확인).

**이 아카이브가 원본과 다른 점**: 이 머신에 GPU가 없어(`nvidia-smi`
없음) triple ensemble의 GPU CatBoost 성분(`task_type="GPU"`,
depth=7, iterations=600)을 **동일 하이퍼파라미터로 CPU 모드로만
바꿔서** 재실행함(`_teammate_repo/experiment_workspace/experiments/
BASELINE_001_main55/models/triple_count_trend_ols_cpuonly.toml`,
`final_cpuonly_repro.toml`). 그 외 피처(78개, `main78_history_
reliability`)/CPU CatBoost/ExtraTrees/count-state 잔차+추세 보정은
전부 원본과 동일. 즉 **원본의 945.44와 정확히 같은 점수를 재현한 게
아니라, 원본 기법이 우리 쪽에서 재현 가능함을 확인한 GPU-미보유
환경용 근사 재현본**임.

**검증 상태**: 팀원 자체 툴(`run.py validate-package`)로 격리 검증
통과 — row-independence 체크(단일행/셔플/행추가/중복피처) 전부 최대
차이 0.0, 확률 범위 정상(5행 샘플 0.389~0.496). 우리 프로젝트의
표준 격리 테스트(별도 임시 폴더에서 새 프로세스로 script.py 실행)는
별도로 하지 않음 — 필요시 요청.

**로컬 검증 점수(holdout 2024)**: 이 CPU 대체판 기준으로는 별도
측정 안 함(빌드 자체가 최종 2019-2024 전체 재학습이라 holdout 재현은
추가 실행 필요 — `run.py study --config ...` 별도 실행 필요, 시간
관계상 생략). 원본 945.44에 가까울 것으로 추정되나 GPU 대체로 인한
편차는 미확인.

**용도**: 우리 팀 파이프라인(exp_027 등)과 별개로, 팀원 코드 자체를
"그대로" 제출해보고 싶을 때 쓸 수 있는 후보. 사용자가 원하면 이걸
그대로 DACON에 제출해 실제 LB 델타를 확인할 수 있음 — 원본 대비
편차가 얼마나 나는지도 함께 알 수 있는 유용한 대조군.

**주의**: 용량이 큼(zip 725MB, 압축 해제 시 더 큼) — 대회 제한
(10GB 압축/32GB 해제)은 통과하지만 우리 자체 챔피언(exp_010 계열,
수 MB)보다 훨씬 큼. `requirements.txt`가 `catboost==1.2.10`만
명시돼 있어 패키지 설치 자체는 가벼움.
