# 저장된 CatBoost 검증 결과

이 폴더의 파일은 이미 완료한 시즌 순서 검증 결과를 팀원이 빠르게 확인하기 위한 요약본이다. 최종 제출 파일을 만드는 데 직접 읽히지는 않는다.

- `brier_by_season.csv`: 피처 출처별 추가·제거 실험의 2022~2024 Brier
- `contrast_summary.csv`: 비교 전후 평균 개선 폭과 결론
- `feature_screen_2024.csv`: EDA에서 만든 추가 후보와 제거 후보의 2024 비교
- `calibration_forward_validation.json`: 이전 검증 시즌의 예측 편향만 사용한 확률 보정 검증

Brier는 낮을수록 좋다. `mean_brier_improvement`는 양수일 때 변경 후 구성이 개선된 것이다. 차이가 `0.00001`보다 작으면 실질적으로 동률로 해석했다.
