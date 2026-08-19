from __future__ import annotations

from collections.abc import Collection
from typing import Any

import numpy as np
import pandas as pd

ID_COL = "row_id"
TARGET_COL = "control_success"

CUSTOM_FEATURES = (
    "pitcher_gap_prev1_career",
    "pitcher_gap_prev3_career",
    "pitcher_gap_prev5_career",
    "win_expectancy_dist50",
    "count_diff",
    "count_total",
    "same_hand_matchup",
    "pressure_x_recent_form",
    "runners_x_li",
    "batter_success_rate_shrunk",
    "reverse_rate_x_li",
    "middle_rate_x_count_diff",
    "late_inning_x_recent_form",
    "offspeed_x_li",
    "recent_history_missing",
    "pitcher_history_missing",
    "batter_history_missing",
    "pitcher_success_rate_shrunk",
    "pitcher_reverse_rate_shrunk",
    "success_minus_reverse",
    "log1p_pitcher_n",
    "log1p_batter_n",
    "pitcher_team_win_expectancy",
    "log1p_li",
    "scoring_position",
    "scoring_position_x_li",
    "count_state",
    "is_full_count",
    "has_two_strikes",
    "has_three_balls",
    "has_two_outs",
    "count_hands_state",
    "count_matchup_state",
    "count_out_state",
    "count_hands_out_state",
    "season_pitch_index_safe",
    "season_progress_safe",
    "season_phase_20_safe",
    "recent_success_blend_135",
    "recent_middle_blend_135",
    "recent_quality_blend_135",
    "recent_success_span_15",
    "recent_middle_span_15",
    "hand_matchup_state",
    "same_hand_x_fastball",
    "same_hand_x_breaking",
    "same_hand_x_offspeed",
    "pitcher_history_bucket",
    "batter_history_bucket",
    "pitcher_history_reliability_k100",
    "batter_history_reliability_k100",
    "pitcher_success_x_reliability",
    "batter_success_x_reliability",
    "pitcher_reverse_x_reliability",
    "pitcher_middle_x_reliability",
    "pitcher_ball_x_reliability",
    "pitcher_strike_x_reliability",
    "pitcher_fastball_x_reliability",
    "pitcher_breaking_x_reliability",
    "pitcher_offspeed_x_reliability",
    "pitcher_history_reliability_k50",
    "batter_history_reliability_k50",
    "pitcher_success_x_reliability_k50",
    "batter_success_x_reliability_k50",
    "pitcher_reverse_x_reliability_k50",
    "pitcher_middle_x_reliability_k50",
    "pitcher_history_reliability_k200",
    "batter_history_reliability_k200",
    "pitcher_success_x_reliability_k200",
    "batter_success_x_reliability_k200",
    "pitcher_reverse_x_reliability_k200",
    "pitcher_middle_x_reliability_k200",
    "pitcher_hand_x_fastball",
    "pitcher_hand_x_breaking",
    "pitcher_hand_x_offspeed",
    "batter_hand_x_fastball",
    "batter_hand_x_breaking",
    "batter_hand_x_offspeed",
    "matchup0_x_fastball",
    "matchup0_x_breaking",
    "matchup0_x_offspeed",
    "matchup1_x_fastball",
    "matchup1_x_breaking",
    "matchup1_x_offspeed",
    "matchup2_x_fastball",
    "matchup2_x_breaking",
    "matchup2_x_offspeed",
    "matchup3_x_fastball",
    "matchup3_x_breaking",
    "matchup3_x_offspeed",
    "inning_phase_state",
    "early_inning_x_li",
    "middle_inning_x_li",
    "late_inning_x_li",
    "extra_inning_x_li",
    "late_inning_x_pitcher_success",
    "late_inning_x_pitcher_reverse",
    "late_inning_x_pitcher_middle",
    "two_strike_x_pitcher_success",
    "two_strike_x_pitcher_reverse",
    "two_strike_x_pitcher_middle",
    "three_ball_x_pitcher_success",
    "three_ball_x_pitcher_reverse",
    "three_ball_x_pitcher_middle",
    "full_count_x_pitcher_success",
    "full_count_x_pitcher_reverse",
    "full_count_x_pitcher_middle",
    "season_pitch_index",
    "season_progress_proxy",
    "season_phase_20",
    "pitcher_previous_pitch_success",
    "pitcher_recent3_pitch_success",
    "pitcher_recent5_pitch_success",
    "pitcher_recent10_pitch_success",
    "pitcher_recent20_pitch_success",
    "pitcher_recent30_pitch_success",
    "pitcher_recent50_pitch_success",
    "batter_previous_pitch_success",
    "batter_recent2_pitch_success",
    "batter_recent3_pitch_success",
    "batter_recent5_pitch_success",
    "batter_recent8_pitch_success",
    "batter_recent10_pitch_success",
    "pitcher_previous_pitch_reverse",
    "pitcher_recent3_pitch_reverse",
    "pitcher_recent5_pitch_reverse",
    "pitcher_recent10_pitch_reverse",
    "pitcher_recent20_pitch_reverse",
    "pitcher_recent50_pitch_reverse",
    "pitcher_previous_pitch_middle",
    "pitcher_recent3_pitch_middle",
    "pitcher_recent5_pitch_middle",
    "pitcher_recent10_pitch_middle",
    "pitcher_previous_pitch_ball",
    "pitcher_recent3_pitch_ball",
    "pitcher_recent5_pitch_ball",
    "pitcher_recent10_pitch_ball",
    "batter_previous_pitch_middle",
    "batter_recent3_pitch_middle",
    "batter_recent5_pitch_middle",
    "batter_recent10_pitch_middle",
    "pitcher_row_gap",
    "batter_row_gap",
    "pitcher_is_immediate",
    "batter_is_immediate",
    "same_matchup_previous",
    "previous_global_success",
    "previous_global_reverse",
    "plate_appearance_pitch_index",
    "plate_appearance_recent2_success",
    "plate_appearance_recent3_success",
    "pitcher_lag2_pitch_success",
    "pitcher_lag3_pitch_success",
    "pitcher_lag5_pitch_success",
    "batter_lag2_pitch_success",
    "batter_lag3_pitch_success",
    "pitcher_last3_success_pattern",
    "batter_last3_success_pattern",
    "pitcher_success_ewm05",
    "pitcher_success_ewm10",
    "batter_success_ewm10",
    "batter_success_ewm20",
    "pitcher_reverse_ewm05",
    "pitcher_reverse_ewm10",
    "global_recent5_success",
    "global_recent10_success",
    "global_recent20_success",
    "global_recent50_success",
    "global_recent100_success",
    "global_recent75_success",
    "global_recent125_success",
    "global_recent150_success",
    "global_recent200_success",
    "global_recent175_success",
    "global_recent225_success",
    "global_recent250_success",
    "global_recent300_success",
    "global_recent400_success",
    "global_recent50_reverse",
    "global_recent100_reverse",
    "global_recent150_reverse",
    "global_recent200_reverse",
    "global_recent300_reverse",
    "game_recent200_success",
    "pitcher_team_recent200_success",
    "batter_team_recent200_success",
    "game_recent100_middle",
    "game_recent200_middle",
    "pitcher_team_recent200_middle",
    "batter_team_recent200_middle",
    "pitcher_target_effect_k50",
    "pitcher_target_effect_k200",
    "batter_target_effect_k50",
    "batter_target_effect_k200",
    "pitcher_team_target_effect_k500",
    "batter_team_target_effect_k500",
    "pitcher_season_n",
    "pitcher_season_success_rate_k20",
    "pitcher_season_reverse_rate_k20",
    "pitcher_season_middle_rate_k20",
    "pitcher_season_ball_rate_k20",
    "pitcher_season_strike_rate_k20",
    "batter_season_n",
    "batter_season_success_rate_k20",
    "batter_season_middle_rate_k20",
    "pitcher_season_success_rate_k5",
    "pitcher_season_success_rate_k10",
    "pitcher_season_success_rate_k50",
    "pitcher_season_success_rate_k100",
    "batter_season_success_rate_k5",
    "batter_season_success_rate_k10",
    "batter_season_success_rate_k50",
    "batter_season_success_rate_k100",
    "pitcher_season_success_count_log",
    "pitcher_season_failure_count_log",
    "pitcher_season_reverse_count_log",
    "pitcher_season_middle_count_log",
    "pitcher_season_ball_count_log",
    "pitcher_season_strike_count_log",
    "batter_season_success_count_log",
    "batter_season_failure_count_log",
    "batter_season_middle_count_log",
    "pitcher_season_n_exact",
    "pitcher_season_success_rate_exact_k20",
    "pitcher_season_success_rate_exact_k50",
    "batter_season_n_exact",
    "batter_season_success_rate_exact_k20",
    "batter_season_success_rate_exact_k50",
    "pitcher_season_ball_rate_k500",
    "pitcher_season_strike_rate_k200",
    "batter_season_middle_rate_k200",
    "pitcher_season_fastball_rate_k20",
    "pitcher_season_breaking_rate_k20",
    "pitcher_season_offspeed_rate_k20",
    "pitcher_season_success_delta_career",
    "pitcher_season_reverse_delta_career",
    "pitcher_season_middle_delta_career",
    "pitcher_season_ball_delta_career",
    "pitcher_season_strike_delta_career",
    "batter_season_success_delta_career",
    "batter_season_middle_delta_career",
    "pitcher_prev1_minus_prev3",
    "pitcher_prev3_minus_prev5",
    "pitcher_prev3_minus_season_success",
    "count_hands_target_effect",
    "count_out_base_target_effect",
    "inning_game_target_effect",
    "pressure_state_target_effect",
    "track_context_rel_speed",
    "track_context_spin_rate",
    "track_context_induced_vert_break",
    "track_context_abs_horz_break",
    "track_context_extension",
    "track_context_zone_speed",
    "track_context_fastball_share",
    "track_context_breaking_share",
    "track_context_offspeed_share",
    "previous_season_target_rate",
    "season_trend_prior",
    "pitcher_prev_season_rate",
    "pitcher_prev_season_log_n",
    "pitcher_prev_season_delta",
    "batter_prev_season_rate",
    "batter_prev_season_log_n",
    "batter_prev_season_delta",
    "pitcher_team_prev_season_rate",
    "batter_team_prev_season_rate",
)

