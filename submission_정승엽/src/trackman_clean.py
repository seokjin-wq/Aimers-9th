"""Non-destructive cleanup of `trackman_history.csv` + shared matching-key
derivation for both trackman and train, in preparation for the
train<->trackman row-level ID mapping (`src/trackman_id_mapping.py`).

Design constraints:
- `data/trackman_history.csv` and `data/train.csv` are never modified
  (CLAUDE.md rule 12). This module reads them and writes NEW files under
  `data/processed/` (already covered by the repo-wide `data/` gitignore).
  The raw `trackman_history.csv` is kept around on purpose — a later,
  separate experiment wants to try a raw-value cosine-similarity match
  against the untouched original file.
- Nothing here drops rows. The ~97 trackman rows with an out-of-range
  `outs_before`/`balls_before`/`strikes_before` are only flagged
  (`is_illegal_count`), never removed. Whether to actually exclude them
  is decided later in `trackman_id_mapping.py`, once we've checked
  whether they still have a plausible corresponding train row via other
  situational columns (train itself has 0 such illegal rows, so this is
  a real open question, not a formality).
- `pitch_type_group` (fastball/breaking/offspeed/other) stays the
  default classification axis for feature engineering (already clean,
  0 missing, and matches the official `asof_pitcher_fastball/breaking/
  offspeed_rate` taxonomy). `tagged_pitch_type`/`auto_pitch_type` are
  still cleaned into `_clean` side-columns and kept alongside the raw
  originals, in case a future experiment wants pitch-type granularity
  finer than the 4-way group.

All normalization dictionaries below were built from the actual
`value_counts()` of the 2019-2024 file (see
`reports/trackman_clean/README.md` for the full counts) -- not guessed.
"""

import numpy as np
import pandas as pd

# --- 1. Pitch-type label cleanup -------------------------------------------
#
# Within each column, unique() variants that differ only by case/typo are
# collapsed onto whichever spelling is the majority in that column. tagged
# and auto are two independent source systems, so the majority spelling can
# differ between them (tagged: "ChangeUp" 170,859 vs "Changeup" 225 -> use
# "ChangeUp"; auto: "Changeup" 185,311 vs "ChangeUp" 90,324 -> use
# "Changeup") -- this is real, so each column gets its own map rather than
# forcing one global spelling.
#
# "Fastball" vs "Four-Seam" in `auto_pitch_type` is NOT touched here: this
# is the real 2022-onward taxonomy shift documented in
# reports/eda_trackman/README.md §5 (auto_pitch_type started splitting
# fastballs into Four-Seam from 2022), not typo noise -- merging it away
# would erase real season-trend information.
TAGGED_PITCH_TYPE_MAP = {
    "SInker": "Sinker",
    "Undefined#": "Undefined",
    "Undefind": "Undefined",
    "Changeup": "ChangeUp",
}

AUTO_PITCH_TYPE_MAP = {
    "ChangeUp": "Changeup",
}


def clean_pitch_type_columns(df):
    df = df.copy()
    df["tagged_pitch_type_clean"] = (
        df["tagged_pitch_type"].replace(TAGGED_PITCH_TYPE_MAP)
    )
    df["auto_pitch_type_clean"] = (
        df["auto_pitch_type"].replace(AUTO_PITCH_TYPE_MAP)
    )
    return df


# --- 2. Team tier (trackman side) ------------------------------------------
#
# `pitcher_team`/`batter_team` (26 codes total) are prefix-coded:
# `MIN_*` -> minor-league/farm team, `KBO_*`/`ACE_*` -> small special-sample
# codes (representative/exhibition rosters, not a regular franchise), the
# remaining 11 codes -> top-team ("1군") rosters. This is a purely
# structural rule (string prefix), so unlike the franchise-identity mapping
# below it doesn't rely on outside KBO knowledge.
#
# Verified via reports/trackman_clean/README.md: within the 11 "no prefix"
# codes, `SK_WYV` (2019-2020, 62,096 pitcher+batter rows) and `SSG_LAN`
# (2021-2024, 84,768 rows) never co-occur in the same season -- confirmed
# by season crosstab -- consistent with the real-world SK Wyverns -> SSG
# Landers franchise sale/rename in 2021. Same pattern for the minor-team
# codes `MIN_SKW`/`MIN_SSG`. This lets 11 major + 11 minor codes resolve to
# 10 real franchises (+ SK/SSG counted once).
def _team_tier(code):
    if pd.isna(code):
        return np.nan
    if code.startswith("MIN_"):
        return "minor"
    if code.startswith("KBO_") or code.startswith("ACE_"):
        return "other"
    return "major"


