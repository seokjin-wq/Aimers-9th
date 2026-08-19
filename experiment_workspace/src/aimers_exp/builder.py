from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any

import catboost
import joblib
import numpy as np
import pandas as pd
import sklearn

from .config import PROJECT_ROOT
from .features import (
    apply_official_state_reference,
    build_official_state_reference,
    engineer_features,
    engineer_official_train_state_features,
    resolve_feature_names,
)
from .modeling import make_model, make_preprocessor, predict_probability
from .runner import (
    _learn_centered_group_trend_offsets,
    read_training_data,
    sha256_file,
    source_tree_hash,
    validate_data_dir,
    write_json,
)


def _triple_inference_script(custom_features: list[str]) -> str:
    core = '''from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
ID_COL = "row_id"
TARGET_COL = "control_success"


def map_offset(frame: pd.DataFrame, columns: list[str], values: pd.Series) -> np.ndarray:
    if not columns:
        return np.zeros(len(frame), dtype=float)
    if len(columns) == 1:
        mapped = frame[columns[0]].map(values)
    else:
        keys = pd.MultiIndex.from_frame(frame.loc[:, columns])
        mapped = pd.Series(values.reindex(keys).to_numpy(), index=frame.index)
    return mapped.fillna(0.0).to_numpy(dtype=float)


def main() -> None:
    data_dir = ROOT / "data"
    test = pd.read_csv(data_dir / "test.csv")
    sample = pd.read_csv(data_dir / "sample_submission.csv")
    bundle = joblib.load(ROOT / "model" / "model.joblib")
    frame = engineer_features(
        test,
        success_prior=float(bundle["success_prior"]),
        shrinkage_k=float(bundle["shrinkage_k"]),
        requested_custom=bundle["custom_features"],
    )
    frame = apply_official_state_reference(
        frame,
        bundle["state_reference"],
        requested=bundle["custom_features"],
        shrinkage_k=float(bundle["shrinkage_k"]),
    )
    selected = frame.loc[:, bundle["features"]]
    cat_matrix = selected.copy()
    for column in bundle["categorical"]:
        cat_matrix[column] = cat_matrix[column].fillna("__MISSING__").astype(str)
    numeric = bundle["cat_numeric"]
    cat_matrix.loc[:, numeric] = (
        cat_matrix.loc[:, numeric]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(bundle["cat_medians"])
        .astype("float32")
    )
    extra_matrix = bundle["extra_preprocessor"].transform(selected)
    spec = bundle["model_spec"]

    def adjusted_cat(model) -> np.ndarray:
        raw = model.predict_proba(cat_matrix)[:, 1]
        return np.clip(
            0.5 + float(spec.get("cat_scale", 1.0)) * (raw - 0.5)
            + float(spec.get("cat_shift", 0.0)),
            0.0, 1.0,
        )

    probability = (
        float(spec["cpu_weight"]) * adjusted_cat(bundle["cpu_model"])
        + float(spec["gpu_weight"]) * adjusted_cat(bundle["gpu_model"])
        + float(spec["extra_weight"]) * np.clip(
            bundle["extra_model"].predict_proba(extra_matrix)[:, 1]
            + float(spec.get("extra_shift", 0.0)),
            0.0, 1.0,
        )
    )
    probability += map_offset(
        frame, bundle["group_columns"], bundle["group_offsets"]
    )
    probability += float(spec.get("trend_strength", 0.0)) * map_offset(
        frame, bundle["trend_group_columns"], bundle["trend_offsets"]
    )
    probability = np.clip(probability, 0.0, 1.0)

    prediction = pd.DataFrame({ID_COL: test[ID_COL], TARGET_COL: probability})
    submission = sample[[ID_COL]].merge(
        prediction, on=ID_COL, how="left", validate="one_to_one"
    )
    if submission[ID_COL].tolist() != sample[ID_COL].tolist():
        raise RuntimeError("sample_submission의 row_id 순서를 보존하지 못했습니다.")
    if submission[TARGET_COL].isna().any():
        raise RuntimeError("예측값에 결측값이 있습니다.")
    if not submission[TARGET_COL].between(0.0, 1.0).all():
        raise RuntimeError("예측 확률 범위를 벗어났습니다.")
    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    submission.to_csv(output_dir / "submission.csv", index=False)


if __name__ == "__main__":
    main()
'''
    return _safe_features_runtime_script(custom_features) + "\n\n" + core


