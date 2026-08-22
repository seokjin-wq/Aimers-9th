"""One-off follow-up to train_exp007.py: re-trains only the winning
shrink_k=50 variant (the full 3-way grid + baseline reproduction was
already run and recorded in experiments/exp007_run_log.txt) to pull
feature importance and segment-level error analysis without repeating
the other 2 grid points."""

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
    PHYSICAL_COLS, TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables, attach_pitcher_physical_features, load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
BEST_K = 50

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
df_k = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=BEST_K)

X_train, y_train = df_k.loc[~is_val, ALL_FEATURES], df_k.loc[~is_val, TARGET]
X_val, y_val = df_k.loc[is_val, ALL_FEATURES], df_k.loc[is_val, TARGET]

cb_params = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=42, thread_count=-1, verbose=200,
)
train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)

t = time.time()
clf = cb.CatBoostClassifier(**cb_params)
clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
print(f"학습 완료 :: {time.time() - t:.1f}s | best_iter={clf.get_best_iteration()}")

val_pred = clf.predict_proba(X_val)[:, 1]
brier, score = official_score(val_pred, y_val)
print(f"[k={BEST_K}] Brier={brier:.6f} | score={score:.2f}")

print("\n--- feature importance (top 20 / 89) ---")
importances = clf.get_feature_importance(train_pool)
ranked = sorted(zip(ALL_FEATURES, importances), key=lambda x: -x[1])
for rank, (name, imp) in enumerate(ranked[:20], start=1):
    tag = " <== trackman" if name in TRACKMAN_PITCHER_ASOF_COLS else ""
    print(f"  #{rank:2d} {name}: {imp:.2f}{tag}")
trackman_ranks = sorted(i + 1 for i, (name, _) in enumerate(ranked) if name in TRACKMAN_PITCHER_ASOF_COLS)
print(f"\ntrackman 피처 5개의 89개 중 순위: {trackman_ranks}")

print("\n--- 오류 분석 (구간별 Brier) ---")
val_seg = df_k.loc[is_val, ["two_strike", "is_close_game", "asof_pitcher_n", "pitcher_id"]].copy()
val_seg["pred"] = val_pred
val_seg["y"] = y_val.values
val_seg["cold_start"] = val_seg["asof_pitcher_n"] < 50
mapped_pids = set(pitcher_mapping["pitcher_id"])
val_seg["pitcher_mapped"] = val_seg["pitcher_id"].isin(mapped_pids)
segments = {
    "two_strike=1": val_seg["two_strike"] == 1,
    "two_strike=0": val_seg["two_strike"] == 0,
    "is_close_game=1": val_seg["is_close_game"] == 1,
    "cold_start(n<50)": val_seg["cold_start"],
    "warm(n>=50)": ~val_seg["cold_start"],
    "trackman 매핑된 투수": val_seg["pitcher_mapped"],
    "trackman 매핑 안 된 투수": ~val_seg["pitcher_mapped"],
}
for name, mask in segments.items():
    sub = val_seg.loc[mask]
    seg_brier = ((sub["pred"] - sub["y"]) ** 2).mean()
    print(f"  {name}: n={len(sub)}, brier={seg_brier:.6f}, 실제 성공률={sub['y'].mean():.4f}, 평균예측={sub['pred'].mean():.4f}")

print("\n완료.")
