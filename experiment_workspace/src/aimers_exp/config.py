from __future__ import annotations

import hashlib
import json
import os
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_ROOT = PROJECT_ROOT / "experiments" / "BASELINE_001_main55"
CONFIG_ROOT = BASELINE_ROOT


def resolve_data_dir() -> Path:
    configured = os.environ.get("AIMERS_DATA_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return PROJECT_ROOT / "data"


DEFAULT_DATA_DIR = resolve_data_dir()


def load_toml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.is_file():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {path}")
    with path.open("rb") as stream:
        return tomllib.load(stream)


def _load_named(directory: str, name: str, section: str) -> dict[str, Any]:
    document = load_toml(CONFIG_ROOT / directory / f"{name}.toml")
    if section not in document:
        raise ValueError(f"{name}.toml에 [{section}] 섹션이 없습니다.")
    return document[section]


def canonical_hash(value: Any, length: int = 12) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if not isinstance(value, dict):
        return {prefix: value}
    flattened: dict[str, Any] = {}
    for key, child in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        flattened.update(_flatten(child, path))
    return flattened


def changed_fields(control: dict[str, Any], variant: dict[str, Any]) -> list[str]:
    left = _flatten(control)
    right = _flatten(variant)
    return sorted(
        key
        for key in set(left) | set(right)
        if left.get(key, object()) != right.get(key, object())
    )


def resolve_study(path: str | Path) -> dict[str, Any]:
    document = load_toml(path)
    if "study" not in document or "variants" not in document:
        raise ValueError("study 설정에는 [study]와 [[variants]]가 필요합니다.")
    study = document["study"]
    variants = document["variants"]
    required = {"id", "protocol", "control", "change_scope"}
    missing = sorted(required - set(study))
    if missing:
        raise ValueError(f"study 필수 설정 누락: {missing}")
    if not variants:
        raise ValueError("study에 variant가 없습니다.")

    names = [variant.get("name") for variant in variants]
    if len(names) != len(set(names)) or any(name is None for name in names):
        raise ValueError("variant name은 누락 없이 고유해야 합니다.")
    if study["control"] not in names:
        raise ValueError(f"control {study['control']!r}이 variants에 없습니다.")

    protocol = _load_named("protocols", study["protocol"], "protocol")
    resolved_variants = []
    for variant in variants:
        if "model" not in variant or "features" not in variant:
            raise ValueError(f"variant {variant['name']}에 model/features가 필요합니다.")
        resolved_variants.append(
            {
                "name": variant["name"],
                "change": variant.get("change", ""),
                "model": _load_named("models", variant["model"], "model"),
                "features": _load_named(
                    "features", variant["features"], "features"
                ),
            }
        )

    control = next(
        variant
        for variant in resolved_variants
        if variant["name"] == study["control"]
    )
    allowed = set(study["change_scope"])
    unknown_scopes = sorted(allowed - {"model", "features"})
    if unknown_scopes:
        raise ValueError(f"지원하지 않는 change_scope: {unknown_scopes}")

    for variant in resolved_variants:
        comparable = {
            "model": variant["model"],
            "features": variant["features"],
        }
        control_comparable = {
            "model": control["model"],
            "features": control["features"],
        }
        differences = changed_fields(control_comparable, comparable)
        changed_sections = {field.split(".", 1)[0] for field in differences}
        disallowed = sorted(changed_sections - allowed)
        if disallowed:
            raise ValueError(
                f"variant {variant['name']}이 change_scope 밖의 설정을 변경했습니다: "
                f"{disallowed}"
            )
        variant["changed_fields_vs_control"] = differences

    resolved = {
        "study": study,
        "protocol": protocol,
        "variants": resolved_variants,
    }
    resolved["config_hash"] = canonical_hash(resolved)
    return resolved


def resolve_final(
    path: str | Path = BASELINE_ROOT / "final.toml",
) -> dict[str, Any]:
    document = load_toml(path)
    if "final" not in document:
        raise ValueError("최종 설정에 [final] 섹션이 없습니다.")
    final = document["final"]
    for key in ("protocol", "model", "features"):
        if key not in final:
            raise ValueError(f"최종 설정에 {key!r}이 없습니다.")
    resolved = {
        "final": final,
        "protocol": _load_named("protocols", final["protocol"], "protocol"),
        "model": _load_named("models", final["model"], "model"),
        "features": _load_named("features", final["features"], "features"),
    }
    resolved["config_hash"] = canonical_hash(resolved)
    return resolved
