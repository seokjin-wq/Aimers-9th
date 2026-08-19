from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor


class NativeCatBoostPreprocessor(BaseEstimator, TransformerMixin):
    """Keep named string categoricals for CatBoost's ordered statistics."""

    def __init__(self, categorical: list[str], features: list[str]):
        self.categorical = categorical
        self.features = features

    def fit(self, frame: pd.DataFrame, target=None):
        numeric = [
            column for column in self.features if column not in self.categorical
        ]
        self.numeric_ = numeric
        self.medians_ = (
            frame.loc[:, numeric]
            .apply(pd.to_numeric, errors="coerce")
            .median()
        )
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        output = frame.loc[:, self.features].copy()
        for column in self.categorical:
            output[column] = output[column].fillna("__MISSING__").astype(str)
        if self.numeric_:
            output.loc[:, self.numeric_] = (
                output.loc[:, self.numeric_]
                .apply(pd.to_numeric, errors="coerce")
                .fillna(self.medians_)
                .astype("float32")
            )
        return output

    def get_feature_names_out(self, input_features=None) -> np.ndarray:
        return np.asarray(self.features, dtype=object)


class CatBoostSeedEnsemble(BaseEstimator):
    def __init__(
        self,
        params: dict[str, Any],
        seeds: list[int],
        categorical: list[str],
    ):
        self.params = params
        self.seeds = seeds
        self.categorical = categorical

    def fit(self, matrix, target, sample_weight=None):
        self.models_ = []
        for seed in self.seeds:
            params = dict(self.params)
            params["random_seed"] = int(seed)
            params["cat_features"] = list(self.categorical)
            model = CatBoostClassifier(**params)
            model.fit(matrix, target, sample_weight=sample_weight)
            self.models_.append(model)
        return self

    def predict_proba(self, matrix) -> np.ndarray:
        return np.mean(
            [model.predict_proba(matrix) for model in self.models_], axis=0
        )

    def get_feature_importance(self) -> np.ndarray:
        return np.mean(
            [model.get_feature_importance() for model in self.models_], axis=0
        )


class SegmentedCatBoost(BaseEstimator):
    """Fit one CatBoost model per observed segment value."""

    def __init__(
        self,
        params: dict[str, Any],
        categorical: list[str],
        segment_columns: list[str],
    ):
        self.params = params
        self.categorical = categorical
        self.segment_columns = segment_columns

    def _keys(self, matrix: pd.DataFrame) -> pd.Series:
        if len(self.segment_columns) == 1:
            return matrix[self.segment_columns[0]].astype(str)
        return matrix[self.segment_columns].astype(str).agg("|".join, axis=1)

    def fit(self, matrix, target, sample_weight=None):
        if not isinstance(matrix, pd.DataFrame):
            raise TypeError("segmented CatBoost에는 DataFrame 입력이 필요합니다.")
        keys = self._keys(matrix)
        target_array = np.asarray(target)
        weight_array = (
            None if sample_weight is None else np.asarray(sample_weight)
        )
        self.prior_ = float(target_array.mean())
        self.models_ = {}
        self.segment_sizes_ = {}
        for key in keys.unique():
            mask = keys.eq(key).to_numpy()
            model = CatBoostClassifier(
                **dict(self.params), cat_features=list(self.categorical)
            )
            model.fit(
                matrix.loc[mask],
                target_array[mask],
                sample_weight=(
                    None if weight_array is None else weight_array[mask]
                ),
            )
            self.models_[key] = model
            self.segment_sizes_[key] = int(mask.sum())
        return self

    def predict_proba(self, matrix) -> np.ndarray:
        keys = self._keys(matrix)
        probability = np.full(len(matrix), self.prior_, dtype=float)
        for key, model in self.models_.items():
            mask = keys.eq(key).to_numpy()
            if mask.any():
                probability[mask] = model.predict_proba(matrix.loc[mask])[:, 1]
        return np.column_stack([1.0 - probability, probability])

    def get_feature_importance(self) -> np.ndarray:
        total = sum(self.segment_sizes_.values())
        return sum(
            self.segment_sizes_[key] * model.get_feature_importance()
            for key, model in self.models_.items()
        ) / total


def make_preprocessor(
    categorical: list[str],
    features: list[str],
    *,
    native_categorical: bool = False,
    linear: bool = False,
) -> ColumnTransformer | NativeCatBoostPreprocessor:
    if native_categorical:
        return NativeCatBoostPreprocessor(categorical, features)
    numeric = [column for column in features if column not in categorical]
    if linear:
        return ColumnTransformer(
            [
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore"),
                    categorical,
                ),
                (
                    "numeric",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler(with_mean=False)),
                        ]
                    ),
                    numeric,
                ),
            ],
            remainder="drop",
            verbose_feature_names_out=False,
        )
    return ColumnTransformer(
        [
            (
                "categorical",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value", unknown_value=-1
                ),
                categorical,
            ),
            ("numeric", SimpleImputer(strategy="median"), numeric),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def make_model(spec: dict[str, Any], categorical: list[str] | None = None):
    family = spec["family"]
    params = dict(spec.get("params", {}))
    if family == "catboost":
        if spec.get("native_categorical", False):
            params["cat_features"] = list(categorical or [])
        return CatBoostClassifier(**params)
    if family == "random_forest":
        return RandomForestClassifier(**params)
    if family == "extra_trees":
        return ExtraTreesClassifier(**params)
    if family == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(**params)
    if family == "logistic_regression":
        return LogisticRegression(**params)
    if family == "lightgbm":
        return LGBMClassifier(**params)
    if family == "xgboost":
        return XGBClassifier(**params)
    if family == "catboost_regressor":
        if spec.get("native_categorical", False):
            params["cat_features"] = list(categorical or [])
        return CatBoostRegressor(**params)
    if family == "lightgbm_regressor":
        return LGBMRegressor(**params)
    if family == "xgboost_regressor":
        return XGBRegressor(**params)
    if family == "catboost_ensemble":
        return CatBoostSeedEnsemble(
            params=params,
            seeds=[int(value) for value in spec["seeds"]],
            categorical=list(categorical or []),
        )
    if family == "catboost_segmented":
        return SegmentedCatBoost(
            params=params,
            categorical=list(categorical or []),
            segment_columns=list(spec["segment_columns"]),
        )
    raise ValueError(f"지원하지 않는 모델군입니다: {family}")


def predict_probability(model, matrix) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(matrix)[:, 1]
    else:
        probability = model.predict(matrix)
    return np.clip(np.asarray(probability, dtype=float), 0.0, 1.0)
