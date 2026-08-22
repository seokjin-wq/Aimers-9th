"""One function per model architecture, identical (X_train, y_train,
X_val, y_val, ...) -> ModelResult signature, so exp_006's Phase A run
and Phase D's leak-free calibration-fold run call the *same* code
instead of six more copy-pasted train_*.py scripts (the gap this phase
is meant to close — see model_comparison.csv's design doc).

Preprocessing per model family (locked in from src/features.py's
CAT_COLS design, matching how each library is already used in
src/train_exp003.py):
- CatBoost: native categorical (`cat_features=CAT_COLS` on raw strings).
- RandomForest / ExtraTrees / LightGBM: share one OrdinalEncoder fit on
  CAT_COLS only; pitcher_id/batter_id/*_team_id pass through as plain
  ints (exactly how CatBoost treats them too). RF/ExtraTrees additionally
  need SimpleImputer(median) since (unlike CatBoost/LightGBM) sklearn's
  tree ensembles don't accept NaN, and the raw asof_* base columns can
  be NaN for cold-start rows (asof_*_n == 0).
- LogisticRegression: ColumnTransformer(median-impute+StandardScaler for
  numeric, OneHotEncoder for categoricals), with pitcher_id/batter_id
  either excluded (LR-1) or one-hot encoded alongside CAT_COLS (LR-2).

LightGBM training is wrapped in try/except: this exact local Windows
env has previously crashed natively (OSError/access violation) mid
LightGBM training (see src/train_exp003.py's comment + experiments/
exp_003 log) — one model's crash must not kill the whole comparison run.
"""

import io
import tempfile
import time
from dataclasses import dataclass, field

import catboost as cb
import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

try:
    import lightgbm as lgb
except ImportError:
    lgb = None


@dataclass
class ModelResult:
    name: str
    model: object = None
    val_pred: np.ndarray = None
    train_seconds: float = None
    infer_seconds: float = None
    model_mb: float = None
    status: str = "ok"
    extra: dict = field(default_factory=dict)


def _sklearn_model_mb(model):
    buf = io.BytesIO()
    joblib.dump(model, buf)
    return buf.getbuffer().nbytes / (1024 * 1024)


def _native_model_mb(save_fn):
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/model.bin"
        save_fn(path)
        import os
        return os.path.getsize(path) / (1024 * 1024)


def check_id_cardinality_feasible(train_only_df, id_cols, max_unique_sum=5000):
    total_unique = sum(train_only_df[c].nunique() for c in id_cols)
    return total_unique <= max_unique_sum, total_unique


def fit_cat_ordinal_encoder(X_train, cat_cols):
    """Fit once on the train split only; caller applies .transform() to
    both train and val (matches train_exp003.py's exact pattern)."""
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    enc.fit(X_train[cat_cols])
    return enc


# ---------------------------------------------------------------- A0 ----

def fit_mean_baseline(y_train, X_val):
    t = time.time()
    p = float(y_train.mean())
    train_seconds = time.time() - t
    t = time.time()
    val_pred = np.full(len(X_val), p)
    infer_seconds = time.time() - t
    return ModelResult(
        name="Mean",
        model=p,
        val_pred=val_pred,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        model_mb=0.0,
        extra={"p": p},
    )


# ---------------------------------------------------------------- A1 ----

def fit_logistic_regression(
    X_train, y_train, X_val, y_val,
    cat_cols, low_card_id_cols, high_card_id_cols, numeric_cols,
    include_high_card_ids, C_grid=(0.01, 0.1, 1.0, 10.0), seed=42,
):
    from metrics import official_score

    ohe_cols = list(cat_cols) + list(low_card_id_cols)
    if include_high_card_ids:
        ohe_cols = ohe_cols + list(high_card_id_cols)
        excluded_cols = []
    else:
        # LR-1: pitcher_id/batter_id excluded entirely (not one-hot, not
        # numeric — including them as raw StandardScaler input would treat
        # an arbitrary ID as an ordinal magnitude, which is meaningless).
        excluded_cols = list(high_card_id_cols)
    num_cols = [c for c in numeric_cols if c not in ohe_cols and c not in excluded_cols]

    preproc = ColumnTransformer([
        ("num", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=True), ohe_cols),
    ])

    t = time.time()
    best = None
    c_scores = {}
    for C in C_grid:
        pipe = Pipeline([
            ("preproc", preproc),
            ("clf", LogisticRegression(C=C, penalty="l2", solver="lbfgs",
                                        max_iter=200, random_state=seed)),
        ])
        pipe.fit(X_train, y_train)
        pred = pipe.predict_proba(X_val)[:, 1]
        _, score = official_score(pred, y_val)
        c_scores[C] = score
        if best is None or score > best[0]:
            best = (score, C, pipe, pred)
    train_seconds = time.time() - t

    best_score, best_C, best_pipe, best_pred = best
    t = time.time()
    _ = best_pipe.predict_proba(X_val)[:, 1]
    infer_seconds = time.time() - t

    return ModelResult(
        name="Logistic_LR2" if include_high_card_ids else "Logistic_LR1",
        model=best_pipe,
        val_pred=best_pred,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        model_mb=_sklearn_model_mb(best_pipe),
        extra={"best_C": best_C, "C_grid_scores": c_scores},
    )


