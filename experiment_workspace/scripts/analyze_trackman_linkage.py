from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


SEASONS = list(range(2019, 2024))


def mode_value(values: pd.Series):
    modes = values.mode(dropna=True)
    return modes.iloc[0] if len(modes) else values.iloc[-1]


def team_mapping(main: pd.DataFrame, track: pd.DataFrame) -> pd.DataFrame:
    main_counts = main.groupby(["pitcher_team_id", "season"]).size().unstack(fill_value=0)
    track_counts = track.groupby(["pitcher_team", "season"]).size().unstack(fill_value=0)
    main_counts = main_counts.reindex(columns=SEASONS, fill_value=0)
    track_counts = track_counts.reindex(columns=SEASONS, fill_value=0)
    main_share = main_counts.div(main_counts.sum(axis=0), axis=1)
    track_share = track_counts.div(track_counts.sum(axis=0), axis=1)
    cost = np.sqrt(
        np.mean(
            (
                main_share.to_numpy()[:, None, :]
                - track_share.to_numpy()[None, :, :]
            )
            ** 2,
            axis=2,
        )
    )
    rows, cols = linear_sum_assignment(cost)
    return pd.DataFrame(
        {
            "pitcher_team_id": main_counts.index.to_numpy()[rows],
            "pitcher_team": track_counts.index.to_numpy()[cols],
            "signature_rmse": cost[rows, cols],
        }
    )


def aggregate_main(main: pd.DataFrame) -> pd.DataFrame:
    grouped = main.groupby(["season", "pitcher_id"], observed=True, sort=False)
    result = grouped.agg(
        main_rows=("pitcher_id", "size"),
        pitcher_hand=("pitcher_hand", mode_value),
        pitcher_team_id=("pitcher_team_id", mode_value),
        start_mix_n=("asof_pitcher_pitchmix_n", "first"),
        end_mix_n=("asof_pitcher_pitchmix_n", "last"),
        start_fast=("asof_pitcher_fastball_rate", "first"),
        end_fast=("asof_pitcher_fastball_rate", "last"),
        start_break=("asof_pitcher_breaking_rate", "first"),
        end_break=("asof_pitcher_breaking_rate", "last"),
        start_off=("asof_pitcher_offspeed_rate", "first"),
        end_off=("asof_pitcher_offspeed_rate", "last"),
    ).reset_index()
    result["season_mix_n"] = (result["end_mix_n"] - result["start_mix_n"]).clip(lower=0)
    for short in ("fast", "break", "off"):
        start_count = result["start_mix_n"] * result[f"start_{short}"].fillna(0.0)
        end_count = result["end_mix_n"] * result[f"end_{short}"].fillna(0.0)
        delta = (end_count - start_count).clip(lower=0.0)
        result[f"{short}_share"] = (delta / result["season_mix_n"].replace(0, np.nan)).clip(0, 1)
    return result


def aggregate_track(track: pd.DataFrame) -> pd.DataFrame:
    history = track.copy()
    history["pitcher_hand"] = history["pitcher_hand"].map({"Right": 1, "Left": 2})
    for group, short in (("fastball", "fast"), ("breaking", "break"), ("offspeed", "off")):
        history[f"{short}_share"] = history["pitch_type_group"].eq(group).astype("float32")
    return (
        history.groupby(["season", "pitcher_trackman_id"], observed=True, sort=False)
        .agg(
            track_rows=("pitcher_trackman_id", "size"),
            pitcher_hand=("pitcher_hand", mode_value),
            pitcher_team=("pitcher_team", mode_value),
            fast_share=("fast_share", "mean"),
            break_share=("break_share", "mean"),
            off_share=("off_share", "mean"),
        )
        .reset_index()
    )


