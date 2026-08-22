"""exp_035 -- add 15 pitch_type_group-conditioned trackman physical
columns on top of exp_030's exact 105 features, single CatBoost (exp_030
hyperparams), 2019-2023/2024 holdout. See
experiments/exp_035_trackman_group_profile.md.
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import pandas as pd

from exp030_baseline import ALL_FEATURES, BASE_FEATURES, DATA_DIR, TARGET, TRACKMAN_SHRINK_K, _recent_seasons_df
from features import CAT_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from metrics import official_score
from model_factory import fit_catboost
from season_state_features import attach_season_state_features, build_season_baselines, fit_season_state_priors
from trackman_pitcher_features import (
    GROUP_TRACKMAN_COLS, GROUP_VALUES, attach_pitcher_physical_features, attach_pitcher_physical_features_by_group,
    build_pitcher_physical_asof_tables, build_pitcher_physical_asof_tables_by_group, load_pitcher_mapping,
)


def main():
    print("=" * 80)
    print("0. 데이터/피처 구축: exp_030의 105개 + 신규 구종군별 트랙맨 15개")
    print("=" * 80)
    train = pd.read_csv(f"{DATA_DIR}/train.csv", encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(f"{DATA_DIR}/processed/trackman_clean.csv", encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables_pooled = build_pitcher_physical_asof_tables(trackman_clean)
    tables_group = build_pitcher_physical_asof_tables_by_group(trackman_clean)

    is_val = train["season"] == 2024
    train_only = train.loc[~is_val]
    val_priors = fit_shrinkage_priors(_recent_seasons_df(train_only))
    train_shrunk_val = apply_shrinkage(train, val_priors)
    df_val = attach_pitcher_physical_features(train_shrunk_val, tables_pooled, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    df_val = attach_pitcher_physical_features_by_group(df_val, tables_group, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    pitcher_baselines = build_season_baselines(train_only, "pitcher")
    pitcher_priors = fit_season_state_priors(train_only, "pitcher")
    df_val = attach_season_state_features(df_val, pitcher_baselines, pitcher_priors, "pitcher")
    batter_baselines = build_season_baselines(train_only, "batter")
    batter_priors = fit_season_state_priors(train_only, "batter")
    df_val = attach_season_state_features(df_val, batter_baselines, batter_priors, "batter")

    feature_list = ALL_FEATURES + GROUP_TRACKMAN_COLS
    assert len(feature_list) == 105 + 15, len(feature_list)
    X_train, y_train = df_val.loc[~is_val, feature_list], df_val.loc[~is_val, TARGET]
    X_val, y_val = df_val.loc[is_val, feature_list], df_val.loc[is_val, TARGET]
    print(f"train={X_train.shape}, val={X_val.shape}, n_features={len(feature_list)} (105 + {len(GROUP_TRACKMAN_COLS)} 신규)")
    print(f"신규 컬럼: {GROUP_TRACKMAN_COLS}")

    print()
    print("=" * 80)
    print("1. baseline: exp_030의 105개 피처만 (비교 기준)")
    print("=" * 80)
    res_base = fit_catboost(X_train[ALL_FEATURES], y_train, X_val[ALL_FEATURES], y_val, CAT_COLS, seed=42, name="baseline-105")
    base_brier, base_score = official_score(res_base.val_pred, y_val)
    print(f"[105피처 raw] Brier={base_brier:.6f} | score={base_score:.2f} (best_iter={res_base.extra['best_iteration']})")

    print()
    print("=" * 80)
    print("2. 105 + 구종군별 트랙맨 15개")
    print("=" * 80)
    res_group = fit_catboost(X_train, y_train, X_val, y_val, CAT_COLS, seed=42, name="105+group15")
    group_brier, group_score = official_score(res_group.val_pred, y_val)
    print(f"[120피처 raw] Brier={group_brier:.6f} | score={group_score:.2f} (best_iter={res_group.extra['best_iteration']})")

    print()
    print("=" * 80)
    print("결과 요약 (raw, 보정 전 -- 두 변형 다 동일 처리라 직접 비교 유효)")
    print("=" * 80)
    print(f"  105피처(baseline)     = {base_score:.2f}")
    print(f"  105+구종군15(exp_035) = {group_score:.2f}")
    print(f"  Δ = {group_score - base_score:+.2f}")
    print("완료.")


if __name__ == "__main__":
    main()