def _inference_script() -> str:
    return '''from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from features_runtime import engineer_features

ROOT = Path(__file__).resolve().parent
ID_COL = "row_id"
TARGET_COL = "control_success"


def main() -> None:
    data_dir = ROOT / "data"
    test = pd.read_csv(data_dir / "test.csv")
    sample = pd.read_csv(data_dir / "sample_submission.csv")
    bundle = joblib.load(ROOT / "model" / "model.joblib")
    calibration = json.loads(
        (ROOT / "model" / "calibration.json").read_text(encoding="utf-8")
    )
    frame = engineer_features(
        test,
        success_prior=float(bundle["success_prior"]),
        shrinkage_k=float(bundle["shrinkage_k"]),
        requested_custom=bundle["custom_features"],
    )
    matrix = bundle["preprocessor"].transform(frame.loc[:, bundle["features"]])
    probability = bundle["model"].predict_proba(matrix)[:, 1]
    prediction_scale = float(calibration.get("prediction_scale", 1.0))
    probability = 0.5 + prediction_scale * (probability - 0.5)
    probability = np.clip(
        probability
        + float(calibration.get("prediction_shift", 0.0))
        + float(calibration["shift"]),
        0.0,
        1.0,
    )

    prediction = pd.DataFrame({ID_COL: test[ID_COL], TARGET_COL: probability})
    submission = sample[[ID_COL]].merge(
        prediction, on=ID_COL, how="left", validate="one_to_one"
    )
    if submission[ID_COL].tolist() != sample[ID_COL].tolist():
        raise RuntimeError("sample_submission의 row_id 순서를 보존하지 못했습니다.")
    if submission[TARGET_COL].isna().any():
        raise RuntimeError("예측값에 결측값이 있습니다.")
    if not submission[TARGET_COL].between(0.0, 1.0).all():
        raise RuntimeError("예측 확률 범위를 벗어났습니다.")
    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    submission.to_csv(output_dir / "submission.csv", index=False)


if __name__ == "__main__":
    main()
'''


def _modeling_runtime_script() -> str:
    """Minimal module required to unpickle the native CatBoost preprocessor."""
    return '''from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class NativeCatBoostPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, categorical: list[str], features: list[str]):
        self.categorical = categorical
        self.features = features

    def fit(self, frame: pd.DataFrame, target=None):
        numeric = [
            column for column in self.features if column not in self.categorical
        ]
        self.numeric_ = numeric
        self.medians_ = (
            frame.loc[:, numeric].apply(pd.to_numeric, errors="coerce").median()
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
'''


def _safe_features_runtime_script(custom_features: list[str]) -> str:
    """Create a submission-only feature module with no cross-row code."""
    source = Path(__file__).with_name("features.py").read_text(encoding="utf-8")
    safe_start = source.index("def _safe_rate(")
    safe_end = source.index("    row_number = pd.to_numeric(", safe_start)
    state_start = source.index("def apply_official_state_reference(")
    state_end = source.index(
        "def engineer_official_train_progress_features(", state_start
    )
    declared = repr(tuple(custom_features))
    return (
        "from __future__ import annotations\n\n"
        "from collections.abc import Collection\n"
        "from typing import Any\n\n"
        "import numpy as np\n"
        "import pandas as pd\n\n"
        f"CUSTOM_FEATURES = frozenset({declared})\n"
        f"ROW_LOCAL_CUSTOM_FEATURES = {declared}\n"
        "SEQUENTIAL_FEATURES = frozenset()\n"
        f"REFERENCE_STATE_FEATURES = frozenset({declared})\n\n"
        + source[safe_start:safe_end]
        + "\n"
        + source[state_start:state_end]
    )


