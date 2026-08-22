"""Run the integrated E00 and E11 TrackMan pitcher-linkage methods."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd


SUBMISSION_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SUBMISSION_DIR.parent
sys.path.insert(0, str(SUBMISSION_DIR / "src"))

from trackman_linkage import (  # noqa: E402
    E00_CONTEXT_COLUMNS,
    E11_ROW_CONTEXT_COLUMNS,
    E00Thresholds,
    E11Rules,
    match_pitchers_e00,
    match_pitchers_e11,
    summarize_linkage_methods,
)


MAIN_COLUMNS = list(
    dict.fromkeys(
        [
            "row_id",
            "pitcher_id",
            "game_type",
            *E11_ROW_CONTEXT_COLUMNS,
        ]
    )
)
TRACKMAN_COLUMNS = list(
    dict.fromkeys(
        [
            "trackman_id",
            "pitcher_trackman_id",
            "pitcher_team",
            *E11_ROW_CONTEXT_COLUMNS,
        ]
    )
)


def _load_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_path = data_dir / "train.csv"
    trackman_path = data_dir / "trackman_history.csv"
    missing = [str(path) for path in (train_path, trackman_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"필요한 데이터 파일이 없습니다: {missing}")
    main = pd.read_csv(train_path, usecols=MAIN_COLUMNS, encoding="utf-8-sig")
    trackman = pd.read_csv(
        trackman_path,
        usecols=TRACKMAN_COLUMNS,
        encoding="utf-8-sig",
    )
    return main, trackman


def _write_mapping(
    output_dir: Path,
    method: str,
    mapping: pd.DataFrame,
) -> None:
    mapping.to_csv(output_dir / f"{method}_pitcher_mapping.csv", index=False)
    mapping.loc[mapping["accepted"].eq(1)].to_csv(
        output_dir / f"{method}_approved_pitcher_mapping.csv",
        index=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPOSITORY_ROOT / "data",
        help="train.csv와 trackman_history.csv가 있는 폴더",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SUBMISSION_DIR / "results" / "trackman_linkage",
    )
    parser.add_argument("--method", choices=("both", "e00", "e11"), default="both")
    parser.add_argument("--cutoff-season", type=int, default=2025)
    parser.add_argument("--min-cosine", type=float, default=0.20)
    parser.add_argument("--min-margin", type=float, default=0.05)
    args = parser.parse_args()

    main_data, trackman_data = _load_data(args.data_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    e00 = None
    e11 = None
    thresholds = E00Thresholds(args.min_cosine, args.min_margin)
    rules = E11Rules()

    if args.method in {"both", "e00"}:
        e00 = match_pitchers_e00(
            main_data,
            trackman_data,
            cutoff_season=args.cutoff_season,
            thresholds=thresholds,
        )
        _write_mapping(args.output_dir, "E00", e00)

    if args.method in {"both", "e11"}:
        e11_result = match_pitchers_e11(
            main_data,
            trackman_data,
            cutoff_season=args.cutoff_season,
            rules=rules,
        )
        e11 = e11_result.mapping
        _write_mapping(args.output_dir, "E11", e11)
        e11_result.rounds.to_csv(args.output_dir / "E11_rounds.csv", index=False)

    payload = {
        "cutoff_policy": "season < cutoff_season",
        "cutoff_season": args.cutoff_season,
        "target_column_used": False,
        "E00": {
            "context_columns": list(E00_CONTEXT_COLUMNS),
            "thresholds": asdict(thresholds),
            "same_hand_candidates_only": True,
            "mutual_top1_required": True,
        },
        "E11": {
            "context_columns": list(E11_ROW_CONTEXT_COLUMNS),
            "rules": asdict(rules),
            "one_to_one_collision_repair": True,
            "tier_free_and_holdout_audits": True,
        },
        "results": summarize_linkage_methods(e00, e11),
    }
    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