def nearest_candidates(
    main_pitchers: pd.DataFrame,
    track_pitchers: pd.DataFrame,
    mapping: pd.DataFrame,
) -> pd.DataFrame:
    mapped = dict(zip(mapping["pitcher_team_id"], mapping["pitcher_team"], strict=True))
    main_pitchers = main_pitchers.copy()
    main_pitchers["pitcher_team"] = main_pitchers["pitcher_team_id"].map(mapped)
    scale = (
        main_pitchers.groupby(["season", "pitcher_team"])["main_rows"].sum()
        / track_pitchers.groupby(["season", "pitcher_team"])["track_rows"].sum()
    )
    output: list[dict[str, object]] = []
    for row in main_pitchers.itertuples(index=False):
        candidates = track_pitchers.loc[
            track_pitchers["season"].eq(row.season)
            & track_pitchers["pitcher_team"].eq(row.pitcher_team)
            & track_pitchers["pitcher_hand"].eq(row.pitcher_hand)
        ].copy()
        if candidates.empty:
            continue
        factor = float(scale.get((row.season, row.pitcher_team), 1.0))
        candidates["count_error"] = np.abs(
            np.log1p(candidates["track_rows"] * factor) - np.log1p(row.main_rows)
        )
        mix_errors = []
        for short in ("fast", "break", "off"):
            value = getattr(row, f"{short}_share")
            if pd.notna(value):
                mix_errors.append(np.abs(candidates[f"{short}_share"] - value))
        candidates["mix_error"] = (
            pd.concat(mix_errors, axis=1).mean(axis=1) if mix_errors else 0.0
        )
        candidates["cost"] = candidates["count_error"] + 2.0 * candidates["mix_error"]
        candidates = candidates.nsmallest(2, "cost")
        best = candidates.iloc[0]
        second_cost = float(candidates.iloc[1]["cost"]) if len(candidates) > 1 else np.nan
        output.append(
            {
                "season": int(row.season),
                "pitcher_id": int(row.pitcher_id),
                "pitcher_team_id": int(row.pitcher_team_id),
                "pitcher_team": row.pitcher_team,
                "pitcher_hand": int(row.pitcher_hand),
                "main_rows": int(row.main_rows),
                "pitcher_trackman_id": int(best["pitcher_trackman_id"]),
                "track_rows": int(best["track_rows"]),
                "count_error": float(best["count_error"]),
                "mix_error": float(best["mix_error"]),
                "cost": float(best["cost"]),
                "margin": second_cost - float(best["cost"]),
            }
        )
    return pd.DataFrame(output)