# Domain-knowledge (KBO team identity), not derivable from the codes alone
# by a pure string rule -- e.g. `DOO_BEA`'s minor counterpart is `MIN_DOO`
# (city abbreviation) but `KIW_HER`'s is `MIN_HER` (mascot abbreviation).
# This is a hypothesis grounded in general KBO domain knowledge
# (CLAUDE.md Ground Truth Sources priority 5), not an official DACON
# document -- kept as a secondary/bonus column, not load-bearing for the
# Phase 1 deliverable (the tier column above is the safe, structural one).
FRANCHISE_RENAME_MAP = {
    "SK_WYV": "SSG_LAN",
    "MIN_SKW": "MIN_SSG",
}

MINOR_TO_MAJOR_FRANCHISE = {
    "MIN_DOO": "DOO_BEA",
    "MIN_NCD": "NC_DIN",
    "MIN_LGT": "LG_TWI",
    "MIN_HAN": "HAN_EAG",
    "MIN_HER": "KIW_HER",
    "MIN_KTW": "KT_WIZ",
    "MIN_LOT": "LOT_GIA",
    "MIN_SAM": "SAM_LIO",
    "MIN_SSG": "SSG_LAN",
    "MIN_KIA": "KIA_TIG",
}


def _team_franchise(code):
    """Canonical franchise id (major-team code), spanning the SK->SSG
    rename and the major/minor split. Codes with no known franchise
    (KBO_*, ACE_*, MIN_HAW) map to themselves."""
    if pd.isna(code):
        return np.nan
    code = FRANCHISE_RENAME_MAP.get(code, code)
    return MINOR_TO_MAJOR_FRANCHISE.get(code, code)


def add_team_tier_columns(df):
    df = df.copy()
    df["pitcher_team_tier"] = df["pitcher_team"].map(_team_tier)
    df["batter_team_tier"] = df["batter_team"].map(_team_tier)
    df["pitcher_team_franchise"] = df["pitcher_team"].map(_team_franchise)
    df["batter_team_franchise"] = df["batter_team"].map(_team_franchise)
    return df


# --- 3. Illegal count-state flag (no rows dropped) --------------------------
def add_illegal_count_flag(df):
    df = df.copy()
    legal = (
        df["balls_before"].between(0, 3)
        & df["strikes_before"].between(0, 2)
        & df["outs_before"].between(0, 2)
    )
    df["is_illegal_count"] = ~legal
    return df


# --- 4. Shared situational matching key -------------------------------------
#
# Columns that exist, with directly comparable values, on BOTH train.csv
# and trackman_history.csv: season, game_month, game_dayofweek, inning,
# top_bottom, balls_before, strikes_before, outs_before. `top_bottom` is
# encoded differently on each side ("Top"/"Bottom" in trackman vs "T"/"B"
# in train) so callers must pass an already-normalized column (see
# `normalize_top_bottom` below) before building the key.
SITUATIONAL_KEY_COLS = [
    "season",
    "game_month",
    "game_dayofweek",
    "inning",
    "top_bottom",
    "balls_before",
    "strikes_before",
    "outs_before",
]


def normalize_top_bottom(series):
    """Map trackman's Top/Bottom or train's T/B onto a single T/B axis."""
    return series.replace({"Top": "T", "Bottom": "B"})


def add_situational_key(df, top_bottom_col="top_bottom"):
    """Add `count_state_code` (int, balls*100+strikes*10+outs) and
    `situational_key` (str, the full SITUATIONAL_KEY_COLS tuple joined) --
    a single hashable fingerprint for the block-matching step in
    trackman_id_mapping.py. Expects `top_bottom_col` to already be
    normalized to T/B (see normalize_top_bottom)."""
    df = df.copy()
    df["count_state_code"] = (
        df["balls_before"].astype(int) * 100
        + df["strikes_before"].astype(int) * 10
        + df["outs_before"].astype(int)
    )
    key_parts = [
        df["season"].astype(int).astype(str),
        df["game_month"].astype(int).astype(str),
        df["game_dayofweek"].astype(int).astype(str),
        df["inning"].astype(int).astype(str),
        df[top_bottom_col].astype(str),
        df["count_state_code"].astype(str),
    ]
    df["situational_key"] = key_parts[0].str.cat(key_parts[1:], sep="|")
    return df


