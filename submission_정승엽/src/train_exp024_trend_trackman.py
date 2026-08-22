"""exp_024 -- trend-extrapolated pitcher-level Trackman physical features,
backtested FAIRLY against what real 2025 inference will actually see.

Important prerequisite finding (see module docstrings in
`trackman_pitcher_features_trend.py`): every prior trackman-pitcher-asof
experiment (exp_007/008/010/...) validated on season 2024 using tables
built from the FULL `trackman_clean.csv` (2019-2024 real rows). Because
season 2024 genuinely has Trackman rows, 2024 validation rows mostly
resolve via the interior cumulative-before-ym table using real in-season
2024 Trackman history -- never touching the flat-mean sentinel at all.
Real 2025 inference has ZERO 2025 Trackman rows, so every 2025 row is
forced onto the sentinel with no in-season update. That means the
existing 749.58 local validation score for the champion trackman feature
set is NOT representative of how that feature set behaves at real
submission time -- it's optimistic specifically for the trackman
columns.

This script fixes that mismatch for a fair A/B: it builds trackman
tables from ONLY season <= 2022 real rows (i.e. deletes 2023 from the
table-building input the same way 2025 is genuinely absent), so a
season-2023 pitcher a trend/flat sentinel is forced for every validation
row -- mirroring the real 2025 condition as closely as this dataset
allows while still validating on a held-out labelled season. Train/val
split for the surrounding CatBoost model is kept at the CLAUDE.md
standard (train 2019-2023, validate 2024) but the TRACKMAN TABLES
specifically are built with season < target_season(=2024) trackman rows.

Since target_season=2024 already needs the sentinel to be blind to 2024
itself (which happens automatically -- season<2024 is exactly the real
production condition, no extra deletion needed), variant construction is
simpler than the exp_024 draft implied: just call table builders with
target_season=2024 and trackman_clean filtered to season<2024. That already
reproduces the true production blindness for free.

Three variants of the sentinel, everything else (base features,
shrinkage, model, hyperparameters) held fixed at the exp_007/010
champion config:
  A. flat   -- production method (trackman_pitcher_features.py), i.e.
              cumulative mean of the pitcher's full season<2024 history.
  B. trend  -- this experiment's linear per-pitcher season-level trend,
              extrapolated to 2024, clipped to [1,99] pct, falls back to
              flat mean under 3 prior seasons.
  C. last   -- naive "most recent season's mean" (no trend fit at all),
              included because exp_023's walk-forward table found this
              sometimes competitive with trend at low season counts.
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
    attach_pitcher_physical_features,
    load_pitcher_mapping,
    PHYSICAL_COLS,
)
from trackman_pitcher_features_trend import build_pitcher_physical_asof_tables_trend

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
VAL_SEASON = 2024
SEED = 42

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


def build_flat_blind_tables(trackman_clean, target_season):
    """Variant A: production flat-mean sentinel, but built from
    season<target_season only (blind, matches real 2025 condition)."""
    tm = trackman_clean.loc[trackman_clean["season"] < target_season].copy()
    tm = tm.loc[~tm["is_illegal_count"]]
    tm["ym"] = tm["season"] * 100 + tm["game_month"]

    tables = {}
    for col in PHYSICAL_COLS:
        frame = tm.dropna(subset=[col])
        g = (
            frame.groupby(["pitcher_trackman_id", "ym"])[col]
            .agg(n="size", s="sum")
            .reset_index()
            .sort_values(["pitcher_trackman_id", "ym"])
        )
        g["cum_n"] = g.groupby("pitcher_trackman_id")["n"].cumsum() - g["n"]
        g["cum_s"] = g.groupby("pitcher_trackman_id")["s"].cumsum() - g["s"]
        g["asof_mean"] = g["cum_s"] / g["cum_n"]
        cum_table = g[["pitcher_trackman_id", "ym", "cum_n", "asof_mean"]]

        totals = frame.groupby("pitcher_trackman_id")[col].agg(n="size", asof_mean="mean").reset_index()
        totals = totals.rename(columns={"n": "cum_n"})
        totals["ym"] = target_season * 100 + 1

        full_table = pd.concat([cum_table, totals[["pitcher_trackman_id", "ym", "cum_n", "asof_mean"]]], ignore_index=True)
        full_table = full_table.sort_values(["pitcher_trackman_id", "ym"]).reset_index(drop=True)
        tables[col] = {"table": full_table, "league_fallback": float(frame[col].mean())}
    return tables


def build_last_season_blind_tables(trackman_clean, target_season):
    """Variant C: naive most-recent-prior-season mean, season<target_season only."""
    tm = trackman_clean.loc[trackman_clean["season"] < target_season].copy()
    tm = tm.loc[~tm["is_illegal_count"]]
    tm["ym"] = tm["season"] * 100 + tm["game_month"]

    tables = {}
    for col in PHYSICAL_COLS:
        frame = tm.dropna(subset=[col])
        g = (
            frame.groupby(["pitcher_trackman_id", "ym"])[col]
            .agg(n="size", s="sum")
            .reset_index()
            .sort_values(["pitcher_trackman_id", "ym"])
        )
        g["cum_n"] = g.groupby("pitcher_trackman_id")["n"].cumsum() - g["n"]
        g["cum_s"] = g.groupby("pitcher_trackman_id")["s"].cumsum() - g["s"]
        g["asof_mean"] = g["cum_s"] / g["cum_n"]
        cum_table = g[["pitcher_trackman_id", "ym", "cum_n", "asof_mean"]]

        league_fallback = float(frame[col].mean())
        season_means = frame.groupby(["pitcher_trackman_id", "season"])[col].mean().reset_index()
        flat_totals = frame.groupby("pitcher_trackman_id").size().rename("cum_n").reset_index()
        last_season = season_means.sort_values("season").groupby("pitcher_trackman_id").tail(1)
        totals = last_season.merge(flat_totals, on="pitcher_trackman_id")
        totals = totals.rename(columns={col: "asof_mean"})
        totals["ym"] = target_season * 100 + 1

        full_table = pd.concat([cum_table, totals[["pitcher_trackman_id", "ym", "cum_n", "asof_mean"]]], ignore_index=True)
        full_table = full_table.sort_values(["pitcher_trackman_id", "ym"]).reset_index(drop=True)
        tables[col] = {"table": full_table, "league_fallback": league_fallback}
    return tables


def evaluate_variant(name, tables, train, is_val, pitcher_mapping):
    train_only = train.loc[~is_val]
    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, val_priors_recent)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    X_train = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET]

    cb_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=SEED, thread_count=-1, verbose=False,
    )
    train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
    t = time.time()
    clf = cb.CatBoostClassifier(**cb_params)
    clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    elapsed = time.time() - t
    pred = clf.predict_proba(X_val)[:, 1]
    brier, score = official_score(pred, y_val)
    print(f"[{name}] Brier={brier:.6f} | score={score:.2f} | best_iter={clf.get_best_iteration()} | {elapsed:.1f}s")
    return brier, score, pred


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)
    is_val = train["season"] == VAL_SEASON

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()

    print()
    print("=" * 80)
    print(f"1. 3-way 공정 backtest (target_season={VAL_SEASON}, trackman은 season<{VAL_SEASON}만 사용 -- 실제 2025 조건 재현)")
    print("=" * 80)

    tables_flat = build_flat_blind_tables(trackman_clean, VAL_SEASON)
    brier_a, score_a, pred_a = evaluate_variant("A: flat (blind, production method)", tables_flat, train, is_val, pitcher_mapping)

    tables_trend = build_pitcher_physical_asof_tables_trend(trackman_clean.loc[trackman_clean["season"] < VAL_SEASON], VAL_SEASON, min_seasons_for_trend=3)
    brier_b, score_b, pred_b = evaluate_variant("B: trend extrapolation", tables_trend, train, is_val, pitcher_mapping)

    tables_last = build_last_season_blind_tables(trackman_clean, VAL_SEASON)
    brier_c, score_c, pred_c = evaluate_variant("C: last-season-only", tables_last, train, is_val, pitcher_mapping)

    print()
    print("=" * 80)
    print("2. 요약")
    print("=" * 80)
    print(f"A flat (blind, production 방식 실제조건 재현): score={score_a:.2f}")
    print(f"B trend extrapolation:                        score={score_b:.2f}  (Δ vs A = {score_b - score_a:+.2f})")
    print(f"C last-season-only:                            score={score_c:.2f}  (Δ vs A = {score_c - score_a:+.2f})")
    print()
    print("참고: 기존 exp_010 로그의 749.58은 season<2024 blind 조건이 아니라")
    print("2024 실제 트랙맨 in-season 데이터를 누린 optimistic 조건이었음 --")
    print("위 A 점수가 실제 2025 제출 조건에 더 가까운 '공정 baseline'.")

    np.savez(
        "./output/exp024_variant_preds.npz",
        pred_a=pred_a, pred_b=pred_b, pred_c=pred_c, y_val=train.loc[is_val, TARGET].to_numpy(),
    )
    print("저장: ./output/exp024_variant_preds.npz")


if __name__ == "__main__":
    main()
