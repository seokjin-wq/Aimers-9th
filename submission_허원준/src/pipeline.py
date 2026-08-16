"""Training, validation, and DACON package helpers for the CatBoost model."""

from __future__ import annotations

import gc
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

import catboost
import joblib
import numpy as np
import pandas as pd
import sklearn
from catboost import CatBoostClassifier
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OrdinalEncoder

from .features import (
    FINAL_CUSTOM_COLUMNS,
    ID_COL,
    PROVIDED_CALENDAR_DERIVED_COLUMNS,
    PROVIDED_CONTEXT_METRIC_COLUMNS,
    PROVIDED_EVENT_STATE_COLUMNS,
    PROVIDED_STATE_RECOMBINATION_COLUMNS,
    RAW_EXCLUSION_REASONS,
    TARGET_COL,
    engineer_features,
    make_feature_specs,
)


FINAL_EXPERIMENT = "main55_fixed"
FINAL_ITERATIONS = 293
FINAL_CALIBRATION_SHIFT = -0.010462037831246366


@dataclass(frozen=True)
class ModelConfig:
    iterations: int = 300
    depth: int = 6
    learning_rate: float = 0.05
    l2_leaf_reg: float = 3.0
    subsample: float = 0.7
    seed: int = 42
    thread_count: int = 8


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_data_dir(data_dir: Path) -> Path:
    data_dir = Path(data_dir).expanduser().resolve()
    required = {"train.csv", "test.csv", "sample_submission.csv"}
    missing = sorted(name for name in required if not (data_dir / name).is_file())
    if missing:
        raise FileNotFoundError(
            f"데이터 폴더 {data_dir}에 다음 파일이 없습니다: {', '.join(missing)}"
        )
    return data_dir


