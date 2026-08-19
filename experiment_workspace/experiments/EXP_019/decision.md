# EXP_019 decision

- decision: `adopt`
- selected variant: `batter_team_cat`
- based on run: `RUN_001`
- comparison basis: `EXP_018`
- reference variant: `d6_i300_control`
- decided at: `2026-08-17T16:57:53.453003+00:00`

## Ablation

main55+count와 CatBoost 설정을 고정하고 pitcher/batter/team/hand ID를 한 종류씩만 native categorical로 추가

## Result

- selected Brier: `0.2478308423`
- delta Brier vs control: `-4.465e-05`
- competition score: `791.0447010075`

## Reason

batter_team_id만 범주형으로 추가한 후보가 Brier 0.2478308423, BSS 791.045로 control보다 0.000044650 개선해 새 최고였다. 양 팀 범주형보다도 근소하게 우수했다.