def _fit_triple_components(
    engineered: pd.DataFrame,
    target: pd.Series,
    seasons: pd.Series,
    mask: pd.Series,
    features: list[str],
    categorical: list[str],
    spec: dict[str, Any],
) -> tuple[Any, Any, Any, Any, Any]:
    cat_preprocessor = make_preprocessor(
        categorical, features, native_categorical=True
    )
    extra_preprocessor = make_preprocessor(categorical, features)
    selected = engineered.loc[mask, features]
    cat_matrix = cat_preprocessor.fit_transform(selected)
    extra_matrix = extra_preprocessor.fit_transform(selected)
    cpu_model = make_model(
        {
            "family": "catboost",
            "native_categorical": True,
            "params": spec["cpu_params"],
        },
        categorical,
    )
    gpu_model = make_model(
        {
            "family": "catboost",
            "native_categorical": True,
            "params": spec["gpu_params"],
        },
        categorical,
    )
    extra_model = make_model(
        {"family": "extra_trees", "params": spec["extra_params"]}, categorical
    )
    sample_weight = None
    if spec.get("season_decay") is not None:
        selected_seasons = seasons.loc[mask].to_numpy()
        sample_weight = np.power(
            float(spec["season_decay"]), int(selected_seasons.max()) - selected_seasons
        )
    selected_target = target.loc[mask]
    cpu_model.fit(cat_matrix, selected_target, sample_weight=sample_weight)
    gpu_model.fit(cat_matrix, selected_target, sample_weight=sample_weight)
    extra_model.fit(extra_matrix, selected_target)
    return (
        cat_preprocessor,
        extra_preprocessor,
        cpu_model,
        gpu_model,
        extra_model,
    )


def _triple_probability(
    components: tuple[Any, Any, Any, Any, Any],
    frame: pd.DataFrame,
    features: list[str],
    spec: dict[str, Any],
) -> np.ndarray:
    cat_preprocessor, extra_preprocessor, cpu_model, gpu_model, extra_model = components
    selected = frame.loc[:, features]
    cat_matrix = cat_preprocessor.transform(selected)
    extra_matrix = extra_preprocessor.transform(selected)
    scale = float(spec.get("cat_scale", 1.0))
    shift = float(spec.get("cat_shift", 0.0))

    def adjusted(model: Any) -> np.ndarray:
        raw = predict_probability(model, cat_matrix)
        return np.clip(0.5 + scale * (raw - 0.5) + shift, 0.0, 1.0)

    return (
        float(spec["cpu_weight"]) * adjusted(cpu_model)
        + float(spec["gpu_weight"]) * adjusted(gpu_model)
        + float(spec["extra_weight"])
        * np.clip(
            predict_probability(extra_model, extra_matrix)
            + float(spec.get("extra_shift", 0.0)),
            0.0,
            1.0,
        )
    )


