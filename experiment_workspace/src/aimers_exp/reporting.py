from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def render_study_report(
    resolved: dict[str, Any], leaderboard: pd.DataFrame, run_dir: Path
) -> str:
    study = resolved["study"]
    protocol = resolved["protocol"]
    lines = [
        f"# {study['id']}: {study.get('description', '')}",
        "",
        f"- 가설: {study.get('hypothesis', '')}",
        f"- control: `{study['control']}`",
        f"- 변경 허용 범위: `{', '.join(study['change_scope'])}`",
        f"- 검증 시즌: `{protocol['validation_seasons']}`",
        f"- 분할 규칙: `{protocol['split_rule']}`",
        f"- calibration: `{protocol['calibration']}`",
        f"- config hash: `{resolved['config_hash']}`",
        "",
        "## 결과",
        "",
    ]
    columns = [
        "variant",
        "change",
        "mean_brier",
        "delta_brier_vs_control",
        "seasons_improved",
        "mean_brier_skill_score",
    ]
    display = leaderboard[columns].copy()
    for column in ("mean_brier", "delta_brier_vs_control"):
        display[column] = display[column].map(lambda value: f"{value:.9f}")
    display["mean_brier_skill_score"] = display[
        "mean_brier_skill_score"
    ].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    headers = list(display.columns)
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in display.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(map(str, row)) + " |")
    lines.extend(["", "## 실제 변경 필드", ""])
    for variant in resolved["variants"]:
        fields = variant["changed_fields_vs_control"] or ["control"]
        lines.append(f"- `{variant['name']}`: {', '.join(fields)}")
    lines.extend(
        [
            "",
            "## 판정 메모",
            "",
            "Brier는 낮을수록 좋고 `delta_brier_vs_control < 0`이면 개선입니다.",
            "자동 표는 수치만 정리하며, 최종 채택 이유는 이 아래에 사람이 기록합니다.",
            "",
            "- 결론:",
            "- 다음 실험:",
            "",
            f"원본 산출물: `{run_dir}`",
        ]
    )
    return "\n".join(lines) + "\n"