MAIN55_CUSTOM_FEATURES = CUSTOM_FEATURES[:14]
TEMPORAL_TARGET_FEATURES = frozenset(CUSTOM_FEATURES[-10:])
REFERENCE_TARGET_FEATURES = frozenset(
    {
        "pitcher_target_effect_k50",
        "pitcher_target_effect_k200",
        "batter_target_effect_k50",
        "batter_target_effect_k200",
        "pitcher_team_target_effect_k500",
        "batter_team_target_effect_k500",
    }
)
REFERENCE_STATE_FEATURES = frozenset(
    {
        "pitcher_season_n",
        "pitcher_season_success_rate_k20",
        "pitcher_season_reverse_rate_k20",
        "pitcher_season_middle_rate_k20",
        "pitcher_season_ball_rate_k20",
        "pitcher_season_strike_rate_k20",
        "batter_season_n",
        "batter_season_success_rate_k20",
        "batter_season_middle_rate_k20",
        "pitcher_season_success_rate_k5",
        "pitcher_season_success_rate_k10",
        "pitcher_season_success_rate_k50",
        "pitcher_season_success_rate_k100",
        "batter_season_success_rate_k5",
        "batter_season_success_rate_k10",
        "batter_season_success_rate_k50",
        "batter_season_success_rate_k100",
        "pitcher_season_success_count_log",
        "pitcher_season_failure_count_log",
        "pitcher_season_reverse_count_log",
        "pitcher_season_middle_count_log",
        "pitcher_season_ball_count_log",
        "pitcher_season_strike_count_log",
        "batter_season_success_count_log",
        "batter_season_failure_count_log",
        "batter_season_middle_count_log",
        "pitcher_season_n_exact",
        "pitcher_season_success_rate_exact_k20",
        "pitcher_season_success_rate_exact_k50",
        "batter_season_n_exact",
        "batter_season_success_rate_exact_k20",
        "batter_season_success_rate_exact_k50",
        "pitcher_season_ball_rate_k500",
        "pitcher_season_strike_rate_k200",
        "batter_season_middle_rate_k200",
        "pitcher_season_fastball_rate_k20",
        "pitcher_season_breaking_rate_k20",
        "pitcher_season_offspeed_rate_k20",
        "pitcher_season_success_delta_career",
        "pitcher_season_reverse_delta_career",
        "pitcher_season_middle_delta_career",
        "pitcher_season_ball_delta_career",
        "pitcher_season_strike_delta_career",
        "batter_season_success_delta_career",
        "batter_season_middle_delta_career",
        "pitcher_prev1_minus_prev3",
        "pitcher_prev3_minus_prev5",
        "pitcher_prev3_minus_season_success",
    }
)
REFERENCE_CONTEXT_FEATURES = frozenset(
    {
        "count_hands_target_effect",
        "count_out_base_target_effect",
        "inning_game_target_effect",
        "pressure_state_target_effect",
    }
)
REFERENCE_PROGRESS_FEATURES = frozenset(
    {
        "season_pitch_index_safe",
        "season_progress_safe",
        "season_phase_20_safe",
    }
)
TRACKMAN_CONTEXT_FEATURES = frozenset(
    {
        "track_context_rel_speed",
        "track_context_spin_rate",
        "track_context_induced_vert_break",
        "track_context_abs_horz_break",
        "track_context_extension",
        "track_context_zone_speed",
        "track_context_fastball_share",
        "track_context_breaking_share",
        "track_context_offspeed_share",
    }
)
SEQUENTIAL_FEATURES = frozenset(
    name
    for name in CUSTOM_FEATURES
    if (
        "previous_pitch" in name
        or "recent" in name and "pitch_" in name
        or "_lag" in name
        or "success_pattern" in name
        or "_ewm" in name
        or name.startswith("global_recent")
        or name.startswith("game_recent")
        or name.startswith("pitcher_team_recent")
        or name.startswith("batter_team_recent")
        or name
        in {
            "season_pitch_index",
            "season_progress_proxy",
            "season_phase_20",
            "pitcher_row_gap",
            "batter_row_gap",
            "pitcher_is_immediate",
            "batter_is_immediate",
            "same_matchup_previous",
            "previous_global_success",
            "previous_global_reverse",
            "plate_appearance_pitch_index",
            "plate_appearance_recent2_success",
            "plate_appearance_recent3_success",
        }
    )
)
ROW_LOCAL_CUSTOM_FEATURES = tuple(
    name
    for name in CUSTOM_FEATURES
    if name
    not in TEMPORAL_TARGET_FEATURES
    | REFERENCE_TARGET_FEATURES
    | REFERENCE_STATE_FEATURES
    | REFERENCE_CONTEXT_FEATURES
    | REFERENCE_PROGRESS_FEATURES
    | TRACKMAN_CONTEXT_FEATURES
    | SEQUENTIAL_FEATURES
)


def _safe_rate(series: pd.Series, prior: float) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(prior)


def _safe_count(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0)


