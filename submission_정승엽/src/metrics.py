"""Shared official-metric + calibration helpers.

Single source of truth for `official_score`, so exp_006 onward doesn't
re-duplicate the inline copies already living in `train_exp003.py` (a
named local function) and `train_lgbm.py` (fully inline, no function at
all) — those two historical scripts are left untouched, this module is
for every *new* comparison script.

`official_score(pred, y)` intentionally keeps the same `(brier, score)`
2-tuple return that `train_exp003.py`'s local copy uses, so numbers are
directly comparable without reshuffling call sites.
"""

import numpy as np
import pandas as pd


def brier_score(pred, y):
    pred = np.asarray(pred, dtype=float)
    y = np.asarray(y, dtype=float)
    return float(((pred - y) ** 2).mean())


def official_score(pred, y):
    y = np.asarray(y, dtype=float)
    pred = np.asarray(pred, dtype=float)
    r = y.mean()
    brier = brier_score(pred, y)
    baseline_brier = r * (1 - r)
    score = max(0.0, 100000 * (1 - brier / baseline_brier))
    return brier, score


def log_loss_safe(pred, y, eps=1e-15):
    pred = np.clip(np.asarray(pred, dtype=float), eps, 1 - eps)
    y = np.asarray(y, dtype=float)
    return float(-(y * np.log(pred) + (1 - y) * np.log(1 - pred)).mean())


def calibration_bins(pred, y, n_bins=10):
    """Per-0.1-width-bin table: bin_lo, bin_hi, mean_prediction,
    actual_success_rate, sample_count. Bin sample_counts always sum to
    len(y) exactly (edges are [0,0.1), [0.1,0.2), ..., [0.9,1.0])."""
    pred = np.asarray(pred, dtype=float)
    y = np.asarray(y, dtype=float)
    edges = np.linspace(0, 1, n_bins + 1)
    # rightmost bin closed on both ends so pred==1.0 isn't dropped
    bin_idx = np.clip(np.digitize(pred, edges[1:-1], right=False), 0, n_bins - 1)

    rows = []
    for b in range(n_bins):
        mask = bin_idx == b
        n = int(mask.sum())
        rows.append({
            "bin_lo": edges[b],
            "bin_hi": edges[b + 1],
            "mean_prediction": float(pred[mask].mean()) if n > 0 else np.nan,
            "actual_success_rate": float(y[mask].mean()) if n > 0 else np.nan,
            "sample_count": n,
        })
    df = pd.DataFrame(rows)
    assert df["sample_count"].sum() == len(y), (
        f"calibration_bins lost rows: bins sum to {df['sample_count'].sum()}, "
        f"expected {len(y)} (check for NaN predictions)"
    )
    return df


def expected_calibration_error(pred, y, n_bins=10):
    bins = calibration_bins(pred, y, n_bins=n_bins)
    bins = bins.dropna(subset=["mean_prediction"])
    n_total = bins["sample_count"].sum()
    if n_total == 0:
        return float("nan")
    weighted_gap = (
        bins["sample_count"] * (bins["mean_prediction"] - bins["actual_success_rate"]).abs()
    ).sum()
    return float(weighted_gap / n_total)