def _build_triple_final_package(
    resolved: dict[str, Any],
    *,
    data_path: Path,
    output: Path,
    package: Path,
    model_dir: Path,
) -> dict[str, Any]:
    train, raw_columns = read_training_data(data_path)
    raw = train.drop(columns=["control_success"])
    target = train["control_success"]
    seasons = pd.to_numeric(train["season"], errors="raise")
    features, categorical = resolve_feature_names(raw_columns, resolved["features"])
    custom = resolved["features"].get("custom", [])
    success_prior = float(target.mean())
    engineered = engineer_features(
        raw, success_prior=success_prior, requested_custom=custom
    )
    all_mask = pd.Series(True, index=train.index)
    no_apply = pd.Series(False, index=train.index)
    engineered = engineer_official_train_state_features(
        engineered,
        target,
        reference_mask=all_mask,
        apply_mask=no_apply,
        requested=custom,
    )
    state_reference = build_official_state_reference(
        engineered, requested=custom
    )
    spec = resolved["model"]

    fit_started = time.time()
    full_components = _fit_triple_components(
        engineered, target, seasons, all_mask, features, categorical, spec
    )
    calibration_season = int(seasons.max())
    calibration_train_mask = seasons.lt(calibration_season)
    calibration_mask = seasons.eq(calibration_season)
    calibration_components = _fit_triple_components(
        engineered,
        target,
        seasons,
        calibration_train_mask,
        features,
        categorical,
        spec,
    )
    calibration_probability = _triple_probability(
        calibration_components,
        engineered.loc[calibration_mask],
        features,
        spec,
    )
    group_columns = list(spec.get("group_columns", []))
    calibration_rows = train.loc[calibration_mask, group_columns].copy()
    residual = target.loc[calibration_mask].to_numpy() - calibration_probability
    if bool(spec.get("center_residual", True)):
        residual -= residual.mean()
    calibration_rows["__residual"] = residual
    group_stats = calibration_rows.groupby(
        group_columns, dropna=False, observed=True
    )["__residual"].agg(["sum", "count"])
    group_offsets = (
        float(spec.get("residual_scale", 1.0))
        * group_stats["sum"]
        / (group_stats["count"] + float(spec.get("group_shrinkage", 1000.0)))
    )
    trend_group_columns = list(spec.get("trend_group_columns", []))
    trend_offsets = _learn_centered_group_trend_offsets(
        train,
        target,
        trend_group_columns,
        shrinkage=float(spec.get("trend_shrinkage", 10_000.0)),
        method=str(spec.get("trend_method", "wls")),
    )
    fit_seconds = time.time() - fit_started
    del calibration_components

    cat_preprocessor, extra_preprocessor, cpu_model, gpu_model, extra_model = (
        full_components
    )
    bundle = {
        "config_hash": resolved["config_hash"],
        "features": features,
        "categorical": categorical,
        "custom_features": custom,
        "success_prior": success_prior,
        "shrinkage_k": 50.0,
        "state_reference": state_reference,
        "cat_numeric": list(cat_preprocessor.numeric_),
        "cat_medians": cat_preprocessor.medians_,
        "extra_preprocessor": extra_preprocessor,
        "cpu_model": cpu_model,
        "gpu_model": gpu_model,
        "extra_model": extra_model,
        "model_spec": spec,
        "group_columns": group_columns,
        "group_offsets": group_offsets,
        "trend_group_columns": trend_group_columns,
        "trend_offsets": trend_offsets,
    }
    model_path = model_dir / "model.joblib"
    joblib.dump(bundle, model_path, compress=3)
    calibration = {
        "method": "official_train_oot_group_residual_plus_centered_season_trend",
        "source_season": calibration_season,
        "uses_test_distribution": False,
        "row_independent_inference": True,
    }
    write_json(model_dir / "calibration.json", calibration)
    (package / "script.py").write_text(
        _triple_inference_script(custom), encoding="utf-8"
    )
    requirements = [f"catboost=={catboost.__version__}"]
    (package / "requirements.txt").write_text(
        "\n".join(requirements) + "\n", encoding="utf-8"
    )
    importance = (
        float(spec["cpu_weight"]) * cpu_model.get_feature_importance()
        + float(spec["gpu_weight"]) * gpu_model.get_feature_importance()
        + float(spec["extra_weight"]) * extra_model.feature_importances_
    )
    pd.DataFrame({"feature": features, "importance": importance}).sort_values(
        "importance", ascending=False
    ).to_csv(output / "feature_importance.csv", index=False)

    zip_path = output / "submit.zip"
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(package.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(package))
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("생성된 제출 ZIP이 손상되었습니다.")
        top_level = {name.split("/", 1)[0] for name in archive.namelist()}
        expected = {"model", "requirements.txt", "script.py"}
        if top_level != expected:
            raise RuntimeError(
                f"제출 ZIP 최상위 구조 불일치: expected={expected}, actual={top_level}"
            )
    metadata = {
        "status": "complete",
        "name": resolved["final"]["name"],
        "config_hash": resolved["config_hash"],
        "source_tree_sha256": source_tree_hash(),
        "provenance_repository": resolved["final"]["provenance_repository"],
        "provenance_commit": resolved["final"]["provenance_commit"],
        "rows": int(len(train)),
        "training_seasons": sorted(int(value) for value in seasons.unique()),
        "target_rate": success_prior,
        "feature_count": len(features),
        "categorical_count": len(categorical),
        "model": spec,
        "calibration": calibration,
        "fit_seconds": fit_seconds,
        "model_bytes": model_path.stat().st_size,
        "model_sha256": sha256_file(model_path),
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256_file(zip_path),
        "requirements": requirements,
        "zip_path": str(zip_path),
    }
    write_json(output / "build_metadata.json", metadata)
    write_json(output / "config_resolved.json", resolved)
    return metadata