def engineer_features(
    frame: pd.DataFrame,
    *,
    success_prior: float,
    shrinkage_k: float = 50.0,
    requested_custom: Collection[str] | None = None,
) -> pd.DataFrame:
    """Create only rule-compliant, row-local features.

    ``requested_custom`` is deliberately checked before any sequence operation.
    Evaluation rows must never affect one another, even through an unused
    intermediate column.
    """
    requested = frozenset(
        ROW_LOCAL_CUSTOM_FEATURES
        if requested_custom is None
        else requested_custom
    )
    unknown = requested.difference(CUSTOM_FEATURES)
    if unknown:
        raise ValueError(f"알 수 없는 custom feature: {sorted(unknown)}")
    forbidden = requested.intersection(SEQUENTIAL_FEATURES)
    if forbidden:
        raise ValueError(
            "대회 규칙상 평가 행 간 연산이 필요한 feature는 사용할 수 없습니다: "
            f"{sorted(forbidden)}"
        )
    out = frame.copy()
    for window in (1, 3, 5):
        out[f"pitcher_gap_prev{window}_career"] = (
            out[f"asof_pitcher_prev{window}_game_success_rate"]
            - out["asof_pitcher_success_rate"]
        ).astype("float32")

    out["win_expectancy_dist50"] = (
        out["home_win_expectancy"] - 50.0
    ).abs().astype("float32")
    out["count_diff"] = (
        out["balls_before"] - out["strikes_before"]
    ).astype("int8")
    out["count_total"] = (
        out["balls_before"] + out["strikes_before"]
    ).astype("int8")
    out["same_hand_matchup"] = (
        out["pitcher_hand"] == out["batter_hand"]
    ).astype("int8")
    out["pressure_x_recent_form"] = (
        out["count_diff"] * out["asof_pitcher_prev3_game_success_rate"]
    ).astype("float32")
    out["runners_x_li"] = (out["num_runners_on"] * out["li"]).astype(
        "float32"
    )

    batter_n = _safe_count(out["asof_batter_n"])
    batter_rate = _safe_rate(out["asof_batter_success_rate"], success_prior)
    out["batter_success_rate_shrunk"] = (
        (batter_rate * batter_n + success_prior * shrinkage_k)
        / (batter_n + shrinkage_k)
    ).astype("float32")
    out["reverse_rate_x_li"] = (
        out["asof_pitcher_reverse_rate"] * out["li"]
    ).astype("float32")
    out["middle_rate_x_count_diff"] = (
        out["asof_pitcher_middle_rate"] * out["count_diff"]
    ).astype("float32")
    out["late_inning_x_recent_form"] = (
        (out["inning"] >= 7).astype("int8")
        * out["asof_pitcher_prev3_game_success_rate"]
    ).astype("float32")
    out["offspeed_x_li"] = (
        out["asof_pitcher_offspeed_rate"] * out["li"]
    ).astype("float32")

    out["recent_history_missing"] = out[
        "asof_pitcher_prev1_game_success_rate"
    ].isna().astype("int8")
    out["pitcher_history_missing"] = out[
        "asof_pitcher_success_rate"
    ].isna().astype("int8")
    out["batter_history_missing"] = out[
        "asof_batter_success_rate"
    ].isna().astype("int8")

    pitcher_n = _safe_count(out["asof_pitcher_n"])
    pitcher_success = _safe_rate(
        out["asof_pitcher_success_rate"], success_prior
    )
    pitcher_reverse = _safe_rate(
        out["asof_pitcher_reverse_rate"], 1.0 - success_prior
    )
    out["pitcher_success_rate_shrunk"] = (
        (pitcher_success * pitcher_n + success_prior * shrinkage_k)
        / (pitcher_n + shrinkage_k)
    ).astype("float32")
    out["pitcher_reverse_rate_shrunk"] = (
        (pitcher_reverse * pitcher_n + (1.0 - success_prior) * shrinkage_k)
        / (pitcher_n + shrinkage_k)
    ).astype("float32")
    out["success_minus_reverse"] = (
        pitcher_success - pitcher_reverse
    ).astype("float32")
    out["log1p_pitcher_n"] = np.log1p(pitcher_n).astype("float32")
    out["log1p_batter_n"] = np.log1p(batter_n).astype("float32")

    out["pitcher_team_win_expectancy"] = np.where(
        out["top_bottom"].eq("T"),
        out["home_win_expectancy"],
        out["away_win_expectancy"],
    ).astype("float32")
    out["log1p_li"] = np.log1p(out["li"].clip(lower=0)).astype("float32")
    out["scoring_position"] = (
        out["runner_on_2b"].astype(bool) | out["runner_on_3b"].astype(bool)
    ).astype("int8")
    out["scoring_position_x_li"] = (
        out["scoring_position"] * out["li"]
    ).astype("float32")

    out["count_state"] = (
        out["balls_before"] * 3 + out["strikes_before"]
    ).astype("int8")
    out["is_full_count"] = (
        (out["balls_before"] == 3) & (out["strikes_before"] == 2)
    ).astype("int8")
    out["has_two_strikes"] = (out["strikes_before"] == 2).astype("int8")
    out["has_three_balls"] = (out["balls_before"] == 3).astype("int8")
    out["has_two_outs"] = (out["outs_before"] == 2).astype("int8")
    out["count_hands_state"] = (
        out["count_state"] * 9
        + (out["pitcher_hand"] - 1) * 3
        + (out["batter_hand"] - 1)
    ).astype("int16")
    out["count_matchup_state"] = (
        out["count_state"] * 2 + out["same_hand_matchup"]
    ).astype("int16")
    out["count_out_state"] = (
        out["count_state"] * 3 + out["outs_before"]
    ).astype("int16")
    out["count_hands_out_state"] = (
        out["count_hands_state"] * 3 + out["outs_before"]
    ).astype("int16")
    out["recent_success_blend_135"] = (
        0.2 * out["asof_pitcher_prev1_game_success_rate"]
        + 0.5 * out["asof_pitcher_prev3_game_success_rate"]
        + 0.3 * out["asof_pitcher_prev5_game_success_rate"]
    ).astype("float32")
    out["recent_middle_blend_135"] = (
        0.2 * out["asof_pitcher_prev1_game_middle_rate"]
        + 0.5 * out["asof_pitcher_prev3_game_middle_rate"]
        + 0.3 * out["asof_pitcher_prev5_game_middle_rate"]
    ).astype("float32")
    out["recent_quality_blend_135"] = (
        out["recent_success_blend_135"] - out["recent_middle_blend_135"]
    ).astype("float32")
    out["recent_success_span_15"] = (
        out["asof_pitcher_prev1_game_success_rate"]
        - out["asof_pitcher_prev5_game_success_rate"]
    ).abs().astype("float32")
    out["recent_middle_span_15"] = (
        out["asof_pitcher_prev1_game_middle_rate"]
        - out["asof_pitcher_prev5_game_middle_rate"]
    ).abs().astype("float32")
    out["hand_matchup_state"] = (
        (out["pitcher_hand"] - 1) * 2 + (out["batter_hand"] - 1)
    ).astype("int8")
    pitchmix = {
        "fastball": out["asof_pitcher_fastball_rate"],
        "breaking": out["asof_pitcher_breaking_rate"],
        "offspeed": out["asof_pitcher_offspeed_rate"],
    }
    same_hand = out["same_hand_matchup"].astype("float32")
    pitcher_hand_centered = (out["pitcher_hand"] - 1.5).astype("float32")
    batter_hand_centered = (out["batter_hand"] - 1.5).astype("float32")
    for mix_name, mix_rate in pitchmix.items():
        out[f"same_hand_x_{mix_name}"] = (same_hand * mix_rate).astype("float32")
        out[f"pitcher_hand_x_{mix_name}"] = (
            pitcher_hand_centered * mix_rate
        ).astype("float32")
        out[f"batter_hand_x_{mix_name}"] = (
            batter_hand_centered * mix_rate
        ).astype("float32")
        for matchup in range(4):
            out[f"matchup{matchup}_x_{mix_name}"] = (
                out["hand_matchup_state"].eq(matchup).astype("float32") * mix_rate
            ).astype("float32")
    # Row-local reliability features.  They use only the organizer-provided
    # as-of history in the current row, so evaluation rows remain independent.
    history_bins = [-np.inf, 0, 10, 50, 200, 1000, np.inf]
    out["pitcher_history_bucket"] = pd.cut(
        pitcher_n, bins=history_bins, labels=False, include_lowest=True
    ).fillna(0).astype("int8")
    out["batter_history_bucket"] = pd.cut(
        batter_n, bins=history_bins, labels=False, include_lowest=True
    ).fillna(0).astype("int8")
    pitcher_reliability = (pitcher_n / (pitcher_n + 100.0)).astype("float32")
    batter_reliability = (batter_n / (batter_n + 100.0)).astype("float32")
    out["pitcher_history_reliability_k100"] = pitcher_reliability
    out["batter_history_reliability_k100"] = batter_reliability
    out["pitcher_success_x_reliability"] = (
        pitcher_success * pitcher_reliability
    ).astype("float32")
    out["batter_success_x_reliability"] = (
        batter_rate * batter_reliability
    ).astype("float32")
    out["pitcher_reverse_x_reliability"] = (
        pitcher_reverse * pitcher_reliability
    ).astype("float32")
    out["pitcher_middle_x_reliability"] = (
        _safe_rate(out["asof_pitcher_middle_rate"], 0.0) * pitcher_reliability
    ).astype("float32")
    for metric in ("ball", "strike", "fastball", "breaking", "offspeed"):
        out[f"pitcher_{metric}_x_reliability"] = (
            _safe_rate(out[f"asof_pitcher_{metric}_rate"], 0.0)
            * pitcher_reliability
        ).astype("float32")
    pitcher_middle = _safe_rate(out["asof_pitcher_middle_rate"], 0.0)
    for reliability_k in (50, 200):
        pitcher_rel = (pitcher_n / (pitcher_n + reliability_k)).astype("float32")
        batter_rel = (batter_n / (batter_n + reliability_k)).astype("float32")
        suffix = f"_k{reliability_k}"
        out[f"pitcher_history_reliability{suffix}"] = pitcher_rel
        out[f"batter_history_reliability{suffix}"] = batter_rel
        out[f"pitcher_success_x_reliability{suffix}"] = (
            pitcher_success * pitcher_rel
        ).astype("float32")
        out[f"batter_success_x_reliability{suffix}"] = (
            batter_rate * batter_rel
        ).astype("float32")
        out[f"pitcher_reverse_x_reliability{suffix}"] = (
            pitcher_reverse * pitcher_rel
        ).astype("float32")
        out[f"pitcher_middle_x_reliability{suffix}"] = (
            pitcher_middle * pitcher_rel
        ).astype("float32")
    out["inning_phase_state"] = np.select(
        [out["inning"].le(3), out["inning"].le(6), out["inning"].le(9)],
        [0, 1, 2],
        default=3,
    ).astype("int8")
    for phase, phase_name in enumerate(("early", "middle", "late", "extra")):
        out[f"{phase_name}_inning_x_li"] = (
            out["inning_phase_state"].eq(phase).astype("float32") * out["li"]
        ).astype("float32")
    late = out["inning"].ge(7).astype("float32")
    out["late_inning_x_pitcher_success"] = (
        late * out["asof_pitcher_success_rate"]
    ).astype("float32")
    out["late_inning_x_pitcher_reverse"] = (
        late * out["asof_pitcher_reverse_rate"]
    ).astype("float32")
    out["late_inning_x_pitcher_middle"] = (
        late * out["asof_pitcher_middle_rate"]
    ).astype("float32")
    pressure_masks = {
        "two_strike": out["strikes_before"].eq(2).astype("float32"),
        "three_ball": out["balls_before"].eq(3).astype("float32"),
        "full_count": (
            out["balls_before"].eq(3) & out["strikes_before"].eq(2)
        ).astype("float32"),
    }
    for pressure_name, pressure_mask in pressure_masks.items():
        for metric in ("success", "reverse", "middle"):
            out[f"{pressure_name}_x_pitcher_{metric}"] = (
                pressure_mask * out[f"asof_pitcher_{metric}_rate"]
            ).astype("float32")
    # Everything below this point in the historical implementation derives
    # one evaluation row from neighboring evaluation rows. It is intentionally
    # unreachable in the compliant path and retained only so old quarantined
    # experiment records remain interpretable.
    return out

    row_number = pd.to_numeric(
        out["row_id"].astype(str).str.extract(r"(\d+)$", expand=False),
        errors="coerce",
    ).fillna(0)
    season_start = row_number.groupby(out["season"]).transform("min")
    is_test_id = out["row_id"].astype(str).str.startswith("TEST_")
    season_pitch_index = pd.Series(
        np.where(is_test_id, row_number, row_number - season_start),
        index=out.index,
    ).clip(lower=0)
    out["season_pitch_index"] = season_pitch_index.astype("int32")
    out["season_progress_proxy"] = (
        season_pitch_index / 250_000.0
    ).astype("float32")
    out["season_phase_20"] = (
        season_pitch_index // 12_500
    ).clip(upper=31).astype("int8")

    # The provided as-of count/rate pair describes history immediately before
    # each row.  Consecutive differences therefore recover only already-known
    # outcomes (most commonly the entity's previous pitch), never the current
    # row's target.
    ordered_index = row_number.sort_values(kind="stable").index
    for entity in ("pitcher", "batter"):
        entity_id = out.loc[ordered_index, f"{entity}_id"]
        entity_n = pd.to_numeric(
            out.loc[ordered_index, f"asof_{entity}_n"], errors="coerce"
        )
        entity_rate = pd.to_numeric(
            out.loc[ordered_index, f"asof_{entity}_success_rate"],
            errors="coerce",
        )
        cumulative_success = entity_n * entity_rate
        delta_n = entity_n.groupby(entity_id, sort=False).diff()
        delta_success = cumulative_success.groupby(
            entity_id, sort=False
        ).diff()
        previous_success = (delta_success / delta_n).where(delta_n.gt(0))
        previous_success = previous_success.clip(0.0, 1.0)
        out.loc[
            ordered_index, f"{entity}_previous_pitch_success"
        ] = previous_success.to_numpy(dtype="float32")
        lag_values: dict[int, pd.Series] = {1: previous_success}
        lag_windows = (2, 3, 5) if entity == "pitcher" else (2, 3)
        for lag in lag_windows:
            lagged = previous_success.groupby(entity_id, sort=False).shift(
                lag - 1
            )
            lag_values[lag] = lagged
            out.loc[
                ordered_index, f"{entity}_lag{lag}_pitch_success"
            ] = lagged.to_numpy(dtype="float32")
        last3_available = (
            lag_values[1].notna()
            & lag_values[2].notna()
            & lag_values[3].notna()
        )
        last3_pattern = (
            (lag_values[1].ge(0.5).astype("int8") * 4)
            + (lag_values[2].ge(0.5).astype("int8") * 2)
            + lag_values[3].ge(0.5).astype("int8")
        ).where(last3_available)
        out.loc[
            ordered_index, f"{entity}_last3_success_pattern"
        ] = last3_pattern.to_numpy(dtype="float32")
        ewm_alphas = (0.05, 0.10) if entity == "pitcher" else (0.10, 0.20)
        for alpha in ewm_alphas:
            ewm = previous_success.groupby(entity_id, sort=False).transform(
                lambda values: values.ewm(
                    alpha=alpha, adjust=False, min_periods=1
                ).mean()
            )
            alpha_label = f"{int(round(alpha * 100)):02d}"
            out.loc[
                ordered_index, f"{entity}_success_ewm{alpha_label}"
            ] = ewm.to_numpy(dtype="float32")
        windows = (3, 5, 10, 20, 30, 50) if entity == "pitcher" else (
            2,
            3,
            5,
            8,
            10,
        )
        for window in windows:
            recent = previous_success.groupby(entity_id, sort=False).transform(
                lambda values: values.rolling(window, min_periods=1).mean()
            )
            out.loc[
                ordered_index, f"{entity}_recent{window}_pitch_success"
            ] = recent.to_numpy(dtype="float32")

    pitcher_id = out.loc[ordered_index, "pitcher_id"]
    pitcher_n = pd.to_numeric(
        out.loc[ordered_index, "asof_pitcher_n"], errors="coerce"
    )
    pitcher_reverse_rate = pd.to_numeric(
        out.loc[ordered_index, "asof_pitcher_reverse_rate"],
        errors="coerce",
    )
    reverse_count = pitcher_n * pitcher_reverse_rate
    reverse_delta_n = pitcher_n.groupby(pitcher_id, sort=False).diff()
    previous_reverse = (
        reverse_count.groupby(pitcher_id, sort=False).diff()
        / reverse_delta_n
    ).where(reverse_delta_n.gt(0)).clip(0.0, 1.0)
    out.loc[
        ordered_index, "pitcher_previous_pitch_reverse"
    ] = previous_reverse.to_numpy(dtype="float32")
    for alpha in (0.05, 0.10):
        reverse_ewm = previous_reverse.groupby(
            pitcher_id, sort=False
        ).transform(
            lambda values: values.ewm(
                alpha=alpha, adjust=False, min_periods=1
            ).mean()
        )
        alpha_label = f"{int(round(alpha * 100)):02d}"
        out.loc[
            ordered_index, f"pitcher_reverse_ewm{alpha_label}"
        ] = reverse_ewm.to_numpy(dtype="float32")
    for window in (3, 5, 10, 20, 50):
        recent_reverse = previous_reverse.groupby(
            pitcher_id, sort=False
        ).transform(lambda values: values.rolling(window, min_periods=1).mean())
        out.loc[
            ordered_index, f"pitcher_recent{window}_pitch_reverse"
        ] = recent_reverse.to_numpy(dtype="float32")

    for entity, metric in (
        ("pitcher", "middle"),
        ("pitcher", "ball"),
        ("batter", "middle"),
    ):
        entity_id = out.loc[ordered_index, f"{entity}_id"]
        entity_n = pd.to_numeric(
            out.loc[ordered_index, f"asof_{entity}_n"], errors="coerce"
        )
        metric_rate = pd.to_numeric(
            out.loc[ordered_index, f"asof_{entity}_{metric}_rate"],
            errors="coerce",
        )
        metric_count = entity_n * metric_rate
        metric_delta_n = entity_n.groupby(entity_id, sort=False).diff()
        previous_metric = (
            metric_count.groupby(entity_id, sort=False).diff()
            / metric_delta_n
        ).where(metric_delta_n.gt(0)).clip(0.0, 1.0)
        out.loc[
            ordered_index, f"{entity}_previous_pitch_{metric}"
        ] = previous_metric.to_numpy(dtype="float32")
        for window in (3, 5, 10):
            recent_metric = previous_metric.groupby(
                entity_id, sort=False
            ).transform(
                lambda values: values.rolling(window, min_periods=1).mean()
            )
            out.loc[
                ordered_index, f"{entity}_recent{window}_pitch_{metric}"
            ] = recent_metric.to_numpy(dtype="float32")

    # Consolidate the many engineered columns before adding sequence-level
    # aggregates. This keeps the large training frame from becoming fragmented.
    out = out.copy()
    ordered_row_number = row_number.loc[ordered_index]
    pitcher_id = out.loc[ordered_index, "pitcher_id"]
    batter_id = out.loc[ordered_index, "batter_id"]
    pitcher_gap = ordered_row_number - ordered_row_number.groupby(
        pitcher_id, sort=False
    ).shift(1)
    batter_gap = ordered_row_number - ordered_row_number.groupby(
        batter_id, sort=False
    ).shift(1)
    pitcher_immediate = pitcher_gap.eq(1)
    batter_immediate = batter_gap.eq(1)
    same_matchup = pitcher_immediate & batter_immediate
    out.loc[ordered_index, "pitcher_row_gap"] = np.log1p(
        pitcher_gap.clip(lower=0)
    ).to_numpy(dtype="float32")
    out.loc[ordered_index, "batter_row_gap"] = np.log1p(
        batter_gap.clip(lower=0)
    ).to_numpy(dtype="float32")
    out.loc[ordered_index, "pitcher_is_immediate"] = pitcher_immediate.to_numpy(
        dtype="int8"
    )
    out.loc[ordered_index, "batter_is_immediate"] = batter_immediate.to_numpy(
        dtype="int8"
    )
    out.loc[ordered_index, "same_matchup_previous"] = same_matchup.to_numpy(
        dtype="int8"
    )
    global_success = out.loc[
        ordered_index, "pitcher_previous_pitch_success"
    ].where(pitcher_immediate)
    global_reverse = out.loc[
        ordered_index, "pitcher_previous_pitch_reverse"
    ].where(pitcher_immediate)
    out.loc[ordered_index, "previous_global_success"] = global_success.to_numpy(
        dtype="float32"
    )
    out.loc[ordered_index, "previous_global_reverse"] = global_reverse.to_numpy(
        dtype="float32"
    )
    for window in (
        5, 10, 20, 50, 75, 100, 125, 150, 175, 200, 225, 250, 300, 400
    ):
        global_recent = global_success.rolling(
            window, min_periods=1
        ).mean()
        out.loc[
            ordered_index, f"global_recent{window}_success"
        ] = global_recent.to_numpy(dtype="float32")
    for window in (50, 100, 150, 200, 300):
        global_recent_reverse = global_reverse.rolling(
            window, min_periods=1
        ).mean()
        out.loc[
            ordered_index, f"global_recent{window}_reverse"
        ] = global_recent_reverse.to_numpy(dtype="float32")
    out = out.copy()
    global_middle = out.loc[
        ordered_index, "pitcher_previous_pitch_middle"
    ].where(pitcher_immediate)
    ordered_season = out.loc[ordered_index, "season"]
    ordered_inning = out.loc[ordered_index, "inning"]
    new_game = ordered_season.ne(ordered_season.shift()) | ordered_inning.lt(
        ordered_inning.shift()
    )
    game_group = new_game.cumsum()
    sequence_groups = {
        "game": game_group,
        "pitcher_team": out.loc[ordered_index, "pitcher_team_id"],
        "batter_team": out.loc[ordered_index, "batter_team_id"],
    }
    for prefix, group in sequence_groups.items():
        recent_success = global_success.groupby(group, sort=False).transform(
            lambda values: values.rolling(200, min_periods=1).mean()
        )
        out.loc[
            ordered_index, f"{prefix}_recent200_success"
        ] = recent_success.to_numpy(dtype="float32")
        middle_windows = (100, 200) if prefix == "game" else (200,)
        for window in middle_windows:
            recent_middle = global_middle.groupby(group, sort=False).transform(
                lambda values: values.rolling(window, min_periods=1).mean()
            )
            out.loc[
                ordered_index, f"{prefix}_recent{window}_middle"
            ] = recent_middle.to_numpy(dtype="float32")
    plate_group = (~same_matchup).cumsum()
    plate_pitch_index = plate_group.groupby(plate_group, sort=False).cumcount()
    out.loc[
        ordered_index, "plate_appearance_pitch_index"
    ] = plate_pitch_index.to_numpy(dtype="int16")
    plate_success = global_success.where(same_matchup)
    for window in (2, 3):
        recent_plate_success = plate_success.groupby(
            plate_group, sort=False
        ).transform(lambda values: values.rolling(window, min_periods=1).mean())
        out.loc[
            ordered_index, f"plate_appearance_recent{window}_success"
        ] = recent_plate_success.to_numpy(dtype="float32")
    return out


