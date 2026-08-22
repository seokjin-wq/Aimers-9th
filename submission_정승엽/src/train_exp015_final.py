"""exp_015 final -- retrain the "2-seed CatBoost average + LightGBM"
blend (catboost_2seed_avg=0.94, lightgbm=0.06, from exp015_run_log.txt)
on the FULL 2019-2024 train.csv, saved as model_type="ensemble" with
3 members (seed42=0.47, seed1=0.47, lightgbm=0.06 -- the 0.94 total
catboost weight split evenly between the two seeds, matching the
uniform 2-seed average exp_010/exp_015 both use). Iteration counts
reused directly from validation runs (deterministic, same seed/data/
params): seed42->696, seed1->632 (exp010_run_log.txt), lightgbm->155
(exp013_run_log.txt, same LightGBM config exp_015 reused).
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import lightgbm as lgb
import catboost as cb
import joblib
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from features import CAT_COLS, DERIVED_COLS, SHRUNK_COLS, POST_SHRINKAGE_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    build_test_time_pitcher_lookup,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
CB_SEED_ITERS = {42: 696, 1: 632}  # exp010_run_log.txt val best_iter+1
LGB_ROUNDS = 155                    # exp013_run_log.txt val best_iter(154)+1
WEIGHTS = {42: 0.47, 1: 0.47, "lightgbm": 0.06}

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    print(f"WEIGHTS={WEIGHTS}")
    print("=" * 80)
    print("1. 전체 2019-2024 데이터 + 피처 구축")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    final_priors = fit_shrinkage_priors(recent_seasons_df(train))
    train_shrunk = apply_shrinkage(train, final_priors)
    train_final = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    X = train_final[ALL_FEATURES]
    y = train_final[TARGET]

    print()
    print("=" * 80)
    print("2. CatBoost 2시드 전체 재학습")
    print("=" * 80)
    train_pool_cb = cb.Pool(X, y, cat_features=CAT_COLS)
    cb_members = {}
    for seed, iters in CB_SEED_ITERS.items():
        cb_params = dict(
            iterations=iters, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=seed, thread_count=-1, verbose=200,
        )
        clf = cb.CatBoostClassifier(**cb_params)
        t = time.time()
        clf.fit(train_pool_cb)
        print(f"[seed={seed}] 완료 :: {time.time() - t:.1f}s")
        cb_members[seed] = clf

    print()
    print("=" * 80)
    print("3. LightGBM 전체 재학습")
    print("=" * 80)
    cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    X_enc = X.copy()
    X_enc[CAT_COLS] = cat_encoder.fit_transform(X_enc[CAT_COLS]).astype(int)
    lgb_params = dict(
        objective="binary", metric="binary_logloss",
        learning_rate=0.03, num_leaves=63,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
        min_child_samples=200, seed=42, num_threads=-1, verbosity=-1,
    )
    train_set = lgb.Dataset(X_enc, label=y.to_numpy(), categorical_feature=CAT_COLS)
    t = time.time()
    booster_lgb = lgb.train(lgb_params, train_set, num_boost_round=LGB_ROUNDS)
    print(f"LightGBM 완료 :: {time.time() - t:.1f}s")

    print()
    print("=" * 80)
    print("4. 저장")
    print("=" * 80)
    os.makedirs(MODEL_DIR, exist_ok=True)

    lookup, league_fallback = build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({lookup.shape})")

    members_meta = []
    for seed, clf in cb_members.items():
        fname = f"catboost_model_seed{seed}.cbm"
        clf.save_model(os.path.join(MODEL_DIR, fname))
        members_meta.append({"type": "catboost", "file": fname, "weight": WEIGHTS[seed]})
    lgb_file = "lgbm_booster.txt"
    booster_lgb.save_model(os.path.join(MODEL_DIR, lgb_file))
    members_meta.append({"type": "lightgbm", "file": lgb_file, "weight": WEIGHTS["lightgbm"]})

    stale = os.path.join(MODEL_DIR, "catboost_model.cbm")
    if os.path.exists(stale):
        os.remove(stale)
        print(f"제거: {stale} (단일모델 아티팩트, ensemble과 혼동 방지)")

    joblib.dump(
        {
            "model_type": "ensemble",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "trackman_cols": TRACKMAN_PITCHER_ASOF_COLS,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
            "trackman_league_fallback": league_fallback,
            "trackman_shrink_k": TRACKMAN_SHRINK_K,
            "members": members_meta,
            "lgb_cat_encoder": cat_encoder,
            "exp_id": "exp_015_seedbag_lgbm_blend",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: model_meta.pkl (members={members_meta})")
    print("\n완료.")


if __name__ == "__main__":
    main()
