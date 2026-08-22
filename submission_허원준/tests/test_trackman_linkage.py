from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


SUBMISSION_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUBMISSION_DIR / "src"))

from trackman_linkage import (  # noqa: E402
    E11Rules,
    match_pitchers_e00,
    match_pitchers_e11,
)


def _row(
    row_id: str | int,
    pitcher_id: int,
    context: int,
    *,
    trackman: bool = False,
    season: int = 2024,
    hand: int = 2,
) -> dict[str, object]:
    row = {
        "trackman_id" if trackman else "row_id": row_id,
        "pitcher_trackman_id" if trackman else "pitcher_id": pitcher_id,
        "season": season,
        "game_month": context,
        "game_dayofweek": context % 7,
        "inning": context,
        "top_bottom": "Top" if trackman else "T",
        "balls_before": context % 4,
        "strikes_before": context % 3,
        "outs_before": context % 3,
        "pitcher_hand": "Right" if trackman and hand == 2 else hand,
        "batter_hand": "Left" if trackman else 1,
    }
    if trackman:
        row["pitcher_team"] = "DOO_BEA"
    else:
        row["game_type"] = "R"
    return row


def test_e00_matches_distinct_context_fingerprints() -> None:
    main = pd.DataFrame(
        [
            *[_row(f"TRAIN_{i}", 1, i) for i in (1, 2, 3)],
            *[_row(f"TRAIN_{i}", 2, i) for i in (4, 5, 6)],
        ]
    )
    trackman = pd.DataFrame(
        [
            *[_row(100 + i, 101, i, trackman=True) for i in (1, 2, 3)],
            *[_row(200 + i, 202, i, trackman=True) for i in (4, 5, 6)],
        ]
    )

    mapping = match_pitchers_e00(main, trackman)

    accepted = mapping.loc[mapping["accepted"].eq(1)]
    assert dict(zip(accepted["pitcher_id"], accepted["pitcher_trackman_id"])) == {
        1: 101,
        2: 202,
    }


def test_e11_accepts_three_unique_votes_and_preserves_one_to_one() -> None:
    main = pd.DataFrame(
        [
            *[_row(f"TRAIN_{i}", 1, i) for i in (1, 2, 3)],
            *[_row(f"TRAIN_{i}", 2, i) for i in (4, 5, 6)],
        ]
    )
    trackman = pd.DataFrame(
        [
            *[_row(100 + i, 101, i, trackman=True) for i in (1, 2, 3)],
            *[_row(200 + i, 202, i, trackman=True) for i in (4, 5, 6)],
        ]
    )

    result = match_pitchers_e11(
        main,
        trackman,
        rules=E11Rules(min_votes=3, max_rounds=3),
    )
    accepted = result.mapping.loc[result.mapping["accepted"].eq(1)]

    assert dict(zip(accepted["pitcher_id"], accepted["pitcher_trackman_id"])) == {
        1: 101,
        2: 202,
    }
    assert not accepted["pitcher_trackman_id"].duplicated().any()


def test_both_methods_ignore_rows_at_or_after_cutoff() -> None:
    main = pd.DataFrame(
        [
            *[_row(f"TRAIN_{i}", 1, i) for i in (1, 2, 3)],
            _row("TRAIN_999", 999, 9, season=2025),
        ]
    )
    trackman = pd.DataFrame(
        [
            *[_row(100 + i, 101, i, trackman=True) for i in (1, 2, 3)],
            _row(999, 9999, 9, trackman=True, season=2025),
            _row(888, 8888, 8, trackman=True),
        ]
    )

    e00 = match_pitchers_e00(main, trackman, cutoff_season=2025)
    e11 = match_pitchers_e11(main, trackman, cutoff_season=2025).mapping

    assert set(e00["pitcher_id"]) == {1}
    assert set(e11["pitcher_id"]) == {1}
