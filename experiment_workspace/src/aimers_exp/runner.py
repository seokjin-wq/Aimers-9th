from __future__ import annotations

import gc
import hashlib
import json
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import catboost
import numpy as np
import pandas as pd
import sklearn
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from .config import BASELINE_ROOT, PROJECT_ROOT
from .features import (
    REFERENCE_TARGET_FEATURES,
    REFERENCE_STATE_FEATURES,
    REFERENCE_PROGRESS_FEATURES,
    REFERENCE_CONTEXT_FEATURES,
    TRACKMAN_CONTEXT_FEATURES,
    TEMPORAL_TARGET_FEATURES,
    engineer_features,
    engineer_official_train_target_features,
    engineer_official_train_state_features,
    engineer_official_train_progress_features,
    engineer_official_train_context_features,
    engineer_trackman_context_features,
    engineer_temporal_target_features,
    resolve_feature_names,
)
from .metrics import probability_metrics
from .modeling import make_model, make_preprocessor, predict_probability
from .reporting import render_study_report


def _json_default(value: Any):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"JSON으로 직렬화할 수 없습니다: {type(value)!r}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value, ensure_ascii=False, indent=2, default=_json_default
        )
        + "\n",
        encoding="utf-8",
    )


def _blend_cached_probabilities(
    cached: dict[str, Any],
    model_spec: dict[str, Any],
    *,
    prefix: str = "",
) -> np.ndarray:
    """Apply variant-specific post-processing to cached raw component scores."""
    scale = float(model_spec.get("cat_scale", 1.0))
    shift = float(model_spec.get("cat_shift", 0.0))

    def adjusted_cat(raw: np.ndarray) -> np.ndarray:
        return np.clip(0.5 + scale * (raw - 0.5) + shift, 0.0, 1.0)

    adjusted_extra = np.clip(
        cached[f"{prefix}extra_probability"]
        + float(model_spec.get("extra_shift", 0.0)),
        0.0,
        1.0,
    )
    blended = (
        float(model_spec["cpu_weight"])
        * adjusted_cat(cached[f"{prefix}cpu_probability"])
        + float(model_spec["gpu_weight"])
        * adjusted_cat(cached[f"{prefix}gpu_probability"])
        + float(model_spec["extra_weight"]) * adjusted_extra
    )
    if "hist_weight" in model_spec:
        adjusted_hist = np.clip(
            cached[f"{prefix}hist_probability"]
            + float(model_spec.get("hist_shift", 0.0)),
            0.0,
            1.0,
        )
        blended = blended + float(model_spec["hist_weight"]) * adjusted_hist
    return blended


def _learn_simplex_blend_weights(
    component_probability: np.ndarray, target: np.ndarray
) -> np.ndarray:
    """Least-squares blend weights constrained to the probability simplex."""
    matrix = np.asarray(component_probability, dtype=float)
    target_array = np.asarray(target, dtype=float)
    component_count = matrix.shape[1]
    best_weight: np.ndarray | None = None
    best_loss = float("inf")
    for mask in range(1, 1 << component_count):
        indices = [i for i in range(component_count) if mask & (1 << i)]
        design = matrix[:, indices]
        gram = design.T @ design
        ones = np.ones((len(indices), 1), dtype=float)
        system = np.block([[gram, ones], [ones.T, np.zeros((1, 1))]])
        rhs = np.concatenate([design.T @ target_array, [1.0]])
        solution = np.linalg.lstsq(system, rhs, rcond=None)[0][:-1]
        if np.any(solution < -1e-10):
            continue
        solution = np.clip(solution, 0.0, None)
        solution /= solution.sum()
        weight = np.zeros(component_count, dtype=float)
        weight[indices] = solution
        loss = float(np.mean((matrix @ weight - target_array) ** 2))
        if loss < best_loss:
            best_loss = loss
            best_weight = weight
    if best_weight is None:
        raise RuntimeError("simplex blend weight optimization failed")
    return best_weight


