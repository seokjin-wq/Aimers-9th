from __future__ import annotations

from pathlib import Path

import pytest

from aimers_exp.config import PROJECT_ROOT, load_toml, resolve_final, resolve_study


def test_all_tracked_studies_resolve() -> None:
    paths = sorted((PROJECT_ROOT / "experiments").glob("EXP_*/study.toml"))
    assert paths
    for path in paths:
        resolved = resolve_study(path)
        assert resolved["config_hash"]
        assert resolved["study"]["control"] in {
            variant["name"] for variant in resolved["variants"]
        }


def test_feature_study_keeps_model_locked() -> None:
    resolved = resolve_study("experiments/EXP_002/study.toml")
    model_specs = [variant["model"] for variant in resolved["variants"]]
    assert all(model == model_specs[0] for model in model_specs)
    assert resolved["study"]["change_scope"] == ["features"]


def test_change_outside_declared_scope_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "invalid.toml"
    path.write_text(
        '''[study]
id = "invalid"
protocol = "holdout_2024"
change_scope = ["features"]
control = "control"

[[variants]]
name = "control"
model = "catboost_default"
features = "raw47"

[[variants]]
name = "bad"
model = "random_forest_default"
features = "raw47"
''',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="change_scope"):
        resolve_study(path)


def test_final_config_tracks_read_only_baseline_commit() -> None:
    resolved = resolve_final()
    assert resolved["final"]["provenance_repository"] == "Aimers-9th"
    assert resolved["final"]["provenance_commit"] == "349498b"
    assert resolved["final"]["name"].startswith("exp130_compliant")
    assert resolved["features"]["name"] == "main78_history_reliability"
    assert resolved["model"]["family"] == "cat_cpu_gpu_extra_blend"
    assert resolved["model"]["trend_method"] == "ols"
    provenance = load_toml(
        "experiments/BASELINE_001_main55/provenance.toml"
    )["provenance"]
    assert provenance["read_only"] is True
    assert provenance["commit"] == "349498b"
