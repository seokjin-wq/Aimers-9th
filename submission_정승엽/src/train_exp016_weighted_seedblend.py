"""exp_016 -- exp_010 only tried CUMULATIVE, UNIFORM averaging of its 5
seeds in a fixed order (1, then avg(1,2), then avg(1,2,3), ...) and found
the 2-seed prefix {42,1} beat every other prefix, including the full
5-seed uniform average. That leaves open whether a properly WEIGHTED
combination search over all 5 seeds (not restricted to uniform prefixes)
finds something better than the 749.58 champion -- e.g. maybe seed 7
deserves a small positive weight even though it hurt the cumulative
average, or maybe a non-uniform 2-or-3-seed weighting beats the naive
50/50 average of {42,1}.

Caveat (documented, not hidden): searching weights over 5 candidates on
the SAME single 2024 validation split risks fitting noise in that split
rather than a real effect -- exp_010 already flagged this same risk for
its own 2-seed finding. This experiment is exploratory; any winner here
is weaker evidence than exp_010's original finding and should be treated
accordingly.
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

from ensemble import coarse_fine_blend_search
from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRUNK_COLS,
    POST_SHRINKAGE_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)
from metrics import official_score
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
SEEDS = [42, 1, 7, 123, 2024]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축")
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

    X_train = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET]

    print()
    print("=" * 80)
    print(f"1. {len(SEEDS)}개 시드 재학습 (exp_010과 동일, 예측값 저장)")
    print("=" * 80)
    pred_dict = {}
    for seed in SEEDS:
        cb_params = dict(
            iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=seed, thread_count=-1, verbose=False,
        )
        t = time.time()
        train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
        val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
        clf = cb.CatBoostClassifier(**cb_params)
        clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        pred = clf.predict_proba(X_val)[:, 1]
        brier, score = official_score(pred, y_val)
        pred_dict[f"seed{seed}"] = pred
        print(f"[seed={seed}] Brier={brier:.6f} | score={score:.2f} | {time.time()-t:.1f}s")

    print()
    print("=" * 80)
    print("2. 가중 블렌드 탐색 (5-way 전체, validation에서만)")
    print("=" * 80)
    candidates = list(pred_dict.keys())
    t = time.time()
    best_w, best_brier, best_score = coarse_fine_blend_search(pred_dict, y_val.to_numpy(), candidates)
    print(f"[5-way 가중 블렌드 최적] weights={ {k: round(v,3) for k,v in best_w.items()} } | Brier={best_brier:.6f} | score={best_score:.2f} | {time.time()-t:.1f}s")

    uniform_5 = sum(pred_dict.values()) / len(SEEDS)
    _, score_uniform5 = official_score(uniform_5, y_val)
    two_seed = (pred_dict["seed42"] + pred_dict["seed1"]) / 2
    _, score_2seed = official_score(two_seed, y_val)

    print()
    print("=" * 80)
    print("요약")
    print("=" * 80)
    print(f"5시드 균등평균: score={score_uniform5:.2f}")
    print(f"2시드(42+1) 균등평균 (exp_010 챔피언): score={score_2seed:.2f}")
    print(f"5-way 가중 블렌드 최적: score={best_score:.2f} | Δ vs exp_010 챔피언={best_score-score_2seed:+.2f}")
    print("\n완료.")


if __name__ == "__main__":
    main()