def _learn_centered_group_trend_offsets(
    rows: pd.DataFrame,
    target: pd.Series | np.ndarray,
    group_columns: list[str],
    *,
    season_column: str = "season",
    shrinkage: float = 10_000.0,
    method: str = "wls",
) -> pd.Series:
    """Estimate one-season relative target-rate trends from reference rows only."""
    if not group_columns:
        raise ValueError("group_columns must not be empty")
    work = rows.loc[:, [season_column, *group_columns]].copy()
    work["__target"] = np.asarray(target, dtype="float64")
    work["__centered"] = work["__target"] - work.groupby(
        season_column, observed=True
    )["__target"].transform("mean")
    grouped = work.groupby(
        [*group_columns, season_column], dropna=False, observed=True
    )["__centered"].agg(
        centered_mean="mean", sample_count="count"
    ).reset_index()

    def weighted_slope(frame: pd.DataFrame) -> float:
        x = frame[season_column].to_numpy(dtype="float64")
        y = frame["centered_mean"].to_numpy(dtype="float64")
        weight = frame["sample_count"].to_numpy(dtype="float64")
        if len(frame) < 2 or np.unique(x).size < 2:
            return 0.0
        if method == "endpoint":
            order = np.argsort(x)
            x = x[order]
            y = y[order]
            slope = (y[-1] - y[0]) / (x[-1] - x[0])
        else:
            if method == "ols":
                weight = np.ones_like(weight)
            elif method != "wls":
                raise ValueError(f"unsupported trend method: {method}")
            x_centered = x - np.average(x, weights=weight)
            denominator = np.sum(weight * np.square(x_centered))
            if denominator <= 0.0:
                return 0.0
            slope = np.sum(weight * x_centered * y) / denominator
        reliability = weight.sum() / (weight.sum() + float(shrinkage))
        return float(slope * reliability)

    return grouped.groupby(
        group_columns, dropna=False, observed=True
    )[[season_column, "centered_mean", "sample_count"]].apply(weighted_slope)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_tree_hash() -> str:
    digest = hashlib.sha256()
    paths = sorted((PROJECT_ROOT / "src").rglob("*.py"))
    paths += sorted(BASELINE_ROOT.rglob("*.toml"))
    for path in paths:
        digest.update(str(path.relative_to(PROJECT_ROOT)).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def git_commit() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def validate_data_dir(data_dir: str | Path) -> Path:
    path = Path(data_dir).expanduser().resolve()
    required = ("train.csv", "test.csv", "sample_submission.csv")
    missing = [name for name in required if not (path / name).is_file()]
    if missing:
        raise FileNotFoundError(f"데이터 파일 누락: {missing} ({path})")
    return path


def read_training_data(data_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    test_columns = pd.read_csv(data_dir / "test.csv", nrows=0).columns.tolist()
    raw_columns = [column for column in test_columns if column != "row_id"]
    train = pd.read_csv(
        data_dir / "train.csv",
        usecols=["row_id", *raw_columns, "control_success"],
        encoding="utf-8-sig",
    )
    if train["control_success"].isna().any():
        raise ValueError("학습 타깃에 결측값이 있습니다.")
    return train, raw_columns


def check_feature_configs(
    resolved: dict[str, Any], data_dir: str | Path
) -> list[dict[str, Any]]:
    data_path = validate_data_dir(data_dir)
    raw_columns = [
        column
        for column in pd.read_csv(data_path / "test.csv", nrows=0).columns
        if column != "row_id"
    ]
    checked = []
    for variant in resolved["variants"]:
        features, categorical = resolve_feature_names(
            raw_columns, variant["features"]
        )
        checked.append(
            {
                "variant": variant["name"],
                "feature_set": variant["features"]["name"],
                "feature_count": len(features),
                "categorical_count": len(categorical),
                "changed_fields_vs_control": variant[
                    "changed_fields_vs_control"
                ],
            }
        )
    return checked


def _runtime_metadata(data_dir: Path, resolved: dict[str, Any]) -> dict[str, Any]:
    files = {}
    for name in ("train.csv", "test.csv", "sample_submission.csv"):
        path = data_dir / name
        files[name] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return {
        "status": "running",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "study_id": resolved["study"]["id"],
        "config_hash": resolved["config_hash"],
        "source_tree_sha256": source_tree_hash(),
        "git_commit": git_commit(),
        "baseline_provenance": {
            "repository": "Aimers-9th",
            "commit": "349498b",
            "path": "submission_허원준",
            "read_only": True,
        },
        "data_dir": str(data_dir),
        "data_files": files,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
        "catboost": catboost.__version__,
    }


def _make_run_dir(runs_root: Path, resolved: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = runs_root / resolved["study"]["id"] / (
        f"{timestamp}_{resolved['config_hash']}"
    )
    path.mkdir(parents=True, exist_ok=False)
    return path


def _variant_summary(
    variant: dict[str, Any], fold_frame: pd.DataFrame
) -> dict[str, Any]:
    scores = fold_frame["brier_skill_score"].dropna()
    return {
        "variant": variant["name"],
        "change": variant["change"],
        "feature_set": variant["features"]["name"],
        "feature_count": int(fold_frame["feature_count"].iloc[0]),
        "model": variant["model"]["name"],
        "model_family": variant["model"]["family"],
        "fold_count": int(len(fold_frame)),
        "mean_brier": float(fold_frame["brier"].mean()),
        "std_brier": float(fold_frame["brier"].std(ddof=0)),
        "mean_brier_skill_score": (
            float(scores.mean()) if len(scores) else None
        ),
        "changed_fields_vs_control": variant[
            "changed_fields_vs_control"
        ],
    }


def run_study(
    resolved: dict[str, Any],
    *,
    data_dir: str | Path,
    runs_root: str | Path = PROJECT_ROOT / "runs",
    only: list[str] | None = None,
    store_predictions: bool | None = None,
) -> Path:
    data_path = validate_data_dir(data_dir)
    selected_variants = resolved["variants"]
    if only:
        requested = set(only)
        requested.add(resolved["study"]["control"])
        unknown = sorted(requested - {v["name"] for v in selected_variants})
        if unknown:
            raise ValueError(f"study에 없는 variant: {unknown}")
        selected_variants = [
            variant for variant in selected_variants if variant["name"] in requested
        ]

    run_dir = _make_run_dir(Path(runs_root).resolve(), resolved)
    write_json(run_dir / "study_resolved.json", resolved)
    metadata = _runtime_metadata(data_path, resolved)
    write_json(run_dir / "metadata.json", metadata)
    started = time.time()

    try:
        train, raw_columns = read_training_data(data_path)
        variant_features: dict[str, tuple[list[str], list[str]]] = {}
        fold_results: dict[str, list[dict[str, Any]]] = {
            variant["name"]: [] for variant in selected_variants
        }
        for variant in selected_variants:
            feature_names, categorical = resolve_feature_names(
                raw_columns, variant["features"]
            )
            variant_features[variant["name"]] = (feature_names, categorical)
            variant_dir = run_dir / variant["name"]
            variant_dir.mkdir()
            write_json(
                variant_dir / "config_resolved.json",
                {
                    "study": resolved["study"],
                    "protocol": resolved["protocol"],
                    "variant": variant,
                },
            )
            (variant_dir / "feature_list.txt").write_text(
                "\n".join(feature_names) + "\n", encoding="utf-8"
            )

        protocol = resolved["protocol"]
        save_predictions = (
            bool(protocol["store_predictions"])
            if store_predictions is None
            else store_predictions
        )
        for validation_season in protocol["validation_seasons"]:
            train_mask = train["season"] < validation_season
            if protocol.get("train_start_season") is not None:
                train_mask &= train["season"] >= int(
                    protocol["train_start_season"]
                )
            validation_mask = train["season"] == validation_season
            if not train_mask.any() or not validation_mask.any():
                raise ValueError(
                    f"검증 시즌 {validation_season}의 학습/검증 데이터가 비었습니다."
                )
            success_prior = float(train.loc[train_mask, "control_success"].mean())
            requested_custom = {
                feature
                for variant in selected_variants
                for feature in variant["features"].get("custom", [])
            }
            engineered = engineer_features(
                train.drop(columns=["control_success"]),
                success_prior=success_prior,
                requested_custom=requested_custom,
            )
            requested_features = {
                feature
                for variant in selected_variants
                for feature in variant_features[variant["name"]][0]
            }
            if requested_features & TEMPORAL_TARGET_FEATURES:
                engineered = engineer_temporal_target_features(
                    engineered,
                    train["control_success"],
                    success_prior=success_prior,
                )
            if requested_features & REFERENCE_TARGET_FEATURES:
                engineered = engineer_official_train_target_features(
                    engineered,
                    train["control_success"],
                    reference_mask=train_mask,
                    apply_mask=validation_mask,
                    success_prior=success_prior,
                    requested=requested_features,
                )
            if requested_features & REFERENCE_STATE_FEATURES:
                engineered = engineer_official_train_state_features(
                    engineered,
                    train["control_success"],
                    reference_mask=train_mask,
                    apply_mask=validation_mask,
                    requested=requested_features,
                )
            if requested_features & REFERENCE_PROGRESS_FEATURES:
                engineered = engineer_official_train_progress_features(
                    engineered,
                    reference_mask=train_mask,
                    apply_mask=validation_mask,
                    requested=requested_features,
                )
            if requested_features & REFERENCE_CONTEXT_FEATURES:
                engineered = engineer_official_train_context_features(
                    engineered,
                    train["control_success"],
                    reference_mask=train_mask,
                    apply_mask=validation_mask,
                    requested=requested_features,
                )
            if requested_features & TRACKMAN_CONTEXT_FEATURES:
                trackman_columns = [
                    "season", "pitcher_hand", "batter_hand", "balls_before",
                    "strikes_before", "pitch_type_group", "rel_speed",
                    "spin_rate", "induced_vert_break", "horz_break",
                    "extension", "zone_speed",
                ]
                trackman = pd.read_csv(
                    data_path / "trackman_history.csv",
                    usecols=trackman_columns,
                )
                trackman = trackman.loc[
                    trackman["season"].lt(validation_season)
                ].reset_index(drop=True)
                engineered = engineer_trackman_context_features(
                    engineered,
                    trackman,
                    reference_mask=train_mask,
                    apply_mask=validation_mask,
                    requested=requested_features,
                )
                del trackman

            blend_component_cache: dict[str, dict[str, Any]] = {}

            for variant in selected_variants:
                name = variant["name"]
                features, categorical = variant_features[name]
                print(f"[{validation_season}] {name}", flush=True)
                model_spec = variant["model"]
                variant_diagnostics: dict[str, Any] = {}
                if model_spec["family"] == "catboost_probability_calibrated":
                    cache_key = json.dumps(
                        {
                            "kind": "probability_calibration",
                            "features": features,
                            "categorical": categorical,
                            "cat_params": model_spec["cat_params"],
                            "cat_season_decay": model_spec.get(
                                "cat_season_decay"
                            ),
                        },
                        sort_keys=True,
                    )
                    cached = blend_component_cache.get(cache_key)
                    if cached is None:
                        calibration_season = int(validation_season) - 1
                        calibration_train_mask = train["season"].lt(
                            calibration_season
                        )
                        if protocol.get("train_start_season") is not None:
                            calibration_train_mask &= train["season"].ge(
                                int(protocol["train_start_season"])
                            )
                        calibration_mask = train["season"].eq(
                            calibration_season
                        )
                        preprocess_started = time.time()
                        full_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        full_train = full_preprocessor.fit_transform(
                            engineered.loc[train_mask, features]
                        )
                        full_validation = full_preprocessor.transform(
                            engineered.loc[validation_mask, features]
                        )
                        calibration_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        calibration_train = calibration_preprocessor.fit_transform(
                            engineered.loc[calibration_train_mask, features]
                        )
                        calibration_validation = calibration_preprocessor.transform(
                            engineered.loc[calibration_mask, features]
                        )
                        preprocess_seconds = time.time() - preprocess_started
                        component_spec = {
                            "family": "catboost",
                            "native_categorical": True,
                            "params": model_spec["cat_params"],
                        }
                        full_model = make_model(component_spec, categorical)
                        calibration_model = make_model(component_spec, categorical)
                        fit_started = time.time()
                        full_model.fit(
                            full_train,
                            train.loc[train_mask, "control_success"],
                        )
                        calibration_model.fit(
                            calibration_train,
                            train.loc[calibration_train_mask, "control_success"],
                        )
                        fit_seconds = time.time() - fit_started
                        cached = {
                            "validation_probability": predict_probability(
                                full_model, full_validation
                            ),
                            "calibration_probability": predict_probability(
                                calibration_model, calibration_validation
                            ),
                            "calibration_target": train.loc[
                                calibration_mask, "control_success"
                            ].to_numpy(),
                            "preprocess_seconds": preprocess_seconds,
                            "fit_seconds": fit_seconds,
                        }
                        blend_component_cache[cache_key] = cached
                        del (
                            full_model,
                            calibration_model,
                            full_preprocessor,
                            calibration_preprocessor,
                            full_train,
                            full_validation,
                            calibration_train,
                            calibration_validation,
                        )
                    else:
                        preprocess_seconds = 0.0
                        fit_seconds = 0.0

                    calibration_probability = np.clip(
                        cached["calibration_probability"], 1e-6, 1.0 - 1e-6
                    )
                    validation_probability = np.clip(
                        cached["validation_probability"], 1e-6, 1.0 - 1e-6
                    )
                    calibration_target = cached["calibration_target"]
                    method = model_spec["calibration_method"]
                    if method == "mean_shift":
                        shift = float(
                            calibration_target.mean()
                            - calibration_probability.mean()
                        )
                        probabilities = validation_probability + shift
                    elif method == "affine":
                        design = np.column_stack(
                            [calibration_probability, np.ones(len(calibration_probability))]
                        )
                        slope, intercept = np.linalg.lstsq(
                            design, calibration_target, rcond=None
                        )[0]
                        probabilities = slope * validation_probability + intercept
                    elif method in {"platt", "beta"}:
                        calibration_logit = np.log(calibration_probability) - np.log1p(
                            -calibration_probability
                        )
                        validation_logit = np.log(validation_probability) - np.log1p(
                            -validation_probability
                        )
                        if method == "platt":
                            calibration_design = calibration_logit[:, None]
                            validation_design = validation_logit[:, None]
                        else:
                            calibration_design = np.column_stack(
                                [
                                    np.log(calibration_probability),
                                    -np.log1p(-calibration_probability),
                                ]
                            )
                            validation_design = np.column_stack(
                                [
                                    np.log(validation_probability),
                                    -np.log1p(-validation_probability),
                                ]
                            )
                        calibrator = LogisticRegression(
                            C=float(model_spec.get("calibration_c", 1000.0)),
                            max_iter=200,
                        )
                        calibrator.fit(calibration_design, calibration_target)
                        probabilities = calibrator.predict_proba(validation_design)[:, 1]
                    elif method == "isotonic":
                        calibrator = IsotonicRegression(
                            y_min=0.0, y_max=1.0, out_of_bounds="clip"
                        )
                        calibrator.fit(calibration_probability, calibration_target)
                        probabilities = calibrator.predict(validation_probability)
                    else:
                        raise ValueError(f"지원하지 않는 확률 보정법입니다: {method}")
                    probabilities = np.clip(probabilities, 0.0, 1.0)
                    model = preprocessor = x_train = x_validation = None
                elif model_spec["family"] == "catboost_group_calibrated":
                    cache_key = json.dumps(
                        {
                            "features": features,
                            "categorical": categorical,
                            "cat_params": model_spec["cat_params"],
                            "cat_scale": model_spec.get("cat_scale", 1.0),
                            "cat_shift": model_spec.get("cat_shift", 0.0),
                        },
                        sort_keys=True,
                    )
                    cached = blend_component_cache.get(cache_key)
                    if cached is None:
                        calibration_season = int(validation_season) - 1
                        calibration_train_mask = train["season"].lt(
                            calibration_season
                        )
                        if protocol.get("train_start_season") is not None:
                            calibration_train_mask &= train["season"].ge(
                                int(protocol["train_start_season"])
                            )
                        calibration_mask = train["season"].eq(
                            calibration_season
                        )
                        preprocess_started = time.time()
                        full_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        full_train = full_preprocessor.fit_transform(
                            engineered.loc[train_mask, features]
                        )
                        full_validation = full_preprocessor.transform(
                            engineered.loc[validation_mask, features]
                        )
                        calibration_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        calibration_train = (
                            calibration_preprocessor.fit_transform(
                                engineered.loc[
                                    calibration_train_mask, features
                                ]
                            )
                        )
                        calibration_validation = (
                            calibration_preprocessor.transform(
                                engineered.loc[calibration_mask, features]
                            )
                        )
                        preprocess_seconds = time.time() - preprocess_started
                        component_spec = {
                            "family": "catboost",
                            "native_categorical": True,
                            "params": model_spec["cat_params"],
                        }
                        full_model = make_model(component_spec, categorical)
                        calibration_model = make_model(
                            component_spec, categorical
                        )
                        fit_started = time.time()
                        full_model.fit(
                            full_train,
                            train.loc[train_mask, "control_success"],
                        )
                        calibration_model.fit(
                            calibration_train,
                            train.loc[
                                calibration_train_mask, "control_success"
                            ],
                        )
                        fit_seconds = time.time() - fit_started

                        def transform_component(probability):
                            return np.clip(
                                0.5
                                + float(model_spec.get("cat_scale", 1.0))
                                * (probability - 0.5)
                                + float(model_spec.get("cat_shift", 0.0)),
                                0.0,
                                1.0,
                            )

                        cached = {
                            "validation_probability": transform_component(
                                predict_probability(
                                    full_model, full_validation
                                )
                            ),
                            "calibration_probability": transform_component(
                                predict_probability(
                                    calibration_model,
                                    calibration_validation,
                                )
                            ),
                            "calibration_index": np.flatnonzero(
                                calibration_mask.to_numpy()
                            ),
                            "validation_index": np.flatnonzero(
                                validation_mask.to_numpy()
                            ),
                            "preprocess_seconds": preprocess_seconds,
                            "fit_seconds": fit_seconds,
                        }
                        blend_component_cache[cache_key] = cached
                        del (
                            full_model,
                            calibration_model,
                            full_preprocessor,
                            calibration_preprocessor,
                            full_train,
                            full_validation,
                            calibration_train,
                            calibration_validation,
                        )
                    else:
                        preprocess_seconds = 0.0
                        fit_seconds = 0.0
                    group_columns = list(model_spec["group_columns"])
                    calibration_rows = train.iloc[
                        cached["calibration_index"]
                    ].loc[:, group_columns].copy()
                    residual = (
                        train.iloc[cached["calibration_index"]][
                            "control_success"
                        ].to_numpy()
                        - cached["calibration_probability"]
                    )
                    residual = residual - residual.mean()
                    calibration_rows["__residual"] = residual
                    stats = calibration_rows.groupby(
                        group_columns, dropna=False, observed=True
                    )["__residual"].agg(["sum", "count"])
                    stats["__offset"] = stats["sum"] / (
                        stats["count"]
                        + float(model_spec.get("group_shrinkage", 100.0))
                    )
                    validation_rows = train.iloc[
                        cached["validation_index"]
                    ].loc[:, group_columns]
                    if len(group_columns) == 1:
                        offsets = validation_rows[group_columns[0]].map(
                            stats["__offset"]
                        )
                    else:
                        keys = pd.MultiIndex.from_frame(validation_rows)
                        offsets = pd.Series(
                            stats["__offset"].reindex(keys).to_numpy(),
                            index=validation_rows.index,
                        )
                    probabilities = np.clip(
                        cached["validation_probability"]
                        + offsets.fillna(0.0).to_numpy(),
                        0.0,
                        1.0,
                    )
                    model = preprocessor = x_train = x_validation = None
                elif model_spec["family"] == "catboost_residual_correction":
                    cache_key = json.dumps(
                        {
                            "kind": "catboost_residual_correction",
                            "features": features,
                            "categorical": categorical,
                            "base_params": model_spec["base_params"],
                            "base_season_decay": model_spec.get(
                                "base_season_decay"
                            ),
                            "residual_params": model_spec["residual_params"],
                        },
                        sort_keys=True,
                    )
                    cached = blend_component_cache.get(cache_key)
                    if cached is None:
                        calibration_season = int(validation_season) - 1
                        calibration_train_mask = train["season"].lt(
                            calibration_season
                        )
                        if protocol.get("train_start_season") is not None:
                            calibration_train_mask &= train["season"].ge(
                                int(protocol["train_start_season"])
                            )
                        calibration_mask = train["season"].eq(
                            calibration_season
                        )
                        preprocess_started = time.time()
                        full_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        full_train = full_preprocessor.fit_transform(
                            engineered.loc[train_mask, features]
                        )
                        full_validation = full_preprocessor.transform(
                            engineered.loc[validation_mask, features]
                        )
                        calibration_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        calibration_train = calibration_preprocessor.fit_transform(
                            engineered.loc[calibration_train_mask, features]
                        )
                        calibration_validation = calibration_preprocessor.transform(
                            engineered.loc[calibration_mask, features]
                        )
                        preprocess_seconds = time.time() - preprocess_started
                        base_spec = {
                            "family": "catboost",
                            "native_categorical": True,
                            "params": model_spec["base_params"],
                        }
                        full_model = make_model(base_spec, categorical)
                        calibration_model = make_model(base_spec, categorical)

                        def decay_weights(mask: pd.Series) -> np.ndarray | None:
                            decay = model_spec.get("base_season_decay")
                            if decay is None:
                                return None
                            maximum = int(train.loc[mask, "season"].max())
                            return np.power(
                                float(decay),
                                maximum - train.loc[mask, "season"].to_numpy(),
                            )

                        fit_started = time.time()
                        full_model.fit(
                            full_train,
                            train.loc[train_mask, "control_success"],
                            sample_weight=decay_weights(train_mask),
                        )
                        calibration_model.fit(
                            calibration_train,
                            train.loc[
                                calibration_train_mask, "control_success"
                            ],
                            sample_weight=decay_weights(
                                calibration_train_mask
                            ),
                        )
                        calibration_probability = predict_probability(
                            calibration_model, calibration_validation
                        )
                        validation_probability = predict_probability(
                            full_model, full_validation
                        )
                        base_scale = float(model_spec.get("base_scale", 1.0))
                        base_shift = float(model_spec.get("base_shift", 0.0))
                        calibration_probability = np.clip(
                            0.5 + base_scale * (calibration_probability - 0.5)
                            + base_shift,
                            0.0,
                            1.0,
                        )
                        validation_probability = np.clip(
                            0.5 + base_scale * (validation_probability - 0.5)
                            + base_shift,
                            0.0,
                            1.0,
                        )
                        residual_target = (
                            train.loc[calibration_mask, "control_success"].to_numpy()
                            - calibration_probability
                        )
                        residual_model = make_model(
                            {
                                "family": "catboost_regressor",
                                "native_categorical": True,
                                "params": model_spec["residual_params"],
                            },
                            categorical,
                        )
                        residual_model.fit(
                            calibration_validation, residual_target
                        )
                        residual_prediction = np.asarray(
                            residual_model.predict(full_validation), dtype=float
                        )
                        fit_seconds = time.time() - fit_started
                        cached = {
                            "validation_probability": validation_probability,
                            "residual_prediction": residual_prediction,
                            "preprocess_seconds": preprocess_seconds,
                            "fit_seconds": fit_seconds,
                        }
                        blend_component_cache[cache_key] = cached
                        del (
                            full_model,
                            calibration_model,
                            residual_model,
                            full_preprocessor,
                            calibration_preprocessor,
                            full_train,
                            full_validation,
                            calibration_train,
                            calibration_validation,
                        )
                    else:
                        preprocess_seconds = 0.0
                        fit_seconds = 0.0
                    probabilities = np.clip(
                        cached["validation_probability"]
                        + float(model_spec["residual_weight"])
                        * cached["residual_prediction"],
                        0.0,
                        1.0,
                    )
                    model = preprocessor = x_train = x_validation = None
                elif model_spec["family"] == "cat_cpu_gpu_extra_blend":
                    cache_key = json.dumps(
                        {
                            "kind": "cat_cpu_gpu_extra_blend",
                            "features": features,
                            "categorical": categorical,
                            "cpu_params": model_spec["cpu_params"],
                            "gpu_params": model_spec["gpu_params"],
                            "extra_params": model_spec["extra_params"],
                            "hist_params": model_spec.get("hist_params"),
                            "season_decay": model_spec.get("season_decay"),
                        },
                        sort_keys=True,
                    )
                    cached = blend_component_cache.get(cache_key)
                    if cached is None:
                        preprocess_started = time.time()
                        cat_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        extra_preprocessor = make_preprocessor(
                            categorical, features
                        )
                        cat_train = cat_preprocessor.fit_transform(
                            engineered.loc[train_mask, features]
                        )
                        cat_validation = cat_preprocessor.transform(
                            engineered.loc[validation_mask, features]
                        )
                        extra_train = extra_preprocessor.fit_transform(
                            engineered.loc[train_mask, features]
                        )
                        extra_validation = extra_preprocessor.transform(
                            engineered.loc[validation_mask, features]
                        )
                        preprocess_seconds = time.time() - preprocess_started
                        cpu_model = make_model(
                            {
                                "family": "catboost",
                                "native_categorical": True,
                                "params": model_spec["cpu_params"],
                            },
                            categorical,
                        )
                        gpu_model = make_model(
                            {
                                "family": "catboost",
                                "native_categorical": True,
                                "params": model_spec["gpu_params"],
                            },
                            categorical,
                        )
                        extra_model = make_model(
                            {
                                "family": "extra_trees",
                                "params": model_spec["extra_params"],
                            },
                            categorical,
                        )
                        hist_model = None
                        if model_spec.get("hist_params") is not None:
                            hist_model = make_model(
                                {
                                    "family": "hist_gradient_boosting",
                                    "params": model_spec["hist_params"],
                                },
                                categorical,
                            )
                        sample_weight = None
                        if model_spec.get("season_decay") is not None:
                            maximum = int(train.loc[train_mask, "season"].max())
                            sample_weight = np.power(
                                float(model_spec["season_decay"]),
                                maximum
                                - train.loc[train_mask, "season"].to_numpy(),
                            )
                        target_train = train.loc[train_mask, "control_success"]
                        fit_started = time.time()
                        cpu_model.fit(
                            cat_train, target_train, sample_weight=sample_weight
                        )
                        gpu_model.fit(
                            cat_train, target_train, sample_weight=sample_weight
                        )
                        extra_model.fit(extra_train, target_train)
                        if hist_model is not None:
                            hist_model.fit(extra_train, target_train)
                        fit_seconds = time.time() - fit_started
                        cached = {
                            "cpu_probability": predict_probability(
                                cpu_model, cat_validation
                            ),
                            "gpu_probability": predict_probability(
                                gpu_model, cat_validation
                            ),
                            "extra_probability": predict_probability(
                                extra_model, extra_validation
                            ),
                            "preprocess_seconds": preprocess_seconds,
                            "fit_seconds": fit_seconds,
                        }
                        if hist_model is not None:
                            cached["hist_probability"] = predict_probability(
                                hist_model, extra_validation
                            )
                        blend_component_cache[cache_key] = cached
                        del (
                            cpu_model,
                            gpu_model,
                            extra_model,
                            hist_model,
                            cat_preprocessor,
                            extra_preprocessor,
                            cat_train,
                            cat_validation,
                            extra_train,
                            extra_validation,
                        )
                    else:
                        preprocess_seconds = 0.0
                        fit_seconds = 0.0
                    group_columns = list(model_spec.get("group_columns", []))
                    if (
                        group_columns
                        and "calibration_cpu_probability" not in cached
                    ):
                        calibration_season = int(validation_season) - 1
                        calibration_train_mask = train["season"].lt(
                            calibration_season
                        )
                        if protocol.get("train_start_season") is not None:
                            calibration_train_mask &= train["season"].ge(
                                int(protocol["train_start_season"])
                            )
                        calibration_mask = train["season"].eq(calibration_season)
                        calibration_preprocess_started = time.time()
                        calibration_cat_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        calibration_extra_preprocessor = make_preprocessor(
                            categorical, features
                        )
                        calibration_cat_train = (
                            calibration_cat_preprocessor.fit_transform(
                                engineered.loc[calibration_train_mask, features]
                            )
                        )
                        calibration_cat_validation = (
                            calibration_cat_preprocessor.transform(
                                engineered.loc[calibration_mask, features]
                            )
                        )
                        calibration_extra_train = (
                            calibration_extra_preprocessor.fit_transform(
                                engineered.loc[calibration_train_mask, features]
                            )
                        )
                        calibration_extra_validation = (
                            calibration_extra_preprocessor.transform(
                                engineered.loc[calibration_mask, features]
                            )
                        )
                        preprocess_seconds += (
                            time.time() - calibration_preprocess_started
                        )
                        calibration_cpu = make_model(
                            {
                                "family": "catboost",
                                "native_categorical": True,
                                "params": model_spec["cpu_params"],
                            },
                            categorical,
                        )
                        calibration_gpu = make_model(
                            {
                                "family": "catboost",
                                "native_categorical": True,
                                "params": model_spec["gpu_params"],
                            },
                            categorical,
                        )
                        calibration_extra = make_model(
                            {
                                "family": "extra_trees",
                                "params": model_spec["extra_params"],
                            },
                            categorical,
                        )
                        calibration_hist = None
                        if model_spec.get("hist_params") is not None:
                            calibration_hist = make_model(
                                {
                                    "family": "hist_gradient_boosting",
                                    "params": model_spec["hist_params"],
                                },
                                categorical,
                            )
                        calibration_weight = None
                        if model_spec.get("season_decay") is not None:
                            calibration_maximum = int(
                                train.loc[calibration_train_mask, "season"].max()
                            )
                            calibration_weight = np.power(
                                float(model_spec["season_decay"]),
                                calibration_maximum
                                - train.loc[
                                    calibration_train_mask, "season"
                                ].to_numpy(),
                            )
                        calibration_target = train.loc[
                            calibration_train_mask, "control_success"
                        ]
                        calibration_fit_started = time.time()
                        calibration_cpu.fit(
                            calibration_cat_train,
                            calibration_target,
                            sample_weight=calibration_weight,
                        )
                        calibration_gpu.fit(
                            calibration_cat_train,
                            calibration_target,
                            sample_weight=calibration_weight,
                        )
                        calibration_extra.fit(
                            calibration_extra_train, calibration_target
                        )
                        if calibration_hist is not None:
                            calibration_hist.fit(
                                calibration_extra_train, calibration_target
                            )
                        fit_seconds += time.time() - calibration_fit_started

                        cached["calibration_cpu_probability"] = (
                            predict_probability(
                                calibration_cpu, calibration_cat_validation
                            )
                        )
                        cached["calibration_gpu_probability"] = (
                            predict_probability(
                                calibration_gpu, calibration_cat_validation
                            )
                        )
                        cached["calibration_extra_probability"] = (
                            predict_probability(
                                calibration_extra,
                                calibration_extra_validation,
                            )
                        )
                        if calibration_hist is not None:
                            cached["calibration_hist_probability"] = (
                                predict_probability(
                                    calibration_hist,
                                    calibration_extra_validation,
                                )
                            )
                        cached["calibration_index"] = np.flatnonzero(
                            calibration_mask.to_numpy()
                        )
                        cached["validation_index"] = np.flatnonzero(
                            validation_mask.to_numpy()
                        )
                        del (
                            calibration_cpu,
                            calibration_gpu,
                            calibration_extra,
                            calibration_hist,
                            calibration_cat_preprocessor,
                            calibration_extra_preprocessor,
                            calibration_cat_train,
                            calibration_cat_validation,
                            calibration_extra_train,
                            calibration_extra_validation,
                        )
                    effective_model_spec = model_spec
                    learned_strength = float(
                        model_spec.get("learned_weight_strength", 0.0)
                    )
                    if learned_strength:
                        component_names = ["cpu", "gpu", "extra"]
                        if "hist_weight" in model_spec:
                            component_names.append("hist")
                        calibration_components = []
                        for selected_component in component_names:
                            basis_spec = dict(model_spec)
                            for component in component_names:
                                basis_spec[f"{component}_weight"] = float(
                                    component == selected_component
                                )
                            calibration_components.append(
                                _blend_cached_probabilities(
                                    cached, basis_spec, prefix="calibration_"
                                )
                            )
                        learned_weights = _learn_simplex_blend_weights(
                            np.column_stack(calibration_components),
                            train.iloc[cached["calibration_index"]][
                                "control_success"
                            ].to_numpy(),
                        )
                        effective_model_spec = dict(model_spec)
                        for index, component in enumerate(component_names):
                            manual = float(model_spec[f"{component}_weight"])
                            effective = (
                                (1.0 - learned_strength) * manual
                                + learned_strength * learned_weights[index]
                            )
                            effective_model_spec[f"{component}_weight"] = effective
                            variant_diagnostics[f"effective_{component}_weight"] = (
                                effective
                            )
                    probabilities = _blend_cached_probabilities(
                        cached, effective_model_spec
                    )
                    if group_columns:
                        calibration_probability = _blend_cached_probabilities(
                            cached, effective_model_spec, prefix="calibration_"
                        )
                        calibration_rows = train.iloc[
                            cached["calibration_index"]
                        ].loc[:, group_columns].copy()
                        residual = (
                            train.iloc[cached["calibration_index"]][
                                "control_success"
                            ].to_numpy()
                            - calibration_probability
                        )
                        if bool(model_spec.get("center_residual", True)):
                            residual = residual - residual.mean()
                        calibration_rows["__residual"] = residual
                        stats = calibration_rows.groupby(
                            group_columns, dropna=False, observed=True
                        )["__residual"].agg(["sum", "count"])
                        stats["__offset"] = (
                            float(model_spec.get("residual_scale", 1.0))
                            * stats["sum"]
                            / (
                                stats["count"]
                                + float(model_spec.get("group_shrinkage", 1000.0))
                            )
                        )
                        validation_rows = train.iloc[
                            cached["validation_index"]
                        ].loc[:, group_columns]
                        if len(group_columns) == 1:
                            offsets = validation_rows[group_columns[0]].map(
                                stats["__offset"]
                            )
                        else:
                            keys = pd.MultiIndex.from_frame(validation_rows)
                            offsets = pd.Series(
                                stats["__offset"].reindex(keys).to_numpy(),
                                index=validation_rows.index,
                            )
                        probabilities = np.clip(
                            probabilities + offsets.fillna(0.0).to_numpy(),
                            0.0,
                            1.0,
                        )
                    trend_group_columns = list(
                        model_spec.get("trend_group_columns", [])
                    )
                    trend_strength = float(model_spec.get("trend_strength", 0.0))
                    if trend_group_columns and trend_strength:
                        trend_offsets = _learn_centered_group_trend_offsets(
                            train.loc[train_mask],
                            train.loc[train_mask, "control_success"],
                            trend_group_columns,
                            shrinkage=float(
                                model_spec.get("trend_shrinkage", 10_000.0)
                            ),
                            method=str(model_spec.get("trend_method", "wls")),
                        )
                        validation_rows = train.loc[
                            validation_mask, trend_group_columns
                        ]
                        if len(trend_group_columns) == 1:
                            trend_values = validation_rows[
                                trend_group_columns[0]
                            ].map(trend_offsets)
                        else:
                            trend_keys = pd.MultiIndex.from_frame(validation_rows)
                            trend_values = pd.Series(
                                trend_offsets.reindex(trend_keys).to_numpy(),
                                index=validation_rows.index,
                            )
                        probabilities = np.clip(
                            probabilities
                            + trend_strength
                            * trend_values.fillna(0.0).to_numpy(),
                            0.0,
                            1.0,
                        )
                        variant_diagnostics["trend_offset_mean"] = float(
                            trend_values.fillna(0.0).mean()
                        )
                        variant_diagnostics["trend_offset_abs_mean"] = float(
                            trend_values.fillna(0.0).abs().mean()
                        )
                    model = preprocessor = x_train = x_validation = None
                elif model_spec["family"] == "cat_extra_blend":
                    cache_key = json.dumps(
                        {
                            "features": features,
                            "categorical": categorical,
                            "cat_params": model_spec["cat_params"],
                            "extra_params": model_spec["extra_params"],
                        },
                        sort_keys=True,
                    )
                    cached = blend_component_cache.get(cache_key)
                    if cached is None:
                        preprocess_started = time.time()
                        cat_preprocessor = make_preprocessor(
                            categorical, features, native_categorical=True
                        )
                        extra_preprocessor = make_preprocessor(
                            categorical, features
                        )
                        cat_train = cat_preprocessor.fit_transform(
                            engineered.loc[train_mask, features]
                        )
                        cat_validation = cat_preprocessor.transform(
                            engineered.loc[validation_mask, features]
                        )
                        extra_train = extra_preprocessor.fit_transform(
                            engineered.loc[train_mask, features]
                        )
                        extra_validation = extra_preprocessor.transform(
                            engineered.loc[validation_mask, features]
                        )
                        preprocess_seconds = time.time() - preprocess_started
                        cat_model = make_model(
                            {
                                "family": "catboost",
                                "native_categorical": True,
                                "params": model_spec["cat_params"],
                            },
                            categorical,
                        )
                        extra_model = make_model(
                            {
                                "family": "extra_trees",
                                "params": model_spec["extra_params"],
                            },
                            categorical,
                        )
                        fit_started = time.time()
                        target_train = train.loc[
                            train_mask, "control_success"
                        ]
                        cat_fit_kwargs: dict[str, Any] = {}
                        cat_season_decay = model_spec.get("cat_season_decay")
                        if cat_season_decay is not None:
                            max_training_season = int(
                                train.loc[train_mask, "season"].max()
                            )
                            cat_fit_kwargs["sample_weight"] = np.power(
                                float(cat_season_decay),
                                max_training_season
                                - train.loc[train_mask, "season"].to_numpy(),
                            )
                        cat_model.fit(
                            cat_train, target_train, **cat_fit_kwargs
                        )
                        extra_model.fit(extra_train, target_train)
                        fit_seconds = time.time() - fit_started
                        cat_probability = predict_probability(
                            cat_model, cat_validation
                        )
                        cat_probability = np.clip(
                            0.5
                            + float(model_spec.get("cat_scale", 1.0))
                            * (cat_probability - 0.5)
                            + float(model_spec.get("cat_shift", 0.0)),
                            0.0,
                            1.0,
                        )
                        extra_probability = np.clip(
                            predict_probability(extra_model, extra_validation)
                            + float(model_spec.get("extra_shift", 0.0)),
                            0.0,
                            1.0,
                        )
                        cached = {
                            "cat_probability": cat_probability,
                            "extra_probability": extra_probability,
                            "preprocess_seconds": preprocess_seconds,
                            "fit_seconds": fit_seconds,
                        }
                        blend_component_cache[cache_key] = cached
                        del (
                            cat_model,
                            extra_model,
                            cat_preprocessor,
                            extra_preprocessor,
                            cat_train,
                            cat_validation,
                            extra_train,
                            extra_validation,
                        )
                    else:
                        preprocess_seconds = 0.0
                        fit_seconds = 0.0
                    extra_weight = float(model_spec["extra_weight"])
                    probabilities = (
                        (1.0 - extra_weight) * cached["cat_probability"]
                        + extra_weight * cached["extra_probability"]
                    )
                    model = preprocessor = x_train = x_validation = None
                else:
                    native_categorical = bool(
                        model_spec.get("native_categorical", False)
                    )
                    preprocessor = make_preprocessor(
                        categorical,
                        features,
                        native_categorical=native_categorical,
                        linear=model_spec["family"] == "logistic_regression",
                    )
                    preprocess_started = time.time()
                    x_train = preprocessor.fit_transform(
                        engineered.loc[train_mask, features]
                    )
                    x_validation = preprocessor.transform(
                        engineered.loc[validation_mask, features]
                    )
                    preprocess_seconds = time.time() - preprocess_started

                    model = make_model(model_spec, categorical)
                    fit_started = time.time()
                    fit_kwargs: dict[str, Any] = {}
                    season_decay = model_spec.get("season_decay")
                    if season_decay is not None:
                        max_training_season = int(
                            train.loc[train_mask, "season"].max()
                        )
                        fit_kwargs["sample_weight"] = np.power(
                            float(season_decay),
                            max_training_season
                            - train.loc[train_mask, "season"].to_numpy(),
                        )
                    model.fit(
                        x_train,
                        train.loc[train_mask, "control_success"],
                        **fit_kwargs,
                    )
                    fit_seconds = time.time() - fit_started
                    probabilities = predict_probability(model, x_validation)
                prediction_scale = float(
                    model_spec.get("prediction_scale", 1.0)
                )
                if prediction_scale != 1.0:
                    probabilities = 0.5 + prediction_scale * (
                        probabilities - 0.5
                    )
                prediction_shift = float(
                    model_spec.get("prediction_shift", 0.0)
                )
                if prediction_shift or prediction_scale != 1.0:
                    probabilities = np.clip(
                        probabilities + prediction_shift, 0.0, 1.0
                    )
                metrics = probability_metrics(
                    train.loc[validation_mask, "control_success"].to_numpy(),
                    probabilities,
                )
                metrics.update(variant_diagnostics)
                metrics.update(
                    {
                        "validation_season": int(validation_season),
                        "training_seasons": "-".join(
                            map(
                                str,
                                sorted(train.loc[train_mask, "season"].unique()),
                            )
                        ),
                        "success_prior": success_prior,
                        "feature_count": len(features),
                        "categorical_count": len(categorical),
                        "preprocess_seconds": preprocess_seconds,
                        "fit_seconds": fit_seconds,
                    }
                )
                fold_results[name].append(metrics)
                fold_frame = pd.DataFrame(fold_results[name])
                fold_frame.to_csv(
                    run_dir / name / "fold_metrics.csv", index=False
                )
                if save_predictions:
                    prediction = pd.DataFrame(
                        {
                            "row_id": train.loc[validation_mask, "row_id"].to_numpy(),
                            "validation_season": int(validation_season),
                            "target": train.loc[
                                validation_mask, "control_success"
                            ].to_numpy(),
                            "probability": probabilities,
                        }
                    )
                    prediction.to_csv(
                        run_dir
                        / name
                        / f"predictions_{validation_season}.csv.gz",
                        index=False,
                        compression="gzip",
                    )
                del model, preprocessor, x_train, x_validation, probabilities
                gc.collect()
            del engineered
            gc.collect()

        summaries = []
        for variant in selected_variants:
            fold_frame = pd.DataFrame(fold_results[variant["name"]])
            summary = _variant_summary(variant, fold_frame)
            summaries.append(summary)
            write_json(run_dir / variant["name"] / "summary.json", summary)

        leaderboard = pd.DataFrame(summaries)
        control_name = resolved["study"]["control"]
        control_row = leaderboard.loc[leaderboard["variant"] == control_name]
        if control_row.empty:
            raise RuntimeError("선택 실행에 control 결과가 없습니다.")
        control_mean = float(control_row.iloc[0]["mean_brier"])
        leaderboard["delta_brier_vs_control"] = (
            leaderboard["mean_brier"] - control_mean
        )
        control_folds = pd.DataFrame(fold_results[control_name]).set_index(
            "validation_season"
        )
        improved = {}
        for variant in selected_variants:
            folds = pd.DataFrame(fold_results[variant["name"]]).set_index(
                "validation_season"
            )
            comparison = folds["brier"] < control_folds["brier"]
            improved[variant["name"]] = f"{int(comparison.sum())}/{len(comparison)}"
        leaderboard["seasons_improved"] = leaderboard["variant"].map(improved)
        leaderboard = leaderboard.sort_values(["mean_brier", "variant"])
        leaderboard.to_csv(run_dir / "leaderboard.csv", index=False)
        report = render_study_report(resolved, leaderboard, run_dir)
        (run_dir / "report.md").write_text(report, encoding="utf-8")

        metadata.update(
            {
                "status": "complete",
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "elapsed_seconds": time.time() - started,
                "run_dir": str(run_dir),
            }
        )
        write_json(run_dir / "metadata.json", metadata)
        return run_dir
    except Exception as error:
        metadata.update(
            {
                "status": "failed",
                "failed_at_utc": datetime.now(timezone.utc).isoformat(),
                "elapsed_seconds": time.time() - started,
                "error_type": type(error).__name__,
                "error": str(error),
            }
        )
        write_json(run_dir / "metadata.json", metadata)
        raise
