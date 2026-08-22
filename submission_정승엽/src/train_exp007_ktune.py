"""Fine-tune shrink_k around the exp_007 grid boundary (k=50 was best of
[50,100,300]; 300 was clearly worse, so search downward: 15/25/40)."""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import pandas as pd

from features import CAT_COLS, DERIVED_COLS, SHRUNK_COLS, POST_SHRINKAGE_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from metrics import official_score
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS, build_pitcher_physical_asof_tables, attach_pitcher_physical_features, load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
K_GRID = [15, 25, 40]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS

train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
train = build_features(train)

trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
pitcher_mapping = load_pitcher_mapping()
tables = build_pitcher_physical_asof_tables(trackman_clean)

is_val = train["season"] == 2024
train_only = train.loc[~is_val]
val_priors_recent = fit_shrinkage_priors(train_only[train_only["season"].isin(sorted(train_only["season"].unique())[-2:])])
train_shrunk = apply_shrinkage(train, val_priors_recent)

cb_params = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=42, thread_count=-1, verbose=False,
)

print("이전 그리드 참고: k=50 -> 740.86, k=100 -> 725.34, k=300 -> 734.90, baseline -> 723.17")
print()
results = {}
for k in K_GRID:
    df_k = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=k)
    X_train, y_train = df_k.loc[~is_val, ALL_FEATURES], df_k.loc[~is_val, TARGET]
    X_val, y_val = df_k.loc[is_val, ALL_FEATURES], df_k.loc[is_val, TARGET]
    train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)

    t = time.time()
    clf = cb.CatBoostClassifier(**cb_params)
    clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    elapsed = time.time() - t
    val_pred = clf.predict_proba(X_val)[:, 1]
    brier, score = official_score(val_pred, y_val)
    print(f"[k={k}] Brier={brier:.6f} | score={score:.2f} | best_iter={clf.get_best_iteration()} | {elapsed:.1f}s")
    results[k] = score

best_k = max(results, key=results.get)
print(f"\n이 그리드 최선: k={best_k} (score {results[best_k]:.2f})")
print("전체(15/25/40/50/100/300) 중 최선 후보를 다음 단계(전체 재학습)에서 확정할 것.")