# ---------------------------------------------------------------- A2/A3 --

def _fit_sklearn_tree_ensemble(cls, name, X_train_enc, y_train, X_val_enc, y_val,
                                seed, n_estimators, max_depth, min_samples_leaf):
    imputer = SimpleImputer(strategy="median")

    t = time.time()
    X_train_imp = imputer.fit_transform(X_train_enc)
    clf = cls(n_estimators=n_estimators, max_depth=max_depth,
              min_samples_leaf=min_samples_leaf, n_jobs=-1, random_state=seed)
    clf.fit(X_train_imp, y_train)
    train_seconds = time.time() - t

    t = time.time()
    X_val_imp = imputer.transform(X_val_enc)
    val_pred = clf.predict_proba(X_val_imp)[:, 1]
    infer_seconds = time.time() - t

    pipe = Pipeline([("impute", imputer), ("clf", clf)])
    return ModelResult(
        name=name,
        model=pipe,
        val_pred=val_pred,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        model_mb=_sklearn_model_mb(pipe),
        extra={"n_estimators": n_estimators, "max_depth": max_depth,
               "min_samples_leaf": min_samples_leaf},
    )


def fit_random_forest(X_train_enc, y_train, X_val_enc, y_val, seed=42,
                       n_estimators=100, max_depth=10, min_samples_leaf=200):
    return _fit_sklearn_tree_ensemble(RandomForestClassifier, "RandomForest",
                                       X_train_enc, y_train, X_val_enc, y_val,
                                       seed, n_estimators, max_depth, min_samples_leaf)


def fit_extra_trees(X_train_enc, y_train, X_val_enc, y_val, seed=42,
                     n_estimators=100, max_depth=10, min_samples_leaf=200):
    return _fit_sklearn_tree_ensemble(ExtraTreesClassifier, "ExtraTrees",
                                       X_train_enc, y_train, X_val_enc, y_val,
                                       seed, n_estimators, max_depth, min_samples_leaf)


# ---------------------------------------------------------------- A4 ----

def fit_catboost(X_train, y_train, X_val, y_val, cat_cols, seed=42):
    cb_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=seed, thread_count=-1, verbose=False,
    )
    train_pool = cb.Pool(X_train, y_train, cat_features=cat_cols)
    val_pool = cb.Pool(X_val, y_val, cat_features=cat_cols)

    t = time.time()
    clf = cb.CatBoostClassifier(**cb_params)
    clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    train_seconds = time.time() - t

    t = time.time()
    val_pred = clf.predict_proba(X_val)[:, 1]
    infer_seconds = time.time() - t

    return ModelResult(
        name="CatBoost",
        model=clf,
        val_pred=val_pred,
        train_seconds=train_seconds,
        infer_seconds=infer_seconds,
        model_mb=_native_model_mb(clf.save_model),
        extra={"best_iteration": clf.get_best_iteration()},
    )


# ---------------------------------------------------------------- A5 ----

def fit_lightgbm(X_train_enc, y_train, X_val_enc, y_val, cat_cols, seed=42):
    if lgb is None:
        return ModelResult(name="LightGBM", status="skipped:ImportError")

    lgb_params = dict(
        objective="binary", metric="binary_logloss", n_estimators=2000,
        learning_rate=0.03, num_leaves=63, subsample=0.8, subsample_freq=1,
        colsample_bytree=0.8, min_child_samples=200, random_state=seed, n_jobs=-1,
    )
    try:
        t = time.time()
        clf = lgb.LGBMClassifier(**lgb_params)
        clf.fit(
            X_train_enc, y_train,
            eval_set=[(X_val_enc, y_val)],
            categorical_feature=cat_cols,
            callbacks=[lgb.early_stopping(100), lgb.log_evaluation(0)],
        )
        train_seconds = time.time() - t

        t = time.time()
        val_pred = clf.predict_proba(X_val_enc)[:, 1]
        infer_seconds = time.time() - t

        return ModelResult(
            name="LightGBM",
            model=clf,
            val_pred=val_pred,
            train_seconds=train_seconds,
            infer_seconds=infer_seconds,
            model_mb=_native_model_mb(clf.booster_.save_model),
            extra={"best_iteration": clf.best_iteration_},
        )
    except Exception as e:
        return ModelResult(
            name="LightGBM",
            status=f"skipped:{type(e).__name__}",
            extra={"error": str(e)},
        )