# --- 5. game_date parsing (season-format-aware) ------------------------------
#
# reports/eda_trackman/README.md §2: game_date is `%m/%d/%Y` for 2019-2021
# and ISO `%Y-%m-%d` for 2022-2024. A single-format parse silently NaTs
# ~53% of rows. train.csv has no game_date at all, so this is only usable
# within trackman itself (e.g. to order rows inside a block).
def parse_game_date(series, season):
    early = season <= 2021
    parsed_early = pd.to_datetime(
        series.where(early), format="%m/%d/%Y", errors="coerce"
    )
    parsed_late = pd.to_datetime(
        series.where(~early), format="%Y-%m-%d", errors="coerce"
    )
    return parsed_early.fillna(parsed_late)


# --- 6. Row-local derived flags also needed for matching ---------------------
#
# Deliberately NOT importing trackman_features._prep_trackman here: that
# function *drops* the illegal-count rows as part of its prep, which
# conflicts with this module's "never drop, only flag" rule. Its four
# one-line derived flags are cheap enough to duplicate rather than pull in
# a function with different (row-dropping) side effects.
def add_pitch_flags(df):
    df = df.copy()
    df["same_hand_matchup"] = (df["pitcher_hand"] == df["batter_hand"]).astype(int)
    df["three_ball"] = (df["balls_before"] == 3).astype(int)
    df["is_breaking"] = (df["pitch_type_group"] == "breaking").astype(int)
    df["is_fastball"] = (df["pitch_type_group"] == "fastball").astype(int)
    return df


def clean_trackman(trackman_df):
    """Full Phase-1 trackman cleanup pipeline. Returns a new DataFrame;
    `trackman_df` is not mutated. Adds columns only -- no rows dropped, no
    original columns removed."""
    df = trackman_df.copy()
    df = clean_pitch_type_columns(df)
    df = add_team_tier_columns(df)
    df = add_illegal_count_flag(df)
    df["top_bottom_norm"] = normalize_top_bottom(df["top_bottom"])
    df = add_situational_key(df, top_bottom_col="top_bottom_norm")
    df["game_date_parsed"] = parse_game_date(df["game_date"], df["season"])
    df = add_pitch_flags(df)
    return df


def build_train_match_keys(train_df):
    """Matching-side-only derived columns for train.csv, kept in a
    separate slim table (row_id + derived columns) rather than touching
    the original train schema. `game_type` (R/F) is used directly as the
    row-level team tier signal here -- see
    reports/trackman_clean/README.md §3 for why: train's numeric
    `pitcher_team_id` turns out to encode the *organization* (10 real KBO
    franchises + a few small all-F special codes), not a major/minor
    split, so tier already lives in `game_type` per row and does not need
    to be derived from any aggregate."""
    df = train_df.copy()
    df["top_bottom_norm"] = normalize_top_bottom(df["top_bottom"])
    df = add_situational_key(df, top_bottom_col="top_bottom_norm")
    df["team_tier"] = df["game_type"].map({"R": "major", "F": "minor"})
    df = add_illegal_count_flag(df)
    df["same_hand_matchup"] = (df["pitcher_hand"] == df["batter_hand"]).astype(int)
    df["three_ball"] = (df["balls_before"] == 3).astype(int)

    keep_cols = [
        "row_id",
        "pitcher_id",
        "batter_id",
        "pitcher_hand",
        "batter_hand",
        "pitcher_team_id",
        "batter_team_id",
        "game_type",
        "team_tier",
        "season",
        "game_month",
        "game_dayofweek",
        "inning",
        "top_bottom_norm",
        "balls_before",
        "strikes_before",
        "outs_before",
        "count_state_code",
        "situational_key",
        "is_illegal_count",
        "same_hand_matchup",
        "three_ball",
    ]
    return df[keep_cols]