def global_player_mapping(
    main_pitchers: pd.DataFrame,
    track_pitchers: pd.DataFrame,
    mapping: pd.DataFrame,
    *,
    fit_seasons: list[int],
) -> pd.DataFrame:
    team_map = dict(zip(mapping["pitcher_team_id"], mapping["pitcher_team"], strict=True))
    main = main_pitchers.loc[main_pitchers["season"].isin(fit_seasons)].copy()
    track = track_pitchers.loc[track_pitchers["season"].isin(fit_seasons)].copy()
    main["pitcher_team"] = main["pitcher_team_id"].map(team_map)
    main_totals = main.groupby("pitcher_id")["main_rows"].sum()
    track_totals = track.groupby("pitcher_trackman_id")["track_rows"].sum()
    main = main.loc[main["pitcher_id"].isin(main_totals[main_totals.ge(50)].index)]
    track = track.loc[
        track["pitcher_trackman_id"].isin(track_totals[track_totals.ge(50)].index)
    ]
    main_ids = np.sort(main["pitcher_id"].unique())
    track_ids = np.sort(track["pitcher_trackman_id"].unique())
    main_groups = {key: rows.set_index("season") for key, rows in main.groupby("pitcher_id")}
    track_groups = {
        key: rows.set_index("season") for key, rows in track.groupby("pitcher_trackman_id")
    }
    scale = (
        main.groupby(["season", "pitcher_team"])["main_rows"].sum()
        / track.groupby(["season", "pitcher_team"])["track_rows"].sum()
    )
    cost = np.full((len(main_ids), len(track_ids)), 20.0, dtype="float32")
    for i, main_id in enumerate(main_ids):
        left = main_groups[main_id]
        left_hand = int(mode_value(left["pitcher_hand"]))
        left_seasons = set(left.index.astype(int))
        for j, track_id in enumerate(track_ids):
            right = track_groups[track_id]
            if int(mode_value(right["pitcher_hand"])) != left_hand:
                continue
            right_seasons = set(right.index.astype(int))
            common = sorted(left_seasons & right_seasons)
            if not common:
                continue
            season_costs = []
            team_matches = 0
            for season in common:
                lrow = left.loc[season]
                rrow = right.loc[season]
                if isinstance(lrow, pd.DataFrame):
                    lrow = lrow.iloc[0]
                if isinstance(rrow, pd.DataFrame):
                    rrow = rrow.iloc[0]
                team_match = lrow["pitcher_team"] == rrow["pitcher_team"]
                team_matches += int(team_match)
                factor = float(scale.get((season, lrow["pitcher_team"]), 1.0))
                count_error = abs(
                    np.log1p(float(rrow["track_rows"]) * factor)
                    - np.log1p(float(lrow["main_rows"]))
                )
                mix_parts = np.asarray(
                    [
                        abs(float(lrow[f"{short}_share"]) - float(rrow[f"{short}_share"]))
                        for short in ("fast", "break", "off")
                    ],
                    dtype="float64",
                )
                mix = float(np.nanmean(mix_parts)) if np.isfinite(mix_parts).any() else 0.5
                season_costs.append(count_error + 2.0 * mix + (0.0 if team_match else 1.5))
            if team_matches == 0:
                continue
            union = left_seasons | right_seasons
            activity_penalty = 0.5 * len(left_seasons ^ right_seasons) / len(union)
            overlap_bonus = 0.1 * (len(common) - 1)
            pair_cost = float(np.mean(season_costs) + activity_penalty - overlap_bonus)
            cost[i, j] = pair_cost if np.isfinite(pair_cost) else 20.0
    cost = np.nan_to_num(cost, nan=20.0, posinf=20.0, neginf=20.0)
    rows, cols = linear_sum_assignment(cost)
    selected = pd.DataFrame(
        {
            "pitcher_id": main_ids[rows],
            "pitcher_trackman_id": track_ids[cols],
            "global_cost": cost[rows, cols],
        }
    )
    return selected.loc[selected["global_cost"].lt(10.0)].reset_index(drop=True)


def heldout_linkage_metrics(
    player_map: pd.DataFrame,
    main_pitchers: pd.DataFrame,
    track_pitchers: pd.DataFrame,
    mapping: pd.DataFrame,
    *,
    season: int,
) -> dict[str, float | int]:
    team_map = dict(zip(mapping["pitcher_team_id"], mapping["pitcher_team"], strict=True))
    main = main_pitchers.loc[main_pitchers["season"].eq(season)].copy()
    main["pitcher_team"] = main["pitcher_team_id"].map(team_map)
    track = track_pitchers.loc[track_pitchers["season"].eq(season)].copy()
    joined = (
        player_map.merge(main, on="pitcher_id", how="inner")
        .merge(track, on="pitcher_trackman_id", how="inner", suffixes=("_main", "_track"))
    )
    if joined.empty:
        return {"pairs": 0}
    scale = main["main_rows"].sum() / track["track_rows"].sum()
    count_error = np.abs(
        np.log1p(joined["track_rows"] * scale) - np.log1p(joined["main_rows"])
    )
    mix_error = pd.concat(
        [
            (joined[f"{short}_share_main"] - joined[f"{short}_share_track"]).abs()
            for short in ("fast", "break", "off")
        ],
        axis=1,
    ).mean(axis=1)
    return {
        "pairs": int(len(joined)),
        "team_match_fraction": float(
            joined["pitcher_team_main"].eq(joined["pitcher_team_track"]).mean()
        ),
        "median_count_error": float(count_error.median()),
        "median_mix_error": float(mix_error.median()),
    }


