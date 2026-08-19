from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from aimers_exp.config import DEFAULT_DATA_DIR

OPEN_DATA = DEFAULT_DATA_DIR


@pytest.fixture
def synthetic_data_dir(tmp_path: Path) -> Path:
    test = pd.read_csv(OPEN_DATA / "test.csv")
    rows = []
    for season in (2019, 2020, 2021, 2022, 2023, 2024):
        fold = test.copy()
        fold["season"] = season
        fold["row_id"] = [f"TRAIN_{season}_{index}" for index in range(len(fold))]
        fold["control_success"] = [index % 2 for index in range(len(fold))]
        rows.append(fold)
    train = pd.concat(rows, ignore_index=True)
    sample = pd.DataFrame(
        {"row_id": test["row_id"], "control_success": 0.5}
    )
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    train.to_csv(data_dir / "train.csv", index=False)
    test.to_csv(data_dir / "test.csv", index=False)
    sample.to_csv(data_dir / "sample_submission.csv", index=False)
    return data_dir
