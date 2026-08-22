"""Chronological train/validation split helpers.

CLAUDE.md "Validation Policy": the hidden eval set is season 2025, so
the mandatory default split is season-based, never random —
train 2019-2023 / validate 2024. Every prior exp inlines
`train["season"] == 2024` itself; this module is the single place new
scripts (starting with exp_006) get that mask from, plus the one new
split this phase needs: a leak-free 3-way chain for calibrator fitting
(see `src/calibration.py`).
"""


def get_main_split(df, val_season=2024):
    """(train_mask, val_mask): train = season < val_season, val = season == val_season."""
    train_mask = df["season"] < val_season
    val_mask = df["season"] == val_season
    return train_mask, val_mask


def get_calibration_split(df, calib_season=2023, val_season=2024):
    """3-way chronological chain for leak-free calibrator fitting (doc's Phase D):

    fit_mask   = season < calib_season   (2019-2022) -> train a *separate* model instance
    calib_mask = season == calib_season  (2023)       -> fit Platt/Isotonic on this model's predictions
    eval_mask  = season == val_season    (2024)        -> informational only; the calibrator is
                 actually applied to the real Phase-A model's already-computed 2024 predictions,
                 not to a fresh prediction from the 2019-2022 sub-model.
    """
    fit_mask = df["season"] < calib_season
    calib_mask = df["season"] == calib_season
    eval_mask = df["season"] == val_season
    return fit_mask, calib_mask, eval_mask