def engineer_temporal_target_features(
    frame: pd.DataFrame,
    targets: pd.Series,
    *,
    success_prior: float,
    shrinkage_k: float = 100.0,
) -> pd.DataFrame:
    """Add prior-season target aggregates without using current-season labels."""
    out = frame.copy()
    target = pd.Series(targets.to_numpy(), index=out.index, dtype="float64")
    seasons = pd.to_numeric(out["season"], errors="raise")
    feature_values = {
        name: pd.Series(index=out.index, dtype="float32")
        for name in TEMPORAL_TARGET_FEATURES
    }
    entity_specs = {
        "pitcher": "pitcher_id",
        "batter": "batter_id",
        "pitcher_team": "pitcher_team_id",
        "batter_team": "batter_team_id",
    }

    completed_seasons: list[int] = []
    season_rates: list[float] = []
    for season in sorted(int(value) for value in seasons.unique()):
        current_mask = seasons.eq(season)
        previous = max(completed_seasons) if completed_seasons else None
        if previous is None:
            previous_rate = success_prior
            previous_mask = pd.Series(False, index=out.index)
        else:
            previous_mask = seasons.eq(previous)
            previous_rate = float(target.loc[previous_mask].mean())
        feature_values["previous_season_target_rate"].loc[current_mask] = (
            previous_rate
        )

        if len(completed_seasons) >= 2:
            slope, intercept = np.polyfit(completed_seasons, season_rates, 1)
            trend_prior = float(np.clip(intercept + slope * season, 0.05, 0.95))
        else:
            trend_prior = previous_rate
        feature_values["season_trend_prior"].loc[current_mask] = trend_prior

        for prefix, key in entity_specs.items():
            if previous is None:
                smoothed = pd.Series(dtype="float64")
                counts = pd.Series(dtype="float64")
            else:
                stats = pd.DataFrame(
                    {"key": out.loc[previous_mask, key], "target": target.loc[previous_mask]}
                ).groupby("key", observed=True)["target"].agg(["sum", "count"])
                counts = stats["count"]
                smoothed = (
                    stats["sum"] + shrinkage_k * previous_rate
                ) / (counts + shrinkage_k)
            mapped_rate = out.loc[current_mask, key].map(smoothed).fillna(previous_rate)
            feature_values[f"{prefix}_prev_season_rate"].loc[current_mask] = (
                mapped_rate.to_numpy(dtype="float32")
            )
            if prefix in {"pitcher", "batter"}:
                mapped_count = out.loc[current_mask, key].map(counts).fillna(0.0)
                feature_values[f"{prefix}_prev_season_log_n"].loc[current_mask] = (
                    np.log1p(mapped_count).to_numpy(dtype="float32")
                )
                feature_values[f"{prefix}_prev_season_delta"].loc[current_mask] = (
                    (mapped_rate - previous_rate).to_numpy(dtype="float32")
                )

        completed_seasons.append(season)
        season_rates.append(float(target.loc[current_mask].mean()))

    for name, values in feature_values.items():
        out[name] = values.fillna(success_prior).astype("float32")
    return out


