from __future__ import annotations

import json
import shutil
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .config import BASELINE_ROOT, PROJECT_ROOT, resolve_study
from .features import resolve_feature_names
from .runner import run_study, write_json

EXPERIMENTS_ROOT = PROJECT_ROOT / "experiments"
VALID_SCOPES = {"features", "model"}
VALID_DECISIONS = {"adopt", "reject", "keep_control", "inconclusive"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _experiment_number(experiment_id: str) -> int:
    if not experiment_id.startswith("EXP_"):
        raise ValueError(f"실험 ID 형식이 올바르지 않습니다: {experiment_id}")
    try:
        return int(experiment_id.removeprefix("EXP_"))
    except ValueError as error:
        raise ValueError(f"실험 ID 형식이 올바르지 않습니다: {experiment_id}") from error


def experiment_dir(
    experiment_id: str, experiments_root: str | Path = EXPERIMENTS_ROOT
) -> Path:
    _experiment_number(experiment_id)
    path = Path(experiments_root) / experiment_id
    if not path.is_dir():
        raise FileNotFoundError(f"등록되지 않은 실험입니다: {experiment_id}")
    return path


def _append_history(directory: Path, event: str, details: dict[str, Any]) -> None:
    record = {"at_utc": now_utc(), "event": event, "details": details}
    with (directory / "history.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_manifest(directory: Path) -> dict[str, Any]:
    path = directory / "experiment.toml"
    if not path.is_file():
        raise FileNotFoundError(f"실험 manifest가 없습니다: {path}")
    with path.open("rb") as stream:
        document = tomllib.load(stream)
    if "experiment" not in document:
        raise ValueError(f"{path}에 [experiment] 섹션이 없습니다.")
    manifest = document["experiment"]
    required = {
        "id",
        "title",
        "hypothesis",
        "change_scope",
        "study_config",
        "based_on",
        "reference_variant",
        "ablation_summary",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ValueError(f"실험 manifest 필수값 누락: {missing}")
    if manifest["id"] != directory.name:
        raise ValueError(
            f"폴더명과 manifest ID가 다릅니다: {directory.name} != {manifest['id']}"
        )
    if manifest["change_scope"] not in VALID_SCOPES:
        raise ValueError(f"지원하지 않는 변경 범위: {manifest['change_scope']}")
    return manifest


def _read_state(directory: Path) -> dict[str, Any]:
    path = directory / "state.json"
    if not path.is_file():
        raise FileNotFoundError(f"실험 상태 파일이 없습니다: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_state(directory: Path, state: dict[str, Any]) -> None:
    state["updated_at_utc"] = now_utc()
    write_json(directory / "state.json", state)


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _next_experiment_id(experiments_root: Path) -> str:
    numbers = []
    if experiments_root.is_dir():
        active = experiments_root.glob("EXP_*")
        quarantined = (experiments_root / "rule_invalid").glob("EXP_*")
        for path in (*active, *quarantined):
            if not path.is_dir():
                continue
            try:
                numbers.append(_experiment_number(path.name))
            except ValueError:
                continue
    return f"EXP_{max(numbers, default=0) + 1:03d}"


def _write_study_template(
    path: Path,
    *,
    experiment_id: str,
    title: str,
    hypothesis: str,
    change_scope: str,
) -> None:
    variant_name = "feature_variant" if change_scope == "features" else "model_variant"
    lines = [
        "[study]",
        f"id = {_toml_string(experiment_id.lower())}",
        f"description = {_toml_string(title)}",
        f"hypothesis = {_toml_string(hypothesis)}",
        'protocol = "holdout_2024"',
        f"change_scope = [{_toml_string(change_scope)}]",
        'control = "main55_control"',
        "",
        "[[variants]]",
        'name = "main55_control"',
        'model = "catboost_default"',
        'features = "main55"',
        'change = "control: 현재 main55 CatBoost 기준선"',
        "",
        "[[variants]]",
        f"name = {_toml_string(variant_name)}",
        'model = "catboost_default"',
        'features = "main55"',
        'change = "TODO: control 대비 한 종류의 변경만 설명"',
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def create_experiment(
    *,
    title: str,
    hypothesis: str,
    change_scope: str,
    ablation_summary: str,
    based_on: str = "BASELINE_001_main55",
    reference_variant: str = "main55_control",
    tags: list[str] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    experiments_root: str | Path | None = None,
) -> dict[str, Any]:
    if change_scope not in VALID_SCOPES:
        raise ValueError(f"change_scope는 {sorted(VALID_SCOPES)} 중 하나여야 합니다.")
    root = Path(project_root).resolve()
    registry_root = (
        Path(experiments_root).resolve()
        if experiments_root is not None
        else root / "experiments"
    )
    registry_root.mkdir(parents=True, exist_ok=True)
    while True:
        experiment_id = _next_experiment_id(registry_root)
        directory = registry_root / experiment_id
        try:
            directory.mkdir()
            break
        except FileExistsError:
            continue

    study_path = directory / "study.toml"
    _write_study_template(
        study_path,
        experiment_id=experiment_id,
        title=title,
        hypothesis=hypothesis,
        change_scope=change_scope,
    )
    relative_study = study_path.relative_to(root).as_posix()
    created_at = now_utc()
    manifest_lines = [
        "[experiment]",
        f"id = {_toml_string(experiment_id)}",
        f"title = {_toml_string(title)}",
        f"hypothesis = {_toml_string(hypothesis)}",
        f"change_scope = {_toml_string(change_scope)}",
        f"study_config = {_toml_string(relative_study)}",
        f"based_on = {_toml_string(based_on)}",
        f"reference_variant = {_toml_string(reference_variant)}",
        f"ablation_summary = {_toml_string(ablation_summary)}",
        "tags = " + json.dumps(tags or [], ensure_ascii=False),
        f"created_at_utc = {_toml_string(created_at)}",
        "",
    ]
    (directory / "experiment.toml").write_text(
        "\n".join(manifest_lines), encoding="utf-8"
    )
    (directory / "runs").mkdir()
    state = {
        "id": experiment_id,
        "status": "draft",
        "created_at_utc": created_at,
        "updated_at_utc": created_at,
        "run_count": 0,
        "latest_run_id": None,
        "decision": None,
        "selected_variant": None,
    }
    write_json(directory / "state.json", state)
    _append_history(
        directory,
        "created",
        {
            "title": title,
            "change_scope": change_scope,
            "study_config": relative_study,
            "based_on": based_on,
            "reference_variant": reference_variant,
            "ablation_summary": ablation_summary,
        },
    )
    rebuild_index(registry_root)
    return {
        "id": experiment_id,
        "experiment_dir": str(directory),
        "study_config": str(study_path),
        "status": "draft",
        "next_step": f"{relative_study}의 TODO variant를 수정한 뒤 exp-plan을 실행하세요.",
    }


def _study_path(manifest: dict[str, Any], project_root: Path) -> Path:
    path = Path(manifest["study_config"])
    return path if path.is_absolute() else project_root / path


def _run_summary_path(directory: Path, run_id: str) -> Path:
    snapshot = directory / "runs" / run_id / "summary.json"
    legacy = directory / "runs" / f"{run_id}.json"
    return snapshot if snapshot.is_file() or not legacy.is_file() else legacy


def _nested_value_diffs(
    control: Any, variant: Any, prefix: str = ""
) -> list[dict[str, Any]]:
    if isinstance(control, dict) and isinstance(variant, dict):
        rows = []
        for key in sorted(set(control) | set(variant)):
            child = f"{prefix}.{key}" if prefix else key
            rows.extend(
                _nested_value_diffs(control.get(key), variant.get(key), child)
            )
        return rows
    if control != variant:
        return [{"field": prefix, "control": control, "variant": variant}]
    return []


def _raw_columns(data_dir: str | Path) -> list[str]:
    test_path = Path(data_dir).expanduser().resolve() / "test.csv"
    if not test_path.is_file():
        raise FileNotFoundError(f"snapshot용 test.csv가 없습니다: {test_path}")
    return [
        column
        for column in pd.read_csv(test_path, nrows=0).columns.tolist()
        if column != "row_id"
    ]


def _ablation_diff(
    manifest: dict[str, Any],
    resolved: dict[str, Any],
    raw_columns: list[str],
) -> dict[str, Any]:
    control_name = resolved["study"]["control"]
    control = next(
        variant for variant in resolved["variants"] if variant["name"] == control_name
    )
    control_features, _ = resolve_feature_names(raw_columns, control["features"])
    control_set = set(control_features)
    variants = []
    for variant in resolved["variants"]:
        features, categorical = resolve_feature_names(raw_columns, variant["features"])
        feature_set = set(features)
        variants.append(
            {
                "name": variant["name"],
                "declared_change": variant["change"],
                "is_control": variant["name"] == control_name,
                "feature_count": len(features),
                "categorical_features": categorical,
                "added_features_vs_control": [
                    feature for feature in features if feature not in control_set
                ],
                "removed_features_vs_control": [
                    feature for feature in control_features if feature not in feature_set
                ],
                "model_changes_vs_control": _nested_value_diffs(
                    control["model"], variant["model"], "model"
                ),
            }
        )
    return {
        "based_on": manifest["based_on"],
        "reference_variant": manifest["reference_variant"],
        "ablation_summary": manifest["ablation_summary"],
        "control": control_name,
        "variants": variants,
    }


def _snapshot_run_configs(
    *,
    run_directory: Path,
    experiment_directory: Path,
    manifest: dict[str, Any],
    resolved: dict[str, Any],
    data_dir: str | Path,
    project_root: Path,
    backfilled: bool,
) -> dict[str, Any]:
    run_directory.mkdir(parents=True, exist_ok=False)
    shutil.copy2(
        experiment_directory / "experiment.toml",
        run_directory / "experiment.toml",
    )
    study_path = _study_path(manifest, project_root)
    shutil.copy2(study_path, run_directory / "study.toml")
    with study_path.open("rb") as stream:
        study_document = tomllib.load(stream)
    study = study_document["study"]
    source_variants = {
        variant["name"]: variant for variant in study_document["variants"]
    }
    protocol_path = BASELINE_ROOT / "protocols" / f"{study['protocol']}.toml"
    shutil.copy2(protocol_path, run_directory / "protocol.toml")
    write_json(run_directory / "resolved_config.json", resolved)

    raw_columns = _raw_columns(data_dir)
    diff = _ablation_diff(manifest, resolved, raw_columns)
    write_json(run_directory / "ablation_diff.json", diff)
    for variant in resolved["variants"]:
        source = source_variants[variant["name"]]
        variant_directory = run_directory / "variants" / variant["name"]
        variant_directory.mkdir(parents=True)
        shutil.copy2(
            BASELINE_ROOT / "models" / f"{source['model']}.toml",
            variant_directory / "model.toml",
        )
        shutil.copy2(
            BASELINE_ROOT / "features" / f"{source['features']}.toml",
            variant_directory / "features.toml",
        )
        feature_names, _ = resolve_feature_names(raw_columns, variant["features"])
        (variant_directory / "feature_list.txt").write_text(
            "\n".join(feature_names) + "\n", encoding="utf-8"
        )
    snapshot = {
        "snapshot_created_at_utc": now_utc(),
        "backfilled_after_run": backfilled,
        "config_hash_verified": resolved["config_hash"],
        "based_on": manifest["based_on"],
        "reference_variant": manifest["reference_variant"],
        "ablation_summary": manifest["ablation_summary"],
    }
    write_json(run_directory / "snapshot_metadata.json", snapshot)
    return diff


def _enhanced_report(base_report: str, diff: dict[str, Any]) -> str:
    marker = "## 실험 계보와 정확한 ablation"
    if marker in base_report:
        base_report = base_report.split(marker, 1)[0].rstrip() + "\n"
    lines = [
        "",
        marker,
        "",
        f"- 비교 기준: `{diff['based_on']}`",
        f"- 기준 variant: `{diff['reference_variant']}`",
        f"- 검증할 변경: {diff['ablation_summary']}",
        "",
    ]
    for variant in diff["variants"]:
        lines.extend([f"### {variant['name']}", ""])
        if variant["is_control"]:
            lines.extend(["- role: control", ""])
            continue
        lines.append(f"- declared change: {variant['declared_change']}")
        added = variant["added_features_vs_control"]
        removed = variant["removed_features_vs_control"]
        lines.append(
            "- added features: " + (", ".join(f"`{name}`" for name in added) or "none")
        )
        lines.append(
            "- removed features: "
            + (", ".join(f"`{name}`" for name in removed) or "none")
        )
        model_changes = variant["model_changes_vs_control"]
        if model_changes:
            lines.append("- model changes:")
            for change in model_changes:
                lines.append(
                    f"  - `{change['field']}`: `{change['control']}` → `{change['variant']}`"
                )
        else:
            lines.append("- model changes: none")
        lines.append("")
    return base_report.rstrip() + "\n" + "\n".join(lines).rstrip() + "\n"


def plan_experiment(
    experiment_id: str,
    *,
    project_root: str | Path = PROJECT_ROOT,
    experiments_root: str | Path = EXPERIMENTS_ROOT,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    directory = experiment_dir(experiment_id, experiments_root)
    manifest = _read_manifest(directory)
    resolved = resolve_study(_study_path(manifest, root))
    warnings = []
    declared_scope = resolved["study"]["change_scope"]
    if declared_scope != [manifest["change_scope"]]:
        warnings.append(
            "manifest와 study의 change_scope가 다릅니다: "
            f"{manifest['change_scope']} != {declared_scope}"
        )
    control = resolved["study"]["control"]
    for variant in resolved["variants"]:
        if variant["name"] == control:
            continue
        if not variant["changed_fields_vs_control"]:
            warnings.append(f"{variant['name']}: control 대비 실제 설정 변경이 없습니다.")
        if "TODO" in variant["change"]:
            warnings.append(f"{variant['name']}: 변경 설명의 TODO를 수정해야 합니다.")
    ready = not warnings
    state = _read_state(directory)
    if ready and state["status"] == "draft":
        state["status"] = "ready"
        _write_state(directory, state)
        _append_history(
            directory,
            "validated",
            {"config_hash": resolved["config_hash"], "status": "ready"},
        )
        rebuild_index(Path(experiments_root))
    return {
        "experiment": manifest,
        "status": _read_state(directory)["status"],
        "ready": ready,
        "warnings": warnings,
        "config_hash": resolved["config_hash"],
        "control": control,
        "protocol": resolved["protocol"],
        "variants": [
            {
                "name": variant["name"],
                "change": variant["change"],
                "model": variant["model"]["name"],
                "features": variant["features"]["name"],
                "changed_fields_vs_control": variant[
                    "changed_fields_vs_control"
                ],
            }
            for variant in resolved["variants"]
        ],
    }


def _next_run_id(directory: Path) -> str:
    numbers = []
    for path in (directory / "runs").glob("RUN_*"):
        try:
            name = path.stem if path.is_file() else path.name
            numbers.append(int(name.removeprefix("RUN_")))
        except ValueError:
            continue
    return f"RUN_{max(numbers, default=0) + 1:03d}"


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records"))


def run_experiment(
    experiment_id: str,
    *,
    data_dir: str | Path,
    raw_runs_root: str | Path = PROJECT_ROOT / "runs",
    only: list[str] | None = None,
    store_predictions: bool | None = None,
    project_root: str | Path = PROJECT_ROOT,
    experiments_root: str | Path = EXPERIMENTS_ROOT,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    registry_root = Path(experiments_root).resolve()
    directory = experiment_dir(experiment_id, registry_root)
    plan = plan_experiment(
        experiment_id, project_root=root, experiments_root=registry_root
    )
    if not plan["ready"]:
        raise ValueError("실험 설정이 실행 준비되지 않았습니다: " + "; ".join(plan["warnings"]))
    manifest = _read_manifest(directory)
    resolved = resolve_study(_study_path(manifest, root))
    run_id = _next_run_id(directory)
    run_directory = directory / "runs" / run_id
    diff = _snapshot_run_configs(
        run_directory=run_directory,
        experiment_directory=directory,
        manifest=manifest,
        resolved=resolved,
        data_dir=data_dir,
        project_root=root,
        backfilled=False,
    )
    state = _read_state(directory)
    state.update(
        {
            "status": "running",
            "latest_run_id": run_id,
            "run_count": int(state.get("run_count", 0)) + 1,
        }
    )
    _write_state(directory, state)
    started_at = now_utc()
    _append_history(
        directory,
        "run_started",
        {
            "run_id": run_id,
            "config_hash": resolved["config_hash"],
            "only": only,
            "store_predictions": store_predictions,
        },
    )
    rebuild_index(registry_root)

    compact_path = run_directory / "summary.json"
    try:
        raw_run_dir = run_study(
            resolved,
            data_dir=data_dir,
            runs_root=raw_runs_root,
            only=only,
            store_predictions=store_predictions,
        )
        leaderboard = pd.read_csv(raw_run_dir / "leaderboard.csv")
        metadata = json.loads((raw_run_dir / "metadata.json").read_text(encoding="utf-8"))
        best = leaderboard.sort_values("mean_brier").iloc[0]
        compact = {
            "experiment_id": experiment_id,
            "run_id": run_id,
            "status": "complete",
            "started_at_utc": started_at,
            "completed_at_utc": now_utc(),
            "config_hash": resolved["config_hash"],
            "based_on": manifest["based_on"],
            "reference_variant": manifest["reference_variant"],
            "ablation_summary": manifest["ablation_summary"],
            "raw_run_dir": str(raw_run_dir),
            "control": resolved["study"]["control"],
            "only": only,
            "invocation": {
                "data_dir": str(Path(data_dir).expanduser().resolve()),
                "raw_runs_root": str(Path(raw_runs_root).expanduser().resolve()),
                "only": only,
                "store_predictions": store_predictions,
            },
            "best_variant": str(best["variant"]),
            "best_mean_brier": float(best["mean_brier"]),
            "best_delta_brier_vs_control": float(best["delta_brier_vs_control"]),
            "leaderboard": _records(leaderboard),
            "source_tree_sha256": metadata.get("source_tree_sha256"),
            "git_commit": metadata.get("git_commit"),
            "data_files": metadata.get("data_files"),
            "elapsed_seconds": metadata.get("elapsed_seconds"),
        }
        write_json(compact_path, compact)
        leaderboard.to_csv(run_directory / "leaderboard.csv", index=False)
        report = _enhanced_report(
            (raw_run_dir / "report.md").read_text(encoding="utf-8"), diff
        )
        (run_directory / "report.md").write_text(report, encoding="utf-8")
        state.update({"status": "completed", "latest_run_id": run_id})
        _write_state(directory, state)
        _append_history(
            directory,
            "run_completed",
            {
                "run_id": run_id,
                "best_variant": compact["best_variant"],
                "best_delta_brier_vs_control": compact[
                    "best_delta_brier_vs_control"
                ],
                "raw_run_dir": str(raw_run_dir),
            },
        )
        rebuild_index(registry_root)
        return compact
    except Exception as error:
        failed = {
            "experiment_id": experiment_id,
            "run_id": run_id,
            "status": "failed",
            "started_at_utc": started_at,
            "failed_at_utc": now_utc(),
            "config_hash": resolved["config_hash"],
            "based_on": manifest["based_on"],
            "reference_variant": manifest["reference_variant"],
            "ablation_summary": manifest["ablation_summary"],
            "invocation": {
                "data_dir": str(Path(data_dir).expanduser().resolve()),
                "raw_runs_root": str(Path(raw_runs_root).expanduser().resolve()),
                "only": only,
                "store_predictions": store_predictions,
            },
            "error_type": type(error).__name__,
            "error": str(error),
        }
        write_json(compact_path, failed)
        state.update({"status": "failed", "latest_run_id": run_id})
        _write_state(directory, state)
        _append_history(
            directory,
            "run_failed",
            {
                "run_id": run_id,
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )
        rebuild_index(registry_root)
        raise


def migrate_legacy_run_snapshots(
    *,
    project_root: str | Path = PROJECT_ROOT,
    experiments_root: str | Path = EXPERIMENTS_ROOT,
) -> list[dict[str, Any]]:
    """Move tracked RUN_NNN.json files into self-contained snapshot directories."""
    root = Path(project_root).resolve()
    registry_root = Path(experiments_root).resolve()
    migrated = []
    for directory in sorted(registry_root.glob("EXP_*")):
        if not directory.is_dir():
            continue
        manifest = _read_manifest(directory)
        resolved = resolve_study(_study_path(manifest, root))
        for legacy_path in sorted((directory / "runs").glob("RUN_*.json")):
            summary = json.loads(legacy_path.read_text(encoding="utf-8"))
            run_id = summary["run_id"]
            if summary.get("config_hash") != resolved["config_hash"]:
                raise ValueError(
                    f"{directory.name}/{run_id} config hash 불일치: "
                    f"recorded={summary.get('config_hash')}, "
                    f"current={resolved['config_hash']}"
                )
            data_dir = summary.get("invocation", {}).get("data_dir")
            if not data_dir:
                raise ValueError(f"{directory.name}/{run_id}에 data_dir 기록이 없습니다.")
            run_directory = directory / "runs" / run_id
            diff = _snapshot_run_configs(
                run_directory=run_directory,
                experiment_directory=directory,
                manifest=manifest,
                resolved=resolved,
                data_dir=data_dir,
                project_root=root,
                backfilled=True,
            )
            raw_run_dir = Path(summary.get("raw_run_dir", ""))
            raw_metadata_path = raw_run_dir / "metadata.json"
            raw_metadata = (
                json.loads(raw_metadata_path.read_text(encoding="utf-8"))
                if raw_metadata_path.is_file()
                else {}
            )
            summary.update(
                {
                    "based_on": manifest["based_on"],
                    "reference_variant": manifest["reference_variant"],
                    "ablation_summary": manifest["ablation_summary"],
                    "git_commit": raw_metadata.get("git_commit"),
                    "snapshot_backfilled_after_run": True,
                    "snapshot_backfilled_at_utc": now_utc(),
                }
            )
            write_json(run_directory / "summary.json", summary)
            if (directory / "result.csv").is_file():
                shutil.copy2(
                    directory / "result.csv", run_directory / "leaderboard.csv"
                )
            base_report_path = directory / "report.md"
            if base_report_path.is_file():
                report = _enhanced_report(
                    base_report_path.read_text(encoding="utf-8"), diff
                )
                (run_directory / "report.md").write_text(report, encoding="utf-8")
                base_report_path.write_text(report, encoding="utf-8")
            legacy_path.unlink()
            _append_history(
                directory,
                "run_snapshot_backfilled",
                {
                    "run_id": run_id,
                    "config_hash_verified": resolved["config_hash"],
                    "snapshot_directory": str(run_directory),
                },
            )
            migrated.append(
                {
                    "experiment_id": directory.name,
                    "run_id": run_id,
                    "snapshot_directory": str(run_directory),
                }
            )
    rebuild_index(registry_root)
    return migrated


def decide_experiment(
    experiment_id: str,
    *,
    decision: str,
    reason: str,
    selected_variant: str | None = None,
    experiments_root: str | Path = EXPERIMENTS_ROOT,
) -> dict[str, Any]:
    if decision not in VALID_DECISIONS:
        raise ValueError(f"decision은 {sorted(VALID_DECISIONS)} 중 하나여야 합니다.")
    registry_root = Path(experiments_root).resolve()
    directory = experiment_dir(experiment_id, registry_root)
    manifest = _read_manifest(directory)
    state = _read_state(directory)
    if state["status"] not in {"completed", "decided"}:
        raise ValueError("완료된 실험만 최종 판단을 기록할 수 있습니다.")
    latest_run_id = state.get("latest_run_id")
    latest_path = _run_summary_path(directory, latest_run_id or "")
    if not latest_run_id or not latest_path.is_file():
        raise ValueError("판단 근거가 될 최신 RUN_NNN 기록이 없습니다.")
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    variants = {
        row["variant"] for row in latest.get("leaderboard", []) if "variant" in row
    }
    if decision == "adopt" and not selected_variant:
        raise ValueError("adopt 판단에는 --selected-variant가 필요합니다.")
    if decision == "keep_control" and not selected_variant:
        selected_variant = latest.get("control")
    if selected_variant and selected_variant not in variants:
        raise ValueError(
            f"최신 실행에 없는 variant입니다: {selected_variant}; "
            f"선택 가능={sorted(variants)}"
        )
    selected_result = next(
        (
            row
            for row in latest.get("leaderboard", [])
            if row.get("variant") == selected_variant
        ),
        None,
    )
    control_result = next(
        (
            row
            for row in latest.get("leaderboard", [])
            if row.get("variant") == latest.get("control")
        ),
        None,
    )
    payload = {
        "experiment_id": experiment_id,
        "decision": decision,
        "selected_variant": selected_variant,
        "reason": reason,
        "based_on": manifest["based_on"],
        "reference_variant": manifest["reference_variant"],
        "ablation_summary": manifest["ablation_summary"],
        "selected_result": selected_result,
        "control_result": control_result,
        "decided_at_utc": now_utc(),
        "based_on_run_id": latest_run_id,
    }
    write_json(directory / "decision.json", payload)
    lines = [
        f"# {experiment_id} decision",
        "",
        f"- decision: `{decision}`",
        f"- selected variant: `{selected_variant or ''}`",
        f"- based on run: `{state.get('latest_run_id') or ''}`",
        f"- comparison basis: `{manifest['based_on']}`",
        f"- reference variant: `{manifest['reference_variant']}`",
        f"- decided at: `{payload['decided_at_utc']}`",
        "",
        "## Ablation",
        "",
        manifest["ablation_summary"],
        "",
        "## Result",
        "",
    ]
    if selected_result is not None:
        lines.extend(
            [
                f"- selected Brier: `{selected_result.get('mean_brier')}`",
                "- delta Brier vs control: "
                f"`{selected_result.get('delta_brier_vs_control')}`",
                "- competition score: "
                f"`{selected_result.get('mean_brier_skill_score')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Reason",
            "",
            reason,
            "",
        ]
    )
    (directory / "decision.md").write_text("\n".join(lines), encoding="utf-8")
    state.update(
        {
            "status": "decided",
            "decision": decision,
            "selected_variant": selected_variant,
        }
    )
    _write_state(directory, state)
    _append_history(directory, "decision_recorded", payload)
    rebuild_index(registry_root)
    return payload


def show_experiment(
    experiment_id: str,
    experiments_root: str | Path = EXPERIMENTS_ROOT,
    *,
    include_history: bool = False,
) -> dict[str, Any]:
    directory = experiment_dir(experiment_id, experiments_root)
    manifest = _read_manifest(directory)
    state = _read_state(directory)
    latest = None
    if state.get("latest_run_id"):
        path = _run_summary_path(directory, state["latest_run_id"])
        if path.is_file():
            latest = json.loads(path.read_text(encoding="utf-8"))
    decision = None
    if (directory / "decision.json").is_file():
        decision = json.loads((directory / "decision.json").read_text(encoding="utf-8"))
    result = {
        "experiment": manifest,
        "state": state,
        "latest_run": latest,
        "decision": decision,
    }
    if include_history:
        result["history"] = [
            json.loads(line)
            for line in (directory / "history.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
    return result


def rebuild_index(
    experiments_root: str | Path = EXPERIMENTS_ROOT,
) -> list[dict[str, Any]]:
    registry_root = Path(experiments_root).resolve()
    registry_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for directory in sorted(registry_root.glob("EXP_*")):
        if not directory.is_dir():
            continue
        try:
            manifest = _read_manifest(directory)
            state = _read_state(directory)
        except (FileNotFoundError, ValueError):
            continue
        latest = None
        if state.get("latest_run_id"):
            path = _run_summary_path(directory, state["latest_run_id"])
            if path.is_file():
                latest = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "id": manifest["id"],
                "title": manifest["title"],
                "status": state["status"],
                "scope": manifest["change_scope"],
                "based_on": manifest["based_on"],
                "reference_variant": manifest["reference_variant"],
                "ablation_summary": manifest["ablation_summary"],
                "run_count": state.get("run_count", 0),
                "latest_run": state.get("latest_run_id"),
                "best_variant": latest.get("best_variant") if latest else None,
                "delta_brier": (
                    latest.get("best_delta_brier_vs_control") if latest else None
                ),
                "decision": state.get("decision"),
                "selected_variant": state.get("selected_variant"),
                "updated_at_utc": state.get("updated_at_utc"),
                "study_config": manifest["study_config"],
            }
        )
    columns = [
        "id", "title", "status", "scope", "based_on", "reference_variant",
        "ablation_summary", "run_count", "latest_run", "best_variant",
        "delta_brier", "decision", "selected_variant", "updated_at_utc",
        "study_config",
    ]
    pd.DataFrame(rows, columns=columns).to_csv(registry_root / "index.csv", index=False)
    return rows