def build_final_package(
    resolved: dict[str, Any],
    *,
    data_dir: str | Path,
    output_dir: str | Path = PROJECT_ROOT / "output" / "final",
) -> dict[str, Any]:
    data_path = validate_data_dir(data_dir)
    output = Path(output_dir).expanduser().resolve()
    package = output / "package"
    if package.exists():
        shutil.rmtree(package)
    model_dir = package / "model"
    model_dir.mkdir(parents=True)

    if resolved["model"]["family"] == "cat_cpu_gpu_extra_blend":
        return _build_triple_final_package(
            resolved,
            data_path=data_path,
            output=output,
            package=package,
            model_dir=model_dir,
        )

    train, raw_columns = read_training_data(data_path)
    features, categorical = resolve_feature_names(raw_columns, resolved["features"])
    success_prior = float(train["control_success"].mean())
    engineered = engineer_features(
        train.drop(columns=["control_success"]),
        success_prior=success_prior,
        requested_custom=resolved["features"].get("custom", []),
    )
    native_categorical = bool(resolved["model"].get("native_categorical", False))
    preprocessor = make_preprocessor(
        categorical,
        features,
        native_categorical=native_categorical,
        linear=resolved["model"]["family"] == "logistic_regression",
    )
    preprocess_started = time.time()
    matrix = preprocessor.fit_transform(engineered.loc[:, features])
    preprocess_seconds = time.time() - preprocess_started

    model = make_model(resolved["model"], categorical)
    fit_started = time.time()
    model.fit(matrix, train["control_success"])
    fit_seconds = time.time() - fit_started
    bundle = {
        "config_hash": resolved["config_hash"],
        "features": features,
        "categorical": categorical,
        "custom_features": resolved["features"].get("custom", []),
        "success_prior": success_prior,
        "shrinkage_k": 50.0,
        "preprocessor": preprocessor,
        "model": model,
    }
    model_path = model_dir / "model.joblib"
    joblib.dump(bundle, model_path, compress=3)

    final = resolved["final"]
    calibration = {
        "method": final["calibration_method"],
        "shift": float(final["calibration_shift"]),
        "prediction_scale": float(resolved["model"].get("prediction_scale", 1.0)),
        "prediction_shift": float(resolved["model"].get("prediction_shift", 0.0)),
        "source_validation_seasons": final["calibration_source_seasons"],
        "uses_test_distribution": bool(final["uses_test_distribution"]),
    }
    write_json(model_dir / "calibration.json", calibration)
    (package / "features_runtime.py").write_text(
        _safe_features_runtime_script(resolved["features"].get("custom", [])),
        encoding="utf-8",
    )
    runtime_package = package / "aimers_exp"
    runtime_package.mkdir()
    (runtime_package / "__init__.py").write_text("", encoding="utf-8")
    (runtime_package / "modeling.py").write_text(
        _modeling_runtime_script(), encoding="utf-8"
    )
    (package / "script.py").write_text(_inference_script(), encoding="utf-8")
    requirements = [
        f"numpy=={np.__version__}",
        f"pandas=={pd.__version__}",
        f"scikit-learn=={sklearn.__version__}",
        f"joblib=={joblib.__version__}",
        f"catboost=={catboost.__version__}",
    ]
    (package / "requirements.txt").write_text(
        "\n".join(requirements) + "\n", encoding="utf-8"
    )
    pd.DataFrame(
        {
            "feature": preprocessor.get_feature_names_out(),
            "importance": model.get_feature_importance(),
        }
    ).sort_values("importance", ascending=False).to_csv(
        output / "feature_importance.csv", index=False
    )

    zip_path = output / "submit.zip"
    with zipfile.ZipFile(
        zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(package.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(package))
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("생성된 제출 ZIP이 손상되었습니다.")
        top_level = {name.split("/", 1)[0] for name in archive.namelist()}
        expected = {
            "aimers_exp",
            "features_runtime.py",
            "model",
            "requirements.txt",
            "script.py",
        }
        if top_level != expected:
            raise RuntimeError(
                f"제출 ZIP 최상위 구조 불일치: expected={expected}, actual={top_level}"
            )

    metadata = {
        "status": "complete",
        "name": final["name"],
        "config_hash": resolved["config_hash"],
        "source_tree_sha256": source_tree_hash(),
        "provenance_repository": final["provenance_repository"],
        "provenance_commit": final["provenance_commit"],
        "rows": int(len(train)),
        "training_seasons": sorted(int(value) for value in train["season"].unique()),
        "target_rate": success_prior,
        "feature_count": len(features),
        "categorical_count": len(categorical),
        "model": resolved["model"],
        "calibration": calibration,
        "preprocess_seconds": preprocess_seconds,
        "fit_seconds": fit_seconds,
        "model_bytes": model_path.stat().st_size,
        "model_sha256": sha256_file(model_path),
        "zip_bytes": zip_path.stat().st_size,
        "zip_sha256": sha256_file(zip_path),
        "requirements": requirements,
        "zip_path": str(zip_path),
    }
    write_json(output / "build_metadata.json", metadata)
    write_json(output / "config_resolved.json", resolved)
    return metadata


def validate_package(
    *, data_dir: str | Path, zip_path: str | Path, sample_rows: int = 5
) -> dict[str, Any]:
    data_path = validate_data_dir(data_dir)
    archive_path = Path(zip_path).expanduser().resolve()
    if not archive_path.is_file():
        raise FileNotFoundError(f"제출 ZIP을 찾을 수 없습니다: {archive_path}")
    with tempfile.TemporaryDirectory(prefix="aimers_package_") as temp_name:
        temp = Path(temp_name)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(temp)
        local_data = temp / "data"
        local_data.mkdir()
        base_test = pd.read_csv(data_path / "test.csv", nrows=sample_rows)

        def execute(test_frame: pd.DataFrame) -> tuple[pd.DataFrame, float]:
            sample = pd.DataFrame(
                {"row_id": test_frame["row_id"], "control_success": 0.0}
            )
            test_frame.to_csv(local_data / "test.csv", index=False)
            sample.to_csv(local_data / "sample_submission.csv", index=False)
            started = time.time()
            completed = subprocess.run(
                [sys.executable, "script.py"],
                cwd=temp,
                capture_output=True,
                text=True,
                check=False,
            )
            elapsed = time.time() - started
            if completed.returncode != 0:
                raise RuntimeError(
                    "패키지 실행 실패\n"
                    f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
                )
            submission = pd.read_csv(temp / "output" / "submission.csv")
            if submission["row_id"].tolist() != sample["row_id"].tolist():
                raise RuntimeError("패키지 출력 row_id가 sample과 다릅니다.")
            return submission, elapsed

        submission, elapsed = execute(base_test)
        baseline = submission.set_index("row_id")["control_success"]
        checks: dict[str, float] = {}
        singleton, _ = execute(base_test.iloc[[0]])
        checks["singleton"] = abs(
            float(singleton.iloc[0]["control_success"])
            - float(baseline.loc[base_test.iloc[0]["row_id"]])
        )
        shuffled_test = base_test.sample(frac=1.0, random_state=42)
        shuffled, _ = execute(shuffled_test)
        checks["shuffle"] = float(
            (shuffled.set_index("row_id")["control_success"].reindex(baseline.index) - baseline)
            .abs()
            .max()
        )
        copied = base_test.iloc[[0]].copy()
        copied.loc[:, "row_id"] = "__INDEPENDENCE_COPY__"
        augmented_test = pd.concat([base_test, copied], ignore_index=True)
        augmented, _ = execute(augmented_test)
        augmented_values = augmented.set_index("row_id")["control_success"]
        checks["add_row"] = float(
            (augmented_values.reindex(baseline.index) - baseline).abs().max()
        )
        checks["duplicate_features"] = abs(
            float(augmented_values.loc["__INDEPENDENCE_COPY__"])
            - float(baseline.loc[base_test.iloc[0]["row_id"]])
        )
        maximum_difference = max(checks.values(), default=0.0)
        if maximum_difference > 1e-12:
            raise RuntimeError(
                f"행 독립성 검증 실패: differences={checks}"
            )
    return {
        "status": "success",
        "zip_path": str(archive_path),
        "zip_sha256": sha256_file(archive_path),
        "sample_rows": int(len(submission)),
        "probability_min": float(submission["control_success"].min()),
        "probability_max": float(submission["control_success"].max()),
        "elapsed_seconds": elapsed,
        "row_independence_max_difference": maximum_difference,
        "row_independence_checks": checks,
    }
