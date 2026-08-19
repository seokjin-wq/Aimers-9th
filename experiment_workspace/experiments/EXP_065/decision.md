# EXP_065 decision

- decision: `keep_control`
- selected variant: `main69_control`
- based on run: `RUN_001`
- comparison basis: `EXP_064`
- reference variant: `main69_control`
- decided at: `2026-08-18T03:32:53.792259+00:00`

## Ablation

EXP_064와 동일한 네 상황 효과를 leave-one-row-out 대신 leave-one-season-out으로 재계산

## Result

- selected Brier: `0.2475377207`
- delta Brier vs control: `0.0`
- competition score: `908.3839506927`

## Reason

season-OOF로 자기 정답 지문은 제거했지만 모든 상황 교차 효과가 악화되어 CatBoost가 원시 상황을 더 잘 학습한다고 판단
