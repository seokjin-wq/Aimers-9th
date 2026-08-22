"""exp_009 — CatBoost hyperparameter search on top of the champion
trackman feature set (exp_007's 5-col physical set, `FEATURE_SET`/
`TRACKMAN_SHRINK_K` below -- exp_008's 8-col extension was tried and
rejected, see experiments/exp_008_trackman_extended_physical.md).
Coordinate-wise search around exp_007's carried-over defaults (depth=6,
l2_leaf_reg=3.0, learning_rate=0.03, CatBoost's own defaults for
everything else) -- one hyperparameter changed per config vs the
baseline row, not a full cartesian grid, to keep the run count (and
therefore wall-clock time) manageable while still covering the standard
CatBoost regularization/capacity knobs.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import pandas as pd

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
SEED = 42

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS

BASE_PARAMS = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=SEED, thread_count=-1, verbose=False,
)

CONFIGS = {
    "baseline (exp_007/008과 동일)": {},
    "depth=8": {"depth": 8},
    "depth=4": {"depth": 4},
    "l2_leaf_reg=8": {"l2_leaf_reg": 8.0},
    "l2_leaf_reg=1": {"l2_leaf_reg": 1.0},
    "learning_rate=0.02,iterations=3000": {"learning_rate": 0.02, "iterations": 3000},
    "random_strength=5": {"random_strength": 5.0},
    "bagging_temperature=2": {"bootstrap_type": "Bayesian", "bagging_temperature": 2.0},
    "grow_policy=Lossguide,max_leaves=64": {"grow_policy": "Lossguide", "max_leaves": 64},
}


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축 (exp_007 5col trackman 챔피언, k=50)")
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

    X_train = train_shrunk.loc[~is_val, FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val = train_shrunk.loc[is_val, FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET]
    train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
    print(f"train={X_train.shape}, val={X_val.shape}, features={len(FEATURE_SET)}")

    print()
    print("=" * 80)
    print(f"1. {len(CONFIGS)}개 하이퍼파라미터 설정 순차 학습")
    print("=" * 80)
    results = {}
    for name, overrides in CONFIGS.items():
        params = dict(BASE_PARAMS)
        params.update(overrides)
        t = time.time()
        clf = cb.CatBoostClassifier(**params)
        clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        elapsed = time.time() - t
        pred = clf.predict_proba(X_val)[:, 1]
        brier, score = official_score(pred, y_val)
        results[name] = {"brier": brier, "score": score, "best_iter": clf.get_best_iteration(), "elapsed": elapsed}
        print(f"[{name}] Brier={brier:.6f} | score={score:.2f} | best_iter={clf.get_best_iteration()} | {elapsed:.1f}s")

    print()
    print("=" * 80)
    print("요약 (baseline 대비 Δ)")
    print("=" * 80)
    base_score = results["baseline (exp_007/008과 동일)"]["score"]
    for name, r in sorted(results.items(), key=lambda kv: -kv[1]["score"]):
        print(f"{name}: score={r['score']:.2f} (Brier {r['brier']:.6f}), Δ vs baseline={r['score']-base_score:+.2f}")

    best_name = max(results, key=lambda n: results[n]["score"])
    print(f"\n최선: {best_name} (score {results[best_name]['score']:.2f})")

    print("\n완료.")


if __name__ == "__main__":
    main()