def engineer_official_train_target_features(
    frame: pd.DataFrame,
    targets: pd.Series,
    *,
    reference_mask: pd.Series,
    apply_mask: pd.Series,
    success_prior: float,
    requested: Collection[str],
) -> pd.DataFrame:
    """Add LOO/full target effects using official training rows only.

    Training rows receive leave-one-out values. Evaluation rows receive a map
    fitted only on ``reference_mask``. No evaluation target or evaluation-row
    aggregate participates in any feature value.
    """
    selected = frozenset(requested).intersection(REFERENCE_TARGET_FEATURES)
    if not selected:
        return frame
    out = frame.copy()
    target = pd.Series(targets.to_numpy(), index=out.index, dtype="float64")
    ref = pd.Series(reference_mask.to_numpy(), index=out.index, dtype="bool")
    apply = pd.Series(apply_mask.to_numpy(), index=out.index, dtype="bool")
    specs = {
        "pitcher_target_effect_k50": ("pitcher_id", 50.0),
        "pitcher_target_effect_k200": ("pitcher_id", 200.0),
        "batter_target_effect_k50": ("batter_id", 50.0),
        "batter_target_effect_k200": ("batter_id", 200.0),
        "pitcher_team_target_effect_k500": ("pitcher_team_id", 500.0),
        "batter_team_target_effect_k500": ("batter_team_id", 500.0),
    }
    for name in sorted(selected):
        key, shrinkage = specs[name]
        stats = pd.DataFrame(
            {"key": out.loc[ref, key], "target": target.loc[ref]}
        ).groupby("key", observed=True)["target"].agg(["sum", "count"])
        mapped_sum = out[key].map(stats["sum"])
        mapped_count = out[key].map(stats["count"])
        values = pd.Series(0.0, index=out.index, dtype="float64")
        loo_count = mapped_count.loc[ref] - 1.0
        loo_sum = mapped_sum.loc[ref] - target.loc[ref]
        values.loc[ref] = (
            loo_sum - loo_count * success_prior
        ) / (loo_count + shrinkage)
        values.loc[apply] = (
            mapped_sum.loc[apply] - mapped_count.loc[apply] * success_prior
        ) / (mapped_count.loc[apply] + shrinkage)
        out[name] = values.fillna(0.0).astype("float32")
    return out


