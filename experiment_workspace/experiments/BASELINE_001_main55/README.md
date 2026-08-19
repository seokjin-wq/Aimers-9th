# BASELINE_001_main55

모든 새 실험이 출발하는 현재 기준선입니다.

- source: `Aimers-9th/submission_허원준`
- source commit: `349498b`
- features: `main55` (provided 41 + custom 14)
- ablation model: CatBoost 300 trees
- final model: CatBoost 293 trees
- primary validation: train 2019~2023, hold out 2024
- historical 2022~2023 folds: stability/calibration diagnostics only
- final calibration shift: `-0.010462037831246366`

이 폴더는 기준선 정의만 보관합니다. 개별 실험에서 사용한 실제 설정은
각 `EXP_NNN` 실행 시 `config_resolved.json`과 `RUN_NNN.json`에 별도로
고정됩니다.
