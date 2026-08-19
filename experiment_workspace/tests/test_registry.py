from __future__ import annotations

import json
from pathlib import Path

from aimers_exp.config import PROJECT_ROOT
from aimers_exp.registry import (
    create_experiment,
    decide_experiment,
    plan_experiment,
    rebuild_index,
    run_experiment,
    show_experiment,
)


def test_registered_experiments_are_ready() -> None:
    rows = rebuild_index()
    ids = [row["id"] for row in rows]
    assert ids == sorted(set(ids))
    quarantined = {
        path.name
        for path in (PROJECT_ROOT / "experiments" / "rule_invalid").glob("EXP_*")
    }
    assert not set(ids).intersection(quarantined)
    for experiment_id in (row["id"] for row in rows):
        plan = plan_experiment(experiment_id)
        assert plan["ready"] is True
        assert plan["warnings"] == []


def test_exp_new_allocates_number_and_local_study(tmp_path: Path) -> None:
    root = tmp_path / "project"
    registry = root / "experiments"
    first = create_experiment(
        title="첫 실험",
        hypothesis="가설",
        change_scope="features",
        ablation_summary="기준 대비 피처 변경",
        project_root=root,
        experiments_root=registry,
    )
    second = create_experiment(
        title="두 번째 실험",
        hypothesis="가설",
        change_scope="model",
        ablation_summary="기준 대비 모델 변경",
        project_root=root,
        experiments_root=registry,
    )
    assert first["id"] == "EXP_001"
    assert second["id"] == "EXP_002"
    assert (registry / "EXP_001/study.toml").is_file()
    assert not (root / "configs").exists()
    plan = plan_experiment(
        "EXP_001", project_root=root, experiments_root=registry
    )
    assert plan["ready"] is False
    assert any("실제 설정 변경이 없습니다" in warning for warning in plan["warnings"])


def test_exp_new_does_not_reuse_quarantined_number(tmp_path: Path) -> None:
    root = tmp_path / "project"
    registry = root / "experiments"
    (registry / "rule_invalid" / "EXP_053").mkdir(parents=True)
    created = create_experiment(
        title="격리 이후 첫 실험",
        hypothesis="규칙 준수 피처가 개선한다",
        change_scope="features",
        ablation_summary="EXP_024 기반 행 독립 피처",
        project_root=root,
        experiments_root=registry,
    )
    assert created["id"] == "EXP_054"


def test_exp_run_creates_compact_timeline(
    synthetic_data_dir: Path, tmp_path: Path
) -> None:
    root = tmp_path / "project"
    registry = root / "experiments"
    created = create_experiment(
        title="custom14 검증",
        hypothesis="custom14가 Brier를 개선한다",
        change_scope="features",
        ablation_summary="selected41 대비 custom14 추가",
        project_root=root,
        experiments_root=registry,
    )
    study_path = Path(created["study_config"])
    study_path.write_text(
        '''[study]
id = "test_custom14"
description = "test"
hypothesis = "test"
protocol = "holdout_2024"
change_scope = ["features"]
control = "selected41_control"

[[variants]]
name = "selected41_control"
model = "catboost_default"
features = "selected41"
change = "control"

[[variants]]
name = "add_custom14"
model = "catboost_default"
features = "main55"
change = "파생 14개 추가"
''',
        encoding="utf-8",
    )
    assert plan_experiment(
        "EXP_001", project_root=root, experiments_root=registry
    )["ready"]
    compact = run_experiment(
        "EXP_001",
        data_dir=synthetic_data_dir,
        raw_runs_root=tmp_path / "raw_runs",
        store_predictions=False,
        project_root=root,
        experiments_root=registry,
    )
    directory = registry / "EXP_001"
    assert compact["run_id"] == "RUN_001"
    assert compact["status"] == "complete"
    assert (directory / "runs/RUN_001/summary.json").is_file()
    assert (directory / "runs/RUN_001/resolved_config.json").is_file()
    assert (directory / "runs/RUN_001/protocol.toml").is_file()
    assert (
        directory / "runs/RUN_001/variants/add_custom14/features.toml"
    ).is_file()
    diff = json.loads(
        (directory / "runs/RUN_001/ablation_diff.json").read_text()
    )
    custom = next(row for row in diff["variants"] if row["name"] == "add_custom14")
    assert len(custom["added_features_vs_control"]) == 14
    assert (directory / "runs/RUN_001/leaderboard.csv").is_file()
    assert (directory / "runs/RUN_001/report.md").is_file()
    assert not (directory / "result.csv").exists()
    assert not (directory / "report.md").exists()
    state = json.loads((directory / "state.json").read_text())
    assert state["status"] == "completed"
    events = [
        json.loads(line)["event"]
        for line in (directory / "history.jsonl").read_text().splitlines()
    ]
    assert events == ["created", "validated", "run_started", "run_completed"]

    decision = decide_experiment(
        "EXP_001",
        decision="adopt",
        selected_variant="add_custom14",
        reason="2024 홀드아웃 Brier 개선",
        experiments_root=registry,
    )
    assert decision["based_on_run_id"] == "RUN_001"
    assert decision["selected_result"]["variant"] == "add_custom14"
    assert (directory / "decision.md").is_file()
    rows = rebuild_index(registry)
    assert rows[0]["status"] == "decided"
    assert rows[0]["selected_variant"] == "add_custom14"
    assert "history" not in show_experiment("EXP_001", experiments_root=registry)
    assert "history" in show_experiment(
        "EXP_001", experiments_root=registry, include_history=True
    )