def summarize(candidates: pd.DataFrame, mapping: pd.DataFrame) -> dict[str, object]:
    eligible = candidates.loc[candidates["main_rows"].ge(50)].copy()
    repeat = eligible.groupby("pitcher_id").filter(lambda rows: len(rows) >= 2)
    consistency = repeat.groupby("pitcher_id")["pitcher_trackman_id"].agg(
        lambda values: values.value_counts(normalize=True).iloc[0]
    )
    return {
        "reference_seasons": SEASONS,
        "team_mapping_max_rmse": float(mapping["signature_rmse"].max()),
        "candidate_rows": int(len(candidates)),
        "eligible_rows_main_n_ge_50": int(len(eligible)),
        "median_count_error": float(eligible["count_error"].median()),
        "median_mix_error": float(eligible["mix_error"].median()),
        "median_top2_margin": float(eligible["margin"].median()),
        "fraction_count_error_below_005": float(eligible["count_error"].lt(0.05).mean()),
        "repeat_pitchers": int(consistency.size),
        "fraction_repeat_pitchers_consistency_100pct": float(consistency.eq(1.0).mean()),
        "fraction_repeat_pitchers_consistency_ge_80pct": float(consistency.ge(0.8).mean()),
        "median_repeat_pitcher_consistency": float(consistency.median()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    main_columns = [
        "season", "pitcher_id", "pitcher_hand", "pitcher_team_id",
        "asof_pitcher_pitchmix_n", "asof_pitcher_fastball_rate",
        "asof_pitcher_breaking_rate", "asof_pitcher_offspeed_rate",
    ]
    track_columns = [
        "season", "pitcher_trackman_id", "pitcher_hand", "pitcher_team",
        "pitch_type_group",
    ]
    train = pd.read_csv(args.data_dir / "train.csv", usecols=main_columns)
    train = train.loc[train["season"].isin(SEASONS)]
    track = pd.read_csv(args.data_dir / "trackman_history.csv", usecols=track_columns)
    track = track.loc[track["season"].isin(SEASONS)]
    mapping = team_mapping(train, track)
    main_pitchers = aggregate_main(train)
    track_pitchers = aggregate_track(track)
    candidates = nearest_candidates(main_pitchers, track_pitchers, mapping)
    summary = summarize(candidates, mapping)
    global_2019_2022 = global_player_mapping(
        main_pitchers, track_pitchers, mapping, fit_seasons=list(range(2019, 2023))
    )
    global_2019_2023 = global_player_mapping(
        main_pitchers, track_pitchers, mapping, fit_seasons=SEASONS
    )
    stable = global_2019_2022.merge(
        global_2019_2023, on="pitcher_id", suffixes=("_pre2023", "_all")
    )
    summary["global_mapping_rows_2019_2022"] = int(len(global_2019_2022))
    summary["global_mapping_rows_2019_2023"] = int(len(global_2019_2023))
    summary["global_mapping_stability_fraction"] = float(
        stable["pitcher_trackman_id_pre2023"].eq(stable["pitcher_trackman_id_all"]).mean()
    )
    summary["heldout_2023"] = heldout_linkage_metrics(
        global_2019_2022, main_pitchers, track_pitchers, mapping, season=2023
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    mapping.to_csv(args.output_dir / "team_mapping.csv", index=False)
    candidates.to_csv(args.output_dir / "pitcher_candidates_by_season.csv", index=False)
    global_2019_2022.to_csv(
        args.output_dir / "global_player_mapping_2019_2022.csv", index=False
    )
    global_2019_2023.to_csv(
        args.output_dir / "global_player_mapping_2019_2023.csv", index=False
    )
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
