# EXP_035 decision

- decision: `adopt`
- selected variant: `add_all_extensions`
- based on run: `RUN_001`
- comparison basis: `EXP_034`
- reference variant: `entity_recent_all`
- decided at: `2026-08-17T18:32:46.727219+00:00`

## Ablation

main68과 GPU CatBoost를 고정하고 투수 recent20·30·50 및 타자 recent2·8 rolling 피처만 개별·조합 추가

## Result

- selected Brier: `0.2471690782`
- delta Brier vs control: `-0.000117191`
- competition score: `1055.954910941`

## Reason

투수 20·30·50 및 타자 2·8 창 전체 추가가 Brier 0.2471691, BSS 1055.95로 최선
