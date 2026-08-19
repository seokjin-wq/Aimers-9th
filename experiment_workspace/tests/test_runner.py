from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from aimers_exp.builder import (
    _safe_features_runtime_script,
    build_final_package,
    validate_package,
)
from aimers_exp.runner import (
    _blend_cached_probabilities,
    _learn_centered_group_trend_offsets,
    _learn_simplex_blend_weights,
    run_study,
)


def raw47_spec() -> dict:
    return {
        "name": "raw47",
        "description": "test",
        "include_all_raw": True,
        "exclude": [],
        "custom": [],
        "categorical": ["top_bottom", "game_type", "base_state"],
        "expected_count": 47,
    }


def small_rf_model() -> dict:
    return {
        "name": "small_rf",
        "family": "random_forest",
        "params": {
            "n_estimators": 3,
            "max_depth": 3,
            "min_samples_leaf": 1,
            "n_jobs": 1,
            "random_state": 42,
        },
    }


def test_cached_blend_applies_each_variants_postprocessing() -> None:
    cached = {
        "cpu_probability": pd.Series([0.4, 0.6]).to_numpy(),
        "gpu_probability": pd.Series([0.3, 0.7]).to_numpy(),
        "extra_probability": pd.Series([0.45, 0.55]).to_numpy(),
    }
    common = {
        "cpu_weight": 0.45,
        "gpu_weight": 0.40,
        "extra_weight": 0.15,
        "cat_scale": 1.06,
        "extra_shift": -0.01,
    }
    first = _blend_cached_probabilities(
        cached, {**common, "cat_shift": -0.008}
    )
    second = _blend_cached_probabilities(
        cached, {**common, "cat_shift": -0.010}
    )
    expected_delta = 0.002 * (common["cpu_weight"] + common["gpu_weight"])
    assert np.allclose(first - second, expected_delta)


def test_cached_blend_supports_optional_hist_component() -> None:
    cached = {
        "cpu_probability": np.array([0.4, 0.6]),
        "gpu_probability": np.array([0.3, 0.7]),
        "extra_probability": np.array([0.45, 0.55]),
        "hist_probability": np.array([0.2, 0.8]),
    }
    spec = {
        "cpu_weight": 0.50,
        "gpu_weight": 0.35,
        "extra_weight": 0.10,
        "hist_weight": 0.05,
        "cat_scale": 1.0,
        "cat_shift": 0.0,
        "extra_shift": 0.0,
        "hist_shift": 0.0,
    }
    result = _blend_cached_probabilities(cached, spec)
    expected = (
        0.50 * cached["cpu_probability"]
        + 0.35 * cached["gpu_probability"]
        + 0.10 * cached["extra_probability"]
        + 0.05 * cached["hist_probability"]
    )
    assert np.allclose(result, expected)


def test_simplex_blend_weight_learning_recovers_convex_mix() -> None:
    components = np.array(
        [[0.1, 0.7, 0.4], [0.8, 0.2, 0.5], [0.3, 0.9, 0.6], [0.7, 0.1, 0.2]]
    )
    expected = np.array([0.6, 0.3, 0.1])
    target = components @ expected
    learned = _learn_simplex_blend_weights(components, target)
    assert np.all(learned >= 0.0)
    assert np.isclose(learned.sum(), 1.0)
    assert np.allclose(components @ learned, target)


def test_centered_group_trend_ignores_global_season_drift() -> None:
    rows = pd.DataFrame(
        {
            "season": np.repeat([2020, 2021, 2022], 4),
            "count": ["a", "a", "b", "b"] * 3,
        }
    )
    target = pd.Series(
        [0.4, 0.4, 0.6, 0.6, 0.3, 0.3, 0.7, 0.7, 0.2, 0.2, 0.8, 0.8]
    )
    offsets = _learn_centered_group_trend_offsets(
        rows, target, ["count"], shrinkage=0.0
    )
    assert np.isclose(offsets.loc["a"], -0.1)
    assert np.isclose(offsets.loc["b"], 0.1)


def test_centered_group_trend_supports_endpoint_method() -> None:
    rows = pd.DataFrame(
        {"season": [2020, 2021, 2022] * 2, "group": ["a"] * 3 + ["b"] * 3}
    )
    target = pd.Series([0.4, 0.7, 0.2, 0.6, 0.3, 0.8])
    offsets = _learn_centered_group_trend_offsets(
        rows, target, ["group"], shrinkage=0.0, method="endpoint"
    )
    assert np.isclose(offsets.loc["a"], -0.1)
    assert np.isclose(offsets.loc["b"], 0.1)


def test_small_study_writes_reproducible_artifacts(
    synthetic_data_dir: Path, tmp_path: Path
) -> None:
    variant = {
        "name": "control",
        "change": "control",
        "model": small_rf_model(),
        "features": raw47_spec(),
        "changed_fields_vs_control": [],
    }
    resolved = {
        "study": {
            "id": "test_study",
            "description": "test",
            "hypothesis": "test",
            "control": "control",
            "change_scope": ["features"],
        },
        "protocol": {
            "validation_seasons": [2022],
            "split_rule": "before_validation_season",
            "calibration": "none",
            "store_predictions": False,
        },
        "variants": [variant],
        "config_hash": "testhash",
    }
    run_dir = run_study(
        resolved,
        data_dir=synthetic_data_dir,
        runs_root=tmp_path / "runs",
    )
    assert (run_dir / "leaderboard.csv").is_file()
    assert (run_dir / "report.md").is_file()
    assert (run_dir / "control/fold_metrics.csv").is_file()
    metadata = json.loads((run_dir / "metadata.json").read_text())
    assert metadata["status"] == "complete"
    leaderboard = pd.read_csv(run_dir / "leaderboard.csv")
    assert leaderboard.loc[0, "delta_brier_vs_control"] == 0.0


def test_small_final_package_runs_independently(
    synthetic_data_dir: Path, tmp_path: Path
) -> None:
    model = {
        "name": "small_catboost",
        "family": "catboost",
        "prediction_scale": 1.06,
        "prediction_shift": -0.008,
        "params": {
            "iterations": 2,
            "depth": 2,
            "learning_rate": 0.1,
            "random_seed": 42,
            "thread_count": 1,
            "allow_writing_files": False,
            "verbose": False,
        },
    }
    resolved = {
        "final": {
            "name": "test_final",
            "provenance_repository": "Aimers-9th",
            "provenance_commit": "349498b",
            "calibration_method": "none",
            "calibration_shift": 0.0,
            "calibration_source_seasons": [],
            "uses_test_distribution": False,
        },
        "protocol": {},
        "model": model,
        "features": raw47_spec(),
        "config_hash": "testfinal",
    }
    output = tmp_path / "final"
    build = build_final_package(
        resolved, data_dir=synthetic_data_dir, output_dir=output
    )
    assert build["feature_count"] == 47
    calibration = json.loads(
        (output / "package/model/calibration.json").read_text()
    )
    assert calibration["prediction_scale"] == 1.06
    assert calibration["prediction_shift"] == -0.008
    validation = validate_package(
        data_dir=synthetic_data_dir,
        zip_path=output / "submit.zip",
        sample_rows=5,
    )
    assert validation["status"] == "success"


def test_submission_runtime_excludes_cross_row_feature_code() -> None:
    source = _safe_features_runtime_script(
        ["count_diff", "pitcher_season_success_rate_k20"]
    )
    compile(source, "features_runtime.py", "exec")
    forbidden_operations = (
        ".groupby(", ".rolling(", ".shift(", ".ewm(", ".diff("
    )
    for forbidden in forbidden_operations:
        assert forbidden not in source