def read_training_data(data_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    data_dir = validate_data_dir(data_dir)
    test_columns = pd.read_csv(data_dir / "test.csv", nrows=0).columns.tolist()
    raw_columns = [column for column in test_columns if column != ID_COL]
    train = pd.read_csv(
        data_dir / "train.csv",
        usecols=[*raw_columns, TARGET_COL],
        encoding="utf-8-sig",
    )
    return train, raw_columns


def make_preprocessor(
    categorical: tuple[str, ...],
    features: tuple[str, ...],
) -> ColumnTransformer:
    numeric = [column for column in features if column not in categorical]
    return ColumnTransformer(
        [
            (
                "cat",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                list(categorical),
            ),
            ("num", SimpleImputer(strategy="median"), numeric),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def _catboost_params(config: ModelConfig) -> dict:
    return {
        "loss_function": "Logloss",
        "eval_metric": "BrierScore",
        "iterations": config.iterations,
        "depth": config.depth,
        "learning_rate": config.learning_rate,
        "l2_leaf_reg": config.l2_leaf_reg,
        "subsample": config.subsample,
        "random_seed": config.seed,
        "thread_count": config.thread_count,
        "task_type": "CPU",
        "allow_writing_files": False,
        "verbose": False,
    }


def _random_forest_params(config: ModelConfig) -> dict:
    return {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_leaf": 200,
        "n_jobs": config.thread_count,
        "random_state": config.seed,
    }


def calculate_metrics(y_true: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    target_rate = float(np.mean(y_true))
    prediction_mean = float(np.mean(probability))
    brier = float(np.mean((probability - y_true) ** 2))
    reference_brier = target_rate * (1.0 - target_rate)
    return {
        "rows": int(len(y_true)),
        "target_rate": target_rate,
        "prediction_mean": prediction_mean,
        "bias": prediction_mean - target_rate,
        "brier": brier,
        "reference_brier": reference_brier,
        "brier_skill_score": max(0.0, 100000.0 * (1.0 - brier / reference_brier)),
        "roc_auc": float(roc_auc_score(y_true, probability)),
    }


def fit_experiment(
    raw_train: pd.DataFrame,
    raw_columns: list[str],
    experiment: str,
    validation_season: int,
    config: ModelConfig,
) -> tuple[dict, dict]:
    train_mask = raw_train["season"] < validation_season
    validation_mask = raw_train["season"] == validation_season
    if not train_mask.any() or not validation_mask.any():
        raise ValueError(f"검증 시즌 {validation_season}의 학습/검증 행을 만들 수 없습니다.")

    success_prior = float(raw_train.loc[train_mask, TARGET_COL].mean())
    feature_frame = engineer_features(
        raw_train.drop(columns=[TARGET_COL]), success_prior=success_prior
    )
    specs = make_feature_specs(raw_columns)
    if experiment not in specs:
        raise ValueError(f"알 수 없는 실험 {experiment!r}; 선택 가능: {sorted(specs)}")
    spec = specs[experiment]

    preprocessor = make_preprocessor(spec.categorical, spec.features)
    preprocess_started = time.time()
    x_train = preprocessor.fit_transform(
        feature_frame.loc[train_mask, list(spec.features)]
    )
    x_validation = preprocessor.transform(
        feature_frame.loc[validation_mask, list(spec.features)]
    )
    preprocess_seconds = time.time() - preprocess_started

    is_random_forest = experiment == "raw47_random_forest"
    model = (
        RandomForestClassifier(**_random_forest_params(config))
        if is_random_forest
        else CatBoostClassifier(**_catboost_params(config))
    )
    fit_started = time.time()
    model.fit(x_train, raw_train.loc[train_mask, TARGET_COL])
    fit_seconds = time.time() - fit_started
    probability = model.predict_proba(x_validation)[:, 1]

    result = calculate_metrics(
        raw_train.loc[validation_mask, TARGET_COL].to_numpy(), probability
    )
    result.update(
        {
            "experiment": experiment,
            "description": spec.description,
            "model_family": "random_forest" if is_random_forest else "catboost",
            "validation_season": validation_season,
            "training_seasons": "-".join(
                map(str, sorted(raw_train.loc[train_mask, "season"].unique()))
            ),
            "feature_count": len(spec.features),
            "categorical_count": len(spec.categorical),
            "success_prior": success_prior,
            "tree_count": int(
                model.n_estimators if is_random_forest else model.tree_count_
            ),
            "preprocess_seconds": preprocess_seconds,
            "fit_seconds": fit_seconds,
        }
    )
    bundle = {
        "experiment": experiment,
        "description": spec.description,
        "model_family": "random_forest" if is_random_forest else "catboost",
        "features": list(spec.features),
        "categorical": list(spec.categorical),
        "success_prior": success_prior,
        "shrinkage_k": 50.0,
        "preprocessor": preprocessor,
        "model": model,
    }
    return result, bundle


def run_experiments(
    data_dir: Path,
    output_dir: Path,
    experiments: list[str],
    validation_seasons: list[int],
    config: ModelConfig | None = None,
) -> pd.DataFrame:
    config = config or ModelConfig()
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_train, raw_columns = read_training_data(data_dir)

    results: list[dict] = []
    for validation_season in validation_seasons:
        for experiment in experiments:
            print(f"[{validation_season}] {experiment}", flush=True)
            result, bundle = fit_experiment(
                raw_train, raw_columns, experiment, validation_season, config
            )
            results.append(result)
            pd.DataFrame(results).to_csv(
                output_dir / "experiment_results.partial.csv", index=False
            )
            print(json.dumps(result, ensure_ascii=False), flush=True)
            del bundle
            gc.collect()

    result_frame = pd.DataFrame(results).sort_values(
        ["validation_season", "brier", "experiment"]
    )
    result_frame.to_csv(output_dir / "experiment_results.csv", index=False)
    metadata = {
        "data_dir": str(Path(data_dir).expanduser().resolve()),
        "output_dir": str(output_dir),
        "experiments": experiments,
        "validation_seasons": validation_seasons,
        "model_config": asdict(config),
    }
    (output_dir / "experiment_config.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result_frame


def _feature_inventory(raw_columns: list[str]) -> pd.DataFrame:
    spec = make_feature_specs(raw_columns)[FINAL_EXPERIMENT]
    rows: list[dict[str, str]] = []
    for feature in spec.features:
        if feature in FINAL_CUSTOM_COLUMNS:
            origin = "새 파생"
        elif feature in PROVIDED_EVENT_STATE_COLUMNS:
            origin = "제공 기초 관측·식별"
        elif feature in (
            PROVIDED_CALENDAR_DERIVED_COLUMNS
            + PROVIDED_STATE_RECOMBINATION_COLUMNS
            + PROVIDED_CONTEXT_METRIC_COLUMNS
        ):
            origin = "제공 행 단위 파생"
        elif feature.startswith("asof_"):
            origin = "제공 과거 기록 파생"
        else:
            raise RuntimeError(f"피처 출처를 분류하지 못했습니다: {feature}")
        rows.append(
            {"status": "사용", "origin": origin, "feature": feature, "reason": "최종 55개에 유지"}
        )
    rows.extend(
        {
            "status": "제외",
            "origin": "제공 피처",
            "feature": feature,
            "reason": reason,
        }
        for feature, reason in RAW_EXCLUSION_REASONS.items()
    )
    inventory = pd.DataFrame(rows)
    origin_counts = inventory.loc[inventory["status"] == "사용", "origin"].value_counts()
    expected = {
        "제공 기초 관측·식별": 17,
        "제공 행 단위 파생": 9,
        "제공 과거 기록 파생": 15,
        "새 파생": 14,
    }
    if origin_counts.to_dict() != expected:
        raise RuntimeError(
            f"최종 피처 출처별 개수가 예상과 다릅니다: {origin_counts.to_dict()}"
        )
    return inventory


def _inference_script() -> str:
    return '''from __future__ import annotations

import json
import os

import joblib
import numpy as np
import pandas as pd

from features import engineer_features


DATA_DIR = "./data"
MODEL_DIR = "./model"
OUTPUT_DIR = "./output"
ID_COL = "row_id"
TARGET_COL = "control_success"


def main() -> None:
    test = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))
    sample = pd.read_csv(os.path.join(DATA_DIR, "sample_submission.csv"))
    bundle = joblib.load(os.path.join(MODEL_DIR, "model.joblib"))
    with open(os.path.join(MODEL_DIR, "calibration.json"), encoding="utf-8") as stream:
        calibration = json.load(stream)

    frame = engineer_features(
        test,
        success_prior=float(bundle["success_prior"]),
        shrinkage_k=float(bundle["shrinkage_k"]),
    )
    matrix = bundle["preprocessor"].transform(frame.loc[:, bundle["features"]])
    probability = bundle["model"].predict_proba(matrix)[:, 1]
    probability = np.clip(probability + float(calibration["shift"]), 0.0, 1.0)

    prediction = pd.DataFrame({ID_COL: test[ID_COL], TARGET_COL: probability})
    submission = sample[[ID_COL]].merge(prediction, on=ID_COL, how="left", validate="one_to_one")
    if len(submission) != len(sample):
        raise RuntimeError("sample_submission.csv와 출력 행 수가 다릅니다.")
    if submission[TARGET_COL].isna().any():
        raise RuntimeError("예측값에 결측치가 있습니다.")
    if not submission[TARGET_COL].between(0.0, 1.0).all():
        raise RuntimeError("예측값은 0과 1 사이여야 합니다.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    submission.to_csv(os.path.join(OUTPUT_DIR, "submission.csv"), index=False)


if __name__ == "__main__":
    main()
'''


def build_submission(
    data_dir: Path,
    output_dir: Path,
    config: ModelConfig | None = None,
    calibration_shift: float = FINAL_CALIBRATION_SHIFT,
) -> dict:
    config = config or ModelConfig(iterations=FINAL_ITERATIONS)
    data_dir = validate_data_dir(data_dir)
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    package_dir = output_dir / "package"
    model_dir = package_dir / "model"
    zip_path = output_dir / "submit.zip"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    model_dir.mkdir(parents=True)

    train, raw_columns = read_training_data(data_dir)
    spec = make_feature_specs(raw_columns)[FINAL_EXPERIMENT]
    success_prior = float(train[TARGET_COL].mean())
    feature_frame = engineer_features(
        train.drop(columns=[TARGET_COL]), success_prior=success_prior
    )
    preprocessor = make_preprocessor(spec.categorical, spec.features)

    preprocess_started = time.time()
    matrix = preprocessor.fit_transform(feature_frame.loc[:, list(spec.features)])
    preprocess_seconds = time.time() - preprocess_started
    model = CatBoostClassifier(**_catboost_params(config))
    fit_started = time.time()
    model.fit(matrix, train[TARGET_COL])
    fit_seconds = time.time() - fit_started

    bundle = {
        "experiment": FINAL_EXPERIMENT,
        "description": spec.description,
        "model_family": "catboost",
        "features": list(spec.features),
        "categorical": list(spec.categorical),
        "success_prior": success_prior,
        "shrinkage_k": 50.0,
        "preprocessor": preprocessor,
        "model": model,
    }
    model_path = model_dir / "model.joblib"
    joblib.dump(bundle, model_path, compress=3)

    calibration = {
        "method": "expanding_mean_prediction_bias_shift",
        "shift": calibration_shift,
        "source_validation_seasons": [2022, 2023, 2024],
        "uses_test_distribution": False,
    }
    (model_dir / "calibration.json").write_text(
        json.dumps(calibration, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    source_features = Path(__file__).with_name("features.py")
    shutil.copy2(source_features, package_dir / "features.py")
    requirements = [
        f"numpy=={np.__version__}",
        f"pandas=={pd.__version__}",
        f"scikit-learn=={sklearn.__version__}",
        f"joblib=={joblib.__version__}",
        f"catboost=={catboost.__version__}",
    ]
    (package_dir / "requirements.txt").write_text(
        "\n".join(requirements) + "\n", encoding="utf-8"
    )
    (package_dir / "script.py").write_text(_inference_script(), encoding="utf-8")

    inventory = _feature_inventory(raw_columns)
    inventory.to_csv(output_dir / "feature_inventory.csv", index=False)
    importance = pd.DataFrame(
        {
            "feature": preprocessor.get_feature_names_out(),
            "importance": model.get_feature_importance(),
        }
    ).sort_values("importance", ascending=False)
    importance.to_csv(output_dir / "final_feature_importance.csv", index=False)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                archive.write(path, path.relative_to(package_dir))
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        top_level = {name.split("/")[0] + ("/" if "/" in name else "") for name in names}
        expected_top_level = {"features.py", "model/", "requirements.txt", "script.py"}
        if top_level != expected_top_level:
            raise RuntimeError(f"제출 ZIP 구조가 예상과 다릅니다: {top_level}")
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise RuntimeError(f"제출 ZIP이 손상되었습니다: {corrupt_member}")

    build = {
        "experiment": FINAL_EXPERIMENT,
        "rows": int(len(train)),
        "training_seasons": sorted(int(value) for value in train["season"].unique()),
        "target_rate": success_prior,
        "feature_count": len(spec.features),
        "feature_origin_counts": {
            "provided_event_state": 17,
            "provided_row_derived": 9,
            "provided_history_derived": 15,
            "custom_derived": 14,
        },
        "categorical_count": len(spec.categorical),
        "model_config": asdict(config),
        "calibration_shift": calibration_shift,
        "preprocess_seconds": preprocess_seconds,
        "fit_seconds": fit_seconds,
        "model_bytes": model_path.stat().st_size,
        "zip_bytes": zip_path.stat().st_size,
        "model_sha256": sha256(model_path),
        "zip_sha256": sha256(zip_path),
        "python": sys.version.split()[0],
        "requirements": requirements,
        "zip_path": str(zip_path),
    }
    (output_dir / "final_build.json").write_text(
        json.dumps(build, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return build


def validate_submission_zip(
    data_dir: Path,
    zip_path: Path,
    sample_rows: int = 5,
) -> dict:
    data_dir = validate_data_dir(data_dir)
    zip_path = Path(zip_path).expanduser().resolve()
    if not zip_path.is_file():
        raise FileNotFoundError(f"제출 ZIP이 없습니다: {zip_path}")

    with tempfile.TemporaryDirectory(prefix="aimers_catboost_validate_") as temp_name:
        temp_dir = Path(temp_name)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(temp_dir)
        test = pd.read_csv(data_dir / "test.csv", nrows=sample_rows)
        sample = pd.read_csv(data_dir / "sample_submission.csv", nrows=sample_rows)
        package_data_dir = temp_dir / "data"
        package_data_dir.mkdir()
        test.to_csv(package_data_dir / "test.csv", index=False)
        sample.to_csv(package_data_dir / "sample_submission.csv", index=False)

        started = time.time()
        completed = subprocess.run(
            [sys.executable, "script.py"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        elapsed_seconds = time.time() - started
        if completed.returncode != 0:
            raise RuntimeError(
                "제출 ZIP 실행 검증에 실패했습니다.\n"
                f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
            )
        result = pd.read_csv(temp_dir / "output" / "submission.csv")
        if result[ID_COL].tolist() != sample[ID_COL].tolist():
            raise RuntimeError("샘플 제출 순서와 검증 출력 순서가 다릅니다.")
        if result[TARGET_COL].isna().any():
            raise RuntimeError("검증 출력에 결측 예측값이 있습니다.")
        if not result[TARGET_COL].between(0.0, 1.0).all():
            raise RuntimeError("검증 출력이 0과 1 범위를 벗어났습니다.")

    validation = {
        "zip_path": str(zip_path),
        "zip_sha256": sha256(zip_path),
        "sample_rows": int(len(result)),
        "missing_predictions": int(result[TARGET_COL].isna().sum()),
        "probability_min": float(result[TARGET_COL].min()),
        "probability_max": float(result[TARGET_COL].max()),
        "elapsed_seconds": elapsed_seconds,
        "status": "success",
    }
    (zip_path.parent / "package_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return validation
