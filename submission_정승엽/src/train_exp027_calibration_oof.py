"""exp_027 calibration prep -- 5-fold cross-fit OOF on 2019-2023 with the
NEW (season-state-augmented) feature set, for both seeds {42, 1}, same
protocol as train_exp018_calibration.py / train_exp019_calibration_blend.py
but using ALL_FEATURES from train_exp027_final.py instead of
TRACKMAN_FEATURE_SET. Needed because the underlying model changed
(exp_027 season-state features), so exp_018/019's cached OOF (fit on the
old 89-feature model) is not valid for calibrating this new model.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

from features import CAT_COLS, DERIVED_COLS, SHRUNK_COLS, POST_SHRINKAGE_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from metrics import official_score
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    load_pitcher_mapping,
)
from season_state_features import build_season_baselines, fit_season_state_priors, attach_season_state_features, season_state_cols

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
N_FOLDS = 5
SEEDS = [42, 1]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS
SEASON_STATE_COLS = season_state_cols("pitcher") + season_state_cols("batter")
ALL_FEATURES = TRACKMAN_FEATURE_SET + SEASON_STATE_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축 (2019-2023)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    is_val = train["season"] == 2024
    train_only = train.loc[~is_val]
    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, val_priors_recent)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    pitcher_baselines = build_season_baselines(train_only, "pitcher")
    batter_baselines = build_season_baselines(train_only, "batter")
    pitcher_priors = fit_season_state_priors(train_only, "pitcher")
    batter_priors = fit_season_state_priors(train_only, "batter")
    train_full_feat = attach_season_state_features(train_shrunk, pitcher_baselines, pitcher_priors, "pitcher")
    train_full_feat = attach_season_state_features(train_full_feat, batter_baselines, batter_priors, "batter")

    train_2319 = train_full_feat.loc[~is_val, ALL_FEATURES + [TARGET]].reset_index(drop=True)
    X_2319 = train_2319[ALL_FEATURES]
    y_2319 = train_2319[TARGET].to_numpy()
    print(f"2019-2023 n={len(X_2319)}, features={len(ALL_FEATURES)}")

    for seed in SEEDS:
        cache_path = f"./output/exp027_oof_cache_seed{seed}.npz"
        if os.path.exists(cache_path):
            print(f"이미 존재: {cache_path} (재사용)")
            continue
        cb_params = dict(
            iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=seed, thread_count=-1, verbose=False,
        )
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        oof_pred = np.zeros(len(train_2319))
        t0 = time.time()
        for fold, (tr_idx, ho_idx) in enumerate(kf.split(train_2319)):
            X_tr, y_tr = X_2319.iloc[tr_idx], y_2319[tr_idx]
            X_ho = X_2319.iloc[ho_idx]
            train_pool = cb.Pool(X_tr, y_tr, cat_features=CAT_COLS)
            clf = cb.CatBoostClassifier(**cb_params)
            clf.fit(train_pool, verbose=False)
            oof_pred[ho_idx] = clf.predict_proba(X_ho)[:, 1]
            print(f"  [seed={seed}] fold {fold+1}/{N_FOLDS} 완료 ({time.time()-t0:.1f}s 누적)")
        oof_brier, oof_score = official_score(oof_pred, y_2319)
        print(f"[seed={seed}] OOF(2019-2023): Brier={oof_brier:.6f}, score={oof_score:.2f}")
        os.makedirs("./output", exist_ok=True)
        np.savez(cache_path, pred=oof_pred, y=y_2319)
        print(f"저장: {cache_path}")

    print("\n완료.")


if __name__ == "__main__":
    main()
