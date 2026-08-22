"""Platt / Isotonic calibration with a leak-free two-stage fit (doc
section 18): a calibrator must never be fit on the same targets it's
later scored against.

Structure:
  fit sub-model on season < calib_season (2019-2022)
      -> predict on season == calib_season (2023)
      -> fit Platt + Isotonic on those (pred, y) pairs
      -> apply BOTH calibrators to the REAL Phase-A/B/C model's
         already-computed season == val_season (2024) predictions
         (never re-predicted here)

`train_fn` is a caller-supplied closure `(X_fit, y_fit, X_calib, y_calib)
-> model_factory.ModelResult`, so this module stays decoupled from each
model family's specific preprocessing (CatBoost cat_features vs.
RF/ExtraTrees ordinal-encoding+imputation vs. Logistic's ColumnTransformer)
— the orchestration script supplies the right closure per model.
"""

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from metrics import calibration_bins, expected_calibration_error, official_score


def fit_platt(raw_pred, y, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y)
    return clf


def apply_platt(clf, raw_pred):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    return clf.predict_proba(raw_pred)[:, 1]


def fit_isotonic(raw_pred, y):
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(np.asarray(raw_pred, dtype=float), y)
    return iso


def apply_isotonic(iso, raw_pred):
    return iso.predict(np.asarray(raw_pred, dtype=float))


def run_two_stage_calibration(model_name, train_fn, df, feature_cols, target,
                               fit_mask, calib_mask, eval_pred, eval_y, seed=42):
    X_fit, y_fit = df.loc[fit_mask, feature_cols], df.loc[fit_mask, target]
    X_calib, y_calib = df.loc[calib_mask, feature_cols], df.loc[calib_mask, target]

    calib_model_result = train_fn(X_fit, y_fit, X_calib, y_calib)
    raw_calib_pred = calib_model_result.val_pred
    y_calib_arr = y_calib.values

    platt = fit_platt(raw_calib_pred, y_calib_arr, seed=seed)
    iso = fit_isotonic(raw_calib_pred, y_calib_arr)

    eval_pred = np.asarray(eval_pred, dtype=float)
    eval_y_arr = np.asarray(eval_y, dtype=float)

    out = {}
    variants = {
        "raw": eval_pred,
        "platt": apply_platt(platt, eval_pred),
        "isotonic": apply_isotonic(iso, eval_pred),
    }
    for method_name, pred in variants.items():
        brier, score = official_score(pred, eval_y_arr)
        out[method_name] = {
            "brier": brier,
            "official_score": score,
            "calibration_error": expected_calibration_error(pred, eval_y_arr),
            "calibration_bins": calibration_bins(pred, eval_y_arr),
            "pred": pred,
        }
    out["_meta"] = {
        "model_name": model_name,
        "calib_model_status": calib_model_result.status,
        "n_fit": int(fit_mask.sum()),
        "n_calib": int(calib_mask.sum()),
    }
    return out
