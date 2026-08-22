"""Shared helper for the exp_031-036 round: builds exactly exp_030's
105-feature set and the standard 2019-2023 train / 2024 validation
split, so every new experiment script in this round reuses one
definition instead of re-copying the ~20-line feature-assembly block
from train_exp027_final.py into each new train_exp03X_*.py file.

Leak-safety: identical to train_exp027_final.py -- all *_priors are
fit_shrinkage_priors/fit_season_state_priors on train_only (season <
2024) rows only, never on the val split.
"""

import os

import joblib
import pandas as pd

from features import CAT_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from season_state_features import (
    attach_season_state_features, build_season_baselines, fit_season_state_priors, season_state_cols,
)
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS, attach_pitcher_physical_features, build_pitcher_physical_asof_tables, load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
CHAMPION_META_PATH = "./submission/archive/exp030_season_state_no_extrapolation/model/model_meta.pkl"

# IMPORTANT: do NOT reconstruct the feature list from features.py's
# current DERIVED_COLS -- that module has grown since exp_030 was
# archived (exp_028 appended 7 columns, same_hand_x_fastball_rate +
# 6 reliability features, that were tested and REJECTED as noise --
# see experiments/exp_028_reliability_fastball.md -- but left in the
# module for future reuse). A naive `DERIVED_COLS`-based rebuild
# silently pulls in those 7 extra columns (105 -> 112), contaminating
# every exp_03X comparison against the real champion. Load the exact
# frozen 105-feature list from the actual archived production model
# instead, so this can never drift again.
_champion_meta = joblib.load(CHAMPION_META_PATH)
ALL_FEATURES = _champion_meta["all_features"]
assert len(ALL_FEATURES) == 105, f"expected exp_030's 105 features, got {len(ALL_FEATURES)}"

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]


def _recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def build_holdout_split(extra_cols=None, val_season=2024, max_train_season=None):
    """Returns (X_train, y_train, X_val, y_val, feature_list) for a
    train/val split with exp_030's exact 105 features (plus any
    extra_cols the caller wants preserved through the pipeline, e.g.
    GROUP_COLS for a calibration step -- these are NOT added to the
    model's feature list, only kept as columns on the returned frames
    if the caller re-slices with them).

    Default (val_season=2024, max_train_season=None) is the standard
    2019-2023/2024 holdout. exp_034 uses val_season=2023,
    max_train_season=2022 to build a genuine out-of-time split (train
    strictly before the season whose residual gets measured) distinct
    from the 2019-2023/2024 split every other exp_03X validates on --
    max_train_season also caps which rows count as "train_only" for
    fitting priors/shrinkage, so a 2019-2022/2023 split never touches
    2023 or 2024 rows when fitting anything."""
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig",
                         usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    is_val = train["season"] == val_season
    if max_train_season is not None:
        train = train.loc[(train["season"] <= max_train_season) | is_val].reset_index(drop=True)
        is_val = train["season"] == val_season
    train_only = train.loc[~is_val]
    val_priors = fit_shrinkage_priors(_recent_seasons_df(train_only))
    train_shrunk_val = apply_shrinkage(train, val_priors)
    df_val = attach_pitcher_physical_features(train_shrunk_val, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    pitcher_baselines = build_season_baselines(train_only, "pitcher")
    pitcher_priors = fit_season_state_priors(train_only, "pitcher")
    df_val = attach_season_state_features(df_val, pitcher_baselines, pitcher_priors, "pitcher")
    batter_baselines = build_season_baselines(train_only, "batter")
    batter_priors = fit_season_state_priors(train_only, "batter")
    df_val = attach_season_state_features(df_val, batter_baselines, batter_priors, "batter")

    feature_list = ALL_FEATURES + list(extra_cols or [])
    X_train = df_val.loc[~is_val, feature_list]
    y_train = df_val.loc[~is_val, TARGET]
    X_val = df_val.loc[is_val, feature_list]
    y_val = df_val.loc[is_val, TARGET]
    return X_train, y_train, X_val, y_val, ALL_FEATURES