def engineer_official_train_state_features(
    frame: pd.DataFrame,
    targets: pd.Series | None = None,
    *,
    reference_mask: pd.Series,
    apply_mask: pd.Series,
    requested: Collection[str],
    shrinkage_k: float = 20.0,
) -> pd.DataFrame:
    """Create current-season state from official-train snapshots + one row."""
    selected = frozenset(requested).intersection(REFERENCE_STATE_FEATURES)
    if not selected:
        return frame
    out = frame.copy()
    ref = pd.Series(reference_mask.to_numpy(), index=out.index, dtype="bool")
    apply = pd.Series(apply_mask.to_numpy(), index=out.index, dtype="bool")
    seasons = pd.to_numeric(out["season"], errors="raise")
    target = None
    if targets is not None:
        target = pd.Series(targets.to_numpy(), index=out.index, dtype="float64")

    for entity, metrics in {
        "pitcher": (
            "success", "reverse", "middle", "ball", "strike",
            "fastball", "breaking", "offspeed",
        ),
        "batter": ("success", "middle"),
    }.items():
        entity_selected = {
            name for name in selected if name.startswith(f"{entity}_season_")
        }
        if not entity_selected:
            continue
        key = f"{entity}_id"
        count_column = f"asof_{entity}_n"
        baseline_count = pd.Series(0.0, index=out.index)
        baseline_counts = {
            metric: pd.Series(0.0, index=out.index) for metric in metrics
        }
        baseline_count_exact = pd.Series(0.0, index=out.index)
        baseline_success_exact = pd.Series(0.0, index=out.index)

        def assign_snapshot(mask: pd.Series, past: pd.Series) -> None:
            if not mask.any() or not past.any():
                return
            last_frame = out.loc[past].copy()
            if target is not None:
                last_frame["__official_target"] = target.loc[past].to_numpy()
            last = (
                last_frame
                .sort_values(ID_COL, kind="stable")
                .groupby(key, observed=True, sort=False)
                .tail(1)
                .set_index(key)
            )
            baseline_count.loc[mask] = (
                out.loc[mask, key].map(last[count_column]).fillna(0.0).to_numpy()
            )
            if target is not None:
                completed_n = pd.to_numeric(last[count_column], errors="coerce") + 1.0
                completed_success = (
                    pd.to_numeric(last[count_column], errors="coerce")
                    * pd.to_numeric(last[f"asof_{entity}_success_rate"], errors="coerce")
                    + pd.to_numeric(last["__official_target"], errors="coerce")
                )
                baseline_count_exact.loc[mask] = (
                    out.loc[mask, key].map(completed_n).fillna(0.0).to_numpy()
                )
                baseline_success_exact.loc[mask] = (
                    out.loc[mask, key].map(completed_success).fillna(0.0).to_numpy()
                )
            for metric in metrics:
                rate_column = f"asof_{entity}_{metric}_rate"
                stored_count = last[count_column] * last[rate_column]
                baseline_counts[metric].loc[mask] = (
                    out.loc[mask, key].map(stored_count).fillna(0.0).to_numpy()
                )

        for season in sorted(int(value) for value in seasons.loc[ref].unique()):
            current = ref & seasons.eq(season)
            assign_snapshot(current, ref & seasons.lt(season))
        assign_snapshot(apply, ref)

        current_n = pd.to_numeric(out[count_column], errors="coerce").fillna(0.0)
        season_n = (current_n - baseline_count).clip(lower=0.0)
        exact_names = {
            f"{entity}_season_n_exact",
            f"{entity}_season_success_rate_exact_k20",
            f"{entity}_season_success_rate_exact_k50",
        }
        if selected.intersection(exact_names):
            if target is None:
                raise ValueError("exact season snapshot에는 공식 학습 target이 필요합니다.")
            exact_season_n = (current_n - baseline_count_exact).clip(lower=0.0)
            exact_success_count = (
                current_n
                * pd.to_numeric(
                    out[f"asof_{entity}_success_rate"], errors="coerce"
                )
                - baseline_success_exact
            ).clip(lower=0.0, upper=exact_season_n)
            exact_prior = float(
                pd.to_numeric(
                    out.loc[ref, f"asof_{entity}_success_rate"], errors="coerce"
                ).median()
            )
            if f"{entity}_season_n_exact" in selected:
                out[f"{entity}_season_n_exact"] = np.log1p(exact_season_n).astype(
                    "float32"
                )
            for exact_k in (20, 50):
                exact_name = f"{entity}_season_success_rate_exact_k{exact_k}"
                if exact_name in selected:
                    out[exact_name] = (
                        (exact_success_count.fillna(0.0) + exact_k * exact_prior)
                        / (exact_season_n + exact_k)
                    ).astype("float32")
        n_name = f"{entity}_season_n"
        if n_name in selected:
            out[n_name] = np.log1p(season_n).astype("float32")
        for metric in metrics:
            candidates = [(f"{entity}_season_{metric}_rate_k20", shrinkage_k)]
            if metric == "success" and entity in {"pitcher", "batter"}:
                candidates.extend(
                    (f"{entity}_season_success_rate_k{k_value}", float(k_value))
                    for k_value in (5, 10, 50, 100)
                )
            if entity == "pitcher" and metric == "ball":
                candidates.append(("pitcher_season_ball_rate_k500", 500.0))
            if entity == "pitcher" and metric == "strike":
                candidates.append(("pitcher_season_strike_rate_k200", 200.0))
            if entity == "batter" and metric == "middle":
                candidates.append(("batter_season_middle_rate_k200", 200.0))
            if not any(name in selected for name, _ in candidates):
                continue
            rate_column = f"asof_{entity}_{metric}_rate"
            rate = pd.to_numeric(out[rate_column], errors="coerce")
            current_count = current_n * rate
            delta_count = (current_count - baseline_counts[metric]).clip(
                lower=0.0, upper=season_n
            )
            count_name = f"{entity}_season_{metric}_count_log"
            if count_name in selected:
                out[count_name] = np.log1p(delta_count.fillna(0.0)).astype("float32")
            failure_name = f"{entity}_season_failure_count_log"
            if metric == "success" and failure_name in selected:
                out[failure_name] = np.log1p(
                    (season_n - delta_count.fillna(0.0)).clip(lower=0.0)
                ).astype("float32")
            prior = float(
                pd.to_numeric(out.loc[ref, rate_column], errors="coerce").median()
            )
            for name, k_value in candidates:
                if name in selected:
                    out[name] = (
                        (delta_count.fillna(0.0) + k_value * prior)
                        / (season_n + k_value)
                    ).astype("float32")
        for metric in metrics:
            delta_name = f"{entity}_season_{metric}_delta_career"
            season_name = f"{entity}_season_{metric}_rate_k20"
            if delta_name in selected:
                out[delta_name] = (
                    out[season_name] - out[f"asof_{entity}_{metric}_rate"]
                ).astype("float32")

    if "pitcher_prev1_minus_prev3" in selected:
        out["pitcher_prev1_minus_prev3"] = (
            out["asof_pitcher_prev1_game_success_rate"]
            - out["asof_pitcher_prev3_game_success_rate"]
        ).astype("float32")
    if "pitcher_prev3_minus_prev5" in selected:
        out["pitcher_prev3_minus_prev5"] = (
            out["asof_pitcher_prev3_game_success_rate"]
            - out["asof_pitcher_prev5_game_success_rate"]
        ).astype("float32")
    if "pitcher_prev3_minus_season_success" in selected:
        out["pitcher_prev3_minus_season_success"] = (
            out["asof_pitcher_prev3_game_success_rate"]
            - out["pitcher_season_success_rate_k20"]
        ).astype("float32")
    return out


def build_official_state_reference(
    frame: pd.DataFrame,
    *,
    requested: Collection[str],
) -> dict[str, Any]:
    """Freeze official-train snapshots needed for independent test-row features."""
    selected = frozenset(requested).intersection(REFERENCE_STATE_FEATURES)
    reference: dict[str, Any] = {"selected": sorted(selected), "entities": {}}
    for entity, metrics in {
        "pitcher": (
            "success", "reverse", "middle", "ball", "strike",
            "fastball", "breaking", "offspeed",
        ),
        "batter": ("success", "middle"),
    }.items():
        if not any(name.startswith(f"{entity}_season_") for name in selected):
            continue
        key = f"{entity}_id"
        count_column = f"asof_{entity}_n"
        last = (
            frame.sort_values(ID_COL, kind="stable")
            .groupby(key, observed=True, sort=False)
            .tail(1)
            .set_index(key)
        )
        entity_reference: dict[str, Any] = {
            "baseline_count": pd.to_numeric(
                last[count_column], errors="coerce"
            ).fillna(0.0),
            "baseline_counts": {},
            "priors": {},
        }
        for metric in metrics:
            rate_column = f"asof_{entity}_{metric}_rate"
            rate = pd.to_numeric(frame[rate_column], errors="coerce")
            last_rate = pd.to_numeric(last[rate_column], errors="coerce")
            entity_reference["baseline_counts"][metric] = (
                entity_reference["baseline_count"] * last_rate
            ).fillna(0.0)
            entity_reference["priors"][metric] = float(rate.median())
        reference["entities"][entity] = entity_reference
    return reference


def apply_official_state_reference(
    frame: pd.DataFrame,
    reference: dict[str, Any],
    *,
    requested: Collection[str],
    shrinkage_k: float = 20.0,
) -> pd.DataFrame:
    """Apply frozen official-train state to rows without aggregating those rows."""
    selected = frozenset(requested).intersection(REFERENCE_STATE_FEATURES)
    out = frame.copy()
    for entity, entity_reference in reference.get("entities", {}).items():
        metrics = tuple(entity_reference["baseline_counts"])
        key = f"{entity}_id"
        count_column = f"asof_{entity}_n"
        baseline_count = out[key].map(entity_reference["baseline_count"]).fillna(0.0)
        current_n = pd.to_numeric(out[count_column], errors="coerce").fillna(0.0)
        season_n = (current_n - baseline_count).clip(lower=0.0)
        n_name = f"{entity}_season_n"
        if n_name in selected:
            out[n_name] = np.log1p(season_n).astype("float32")
        for metric in metrics:
            candidates = [(f"{entity}_season_{metric}_rate_k20", shrinkage_k)]
            if metric == "success" and entity in {"pitcher", "batter"}:
                candidates.extend(
                    (f"{entity}_season_success_rate_k{k_value}", float(k_value))
                    for k_value in (5, 10, 50, 100)
                )
            if entity == "pitcher" and metric == "ball":
                candidates.append(("pitcher_season_ball_rate_k500", 500.0))
            if entity == "pitcher" and metric == "strike":
                candidates.append(("pitcher_season_strike_rate_k200", 200.0))
            if entity == "batter" and metric == "middle":
                candidates.append(("batter_season_middle_rate_k200", 200.0))
            if not any(name in selected for name, _ in candidates):
                continue
            rate_column = f"asof_{entity}_{metric}_rate"
            current_count = current_n * pd.to_numeric(
                out[rate_column], errors="coerce"
            )
            baseline_metric = out[key].map(
                entity_reference["baseline_counts"][metric]
            ).fillna(0.0)
            delta_count = (current_count - baseline_metric).clip(
                lower=0.0, upper=season_n
            )
            count_name = f"{entity}_season_{metric}_count_log"
            if count_name in selected:
                out[count_name] = np.log1p(delta_count.fillna(0.0)).astype("float32")
            failure_name = f"{entity}_season_failure_count_log"
            if metric == "success" and failure_name in selected:
                out[failure_name] = np.log1p(
                    (season_n - delta_count.fillna(0.0)).clip(lower=0.0)
                ).astype("float32")
            prior = float(entity_reference["priors"][metric])
            for name, k_value in candidates:
                if name in selected:
                    out[name] = (
                        (delta_count.fillna(0.0) + k_value * prior)
                        / (season_n + k_value)
                    ).astype("float32")
        for metric in metrics:
            delta_name = f"{entity}_season_{metric}_delta_career"
            season_name = f"{entity}_season_{metric}_rate_k20"
            if delta_name in selected:
                out[delta_name] = (
                    out[season_name] - out[f"asof_{entity}_{metric}_rate"]
                ).astype("float32")
    return out


def engineer_official_train_progress_features(
    frame: pd.DataFrame,
    *,
    reference_mask: pd.Series,
    apply_mask: pd.Series,
    requested: Collection[str],
) -> pd.DataFrame:
    """Create row-ID progress without inspecting any other evaluation row."""
    selected = frozenset(requested).intersection(REFERENCE_PROGRESS_FEATURES)
    if not selected:
        return frame
    out = frame.copy()
    ref = pd.Series(reference_mask.to_numpy(), index=out.index, dtype="bool")
    apply = pd.Series(apply_mask.to_numpy(), index=out.index, dtype="bool")
    seasons = pd.to_numeric(out["season"], errors="raise")
    row_text = out[ID_COL].astype(str)
    row_number = pd.to_numeric(
        row_text.str.extract(r"(\d+)$", expand=False), errors="raise"
    ).astype("int64")
    progress = pd.Series(0, index=out.index, dtype="int64")

    reference_starts = row_number.loc[ref].groupby(seasons.loc[ref]).min()
    progress.loc[ref] = (
        row_number.loc[ref] - seasons.loc[ref].map(reference_starts)
    ).clip(lower=0)

    reference_prefix = row_text.loc[ref].str.replace(r"\d+$", "", regex=True)
    max_by_prefix = row_number.loc[ref].groupby(reference_prefix).max()
    apply_prefix = row_text.loc[apply].str.replace(r"\d+$", "", regex=True)
    apply_start = apply_prefix.map(max_by_prefix.add(1.0))
    # Competition TEST identifiers restart at zero. Unknown prefixes likewise
    # use only their own suffix and never an evaluation-set minimum.
    apply_start = apply_start.fillna(0.0).astype("int64")
    progress.loc[apply] = (row_number.loc[apply] - apply_start).clip(lower=0)

    if "season_pitch_index_safe" in selected:
        out["season_pitch_index_safe"] = progress.astype("int32")
    if "season_progress_safe" in selected:
        out["season_progress_safe"] = (progress / 250_000.0).astype("float32")
    if "season_phase_20_safe" in selected:
        out["season_phase_20_safe"] = (progress // 12_500).clip(
            upper=31
        ).astype("int8")
    return out


def engineer_official_train_context_features(
    frame: pd.DataFrame,
    targets: pd.Series,
    *,
    reference_mask: pd.Series,
    apply_mask: pd.Series,
    requested: Collection[str],
) -> pd.DataFrame:
    """Add stable context effects fitted exclusively on official train rows."""
    selected = frozenset(requested).intersection(REFERENCE_CONTEXT_FEATURES)
    if not selected:
        return frame
    out = frame.copy()
    ref = pd.Series(reference_mask.to_numpy(), index=out.index, dtype="bool")
    apply = pd.Series(apply_mask.to_numpy(), index=out.index, dtype="bool")
    target = pd.Series(targets.to_numpy(), index=out.index, dtype="float64")
    season = pd.to_numeric(out["season"], errors="raise")
    season_mean = target.loc[ref].groupby(season.loc[ref]).transform("mean")
    centered = target.loc[ref] - season_mean
    specs = {
        "count_hands_target_effect": (
            ["balls_before", "strikes_before", "pitcher_hand", "batter_hand"],
            500.0,
        ),
        "count_out_base_target_effect": (
            ["balls_before", "strikes_before", "outs_before", "base_state"],
            500.0,
        ),
        "inning_game_target_effect": (
            ["inning", "top_bottom", "game_type"],
            500.0,
        ),
        "pressure_state_target_effect": (
            [
                "inning", "balls_before", "strikes_before", "outs_before",
                "num_runners_on",
            ],
            1000.0,
        ),
    }
    for name in sorted(selected):
        columns, shrinkage = specs[name]
        def build_stats(mask: pd.Series) -> pd.DataFrame:
            stats_frame = out.loc[mask, columns].copy()
            stats_frame["__centered"] = centered.loc[mask].to_numpy()
            return stats_frame.groupby(
                columns, dropna=False, observed=True
            )["__centered"].agg(["sum", "count"])

        def map_stat(
            mask: pd.Series, stats: pd.DataFrame, column: str
        ) -> pd.Series:
            keys = pd.MultiIndex.from_frame(out.loc[mask, columns])
            return pd.Series(
                stats[column].reindex(keys).to_numpy(),
                index=out.index[mask],
                dtype="float64",
            )

        values = pd.Series(0.0, index=out.index, dtype="float64")
        # Entire-season OOF: a training row's feature is built with other
        # official seasons, so its own target cannot leave a numeric fingerprint.
        for current_season in sorted(int(value) for value in season.loc[ref].unique()):
            current = ref & season.eq(current_season)
            other_seasons = ref & season.ne(current_season)
            season_stats = build_stats(other_seasons)
            season_sum = map_stat(current, season_stats, "sum")
            season_count = map_stat(current, season_stats, "count")
            values.loc[current] = season_sum / (season_count + shrinkage)

        full_stats = build_stats(ref)
        apply_sum = map_stat(apply, full_stats, "sum")
        apply_count = map_stat(apply, full_stats, "count")
        values.loc[apply] = apply_sum / (apply_count + shrinkage)
        out[name] = values.fillna(0.0).astype("float32")
    return out


def engineer_trackman_context_features(
    frame: pd.DataFrame,
    trackman: pd.DataFrame,
    *,
    reference_mask: pd.Series,
    apply_mask: pd.Series,
    requested: Collection[str],
) -> pd.DataFrame:
    """Map official Trackman context aggregates without joining eval rows."""
    selected = frozenset(requested).intersection(TRACKMAN_CONTEXT_FEATURES)
    if not selected:
        return frame
    out = frame.copy()
    ref = pd.Series(reference_mask.to_numpy(), index=out.index, dtype="bool")
    apply = pd.Series(apply_mask.to_numpy(), index=out.index, dtype="bool")
    season = pd.to_numeric(out["season"], errors="raise")
    history = trackman.copy()
    history["pitcher_hand"] = history["pitcher_hand"].map(
        {"Right": 1, "Left": 2}
    )
    history["batter_hand"] = history["batter_hand"].map(
        {"Right": 1, "Left": 2}
    )
    history["abs_horz_break"] = history["horz_break"].abs()
    for group in ("fastball", "breaking", "offspeed"):
        history[f"{group}_share"] = history["pitch_type_group"].eq(group).astype(
            "float32"
        )
    keys = [
        "pitcher_hand", "batter_hand", "balls_before", "strikes_before"
    ]
    source = {
        "track_context_rel_speed": "rel_speed",
        "track_context_spin_rate": "spin_rate",
        "track_context_induced_vert_break": "induced_vert_break",
        "track_context_abs_horz_break": "abs_horz_break",
        "track_context_extension": "extension",
        "track_context_zone_speed": "zone_speed",
        "track_context_fastball_share": "fastball_share",
        "track_context_breaking_share": "breaking_share",
        "track_context_offspeed_share": "offspeed_share",
    }

    def aggregate(mask: pd.Series) -> pd.DataFrame:
        return history.loc[mask].groupby(
            keys, dropna=False, observed=True
        )[list(source.values())].mean()

    def map_values(mask: pd.Series, stats: pd.DataFrame, column: str) -> np.ndarray:
        index = pd.MultiIndex.from_frame(out.loc[mask, keys])
        return stats[column].reindex(index).to_numpy()

    values = {
        name: pd.Series(index=out.index, dtype="float64") for name in selected
    }
    track_season = pd.to_numeric(history["season"], errors="raise")
    reference_seasons = sorted(int(value) for value in season.loc[ref].unique())
    for current_season in reference_seasons:
        current = ref & season.eq(current_season)
        stats = aggregate(track_season.ne(current_season))
        for name in selected:
            values[name].loc[current] = map_values(current, stats, source[name])
    full_stats = aggregate(pd.Series(True, index=history.index))
    for name in selected:
        values[name].loc[apply] = map_values(apply, full_stats, source[name])
        fallback = float(history[source[name]].mean())
        out[name] = values[name].fillna(fallback).astype("float32")
    return out


def resolve_feature_names(
    raw_columns: list[str], spec: dict[str, Any]
) -> tuple[list[str], list[str]]:
    unknown_exclusions = sorted(set(spec.get("exclude", [])) - set(raw_columns))
    if unknown_exclusions:
        raise ValueError(f"존재하지 않는 제공 피처를 제외하려고 합니다: {unknown_exclusions}")
    unknown_custom = sorted(set(spec.get("custom", [])) - set(CUSTOM_FEATURES))
    if unknown_custom:
        raise ValueError(f"정의되지 않은 파생 피처입니다: {unknown_custom}")

    base = list(raw_columns) if spec.get("include_all_raw", False) else []
    excluded = set(spec.get("exclude", []))
    selected = [column for column in base if column not in excluded]
    selected.extend(spec.get("custom", []))
    selected = list(dict.fromkeys(selected))

    expected = spec.get("expected_count")
    if expected is not None and len(selected) != int(expected):
        raise ValueError(
            f"피처 {spec.get('name')} 개수 불일치: expected={expected}, "
            f"actual={len(selected)}"
        )
    categorical = [
        column for column in spec.get("categorical", []) if column in selected
    ]
    return selected, categorical
