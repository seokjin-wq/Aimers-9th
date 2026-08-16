"""Leakage-safe feature definitions used by the CatBoost submission.

All custom features are calculated from one input row.  No target values,
future rows, or aggregates over test rows are used during inference.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


ID_COL = "row_id"
TARGET_COL = "control_success"
BASE_CATEGORICAL_COLUMNS = ("top_bottom", "game_type", "base_state")

PROVIDED_EVENT_STATE_COLUMNS = (
    "inning",
    "top_bottom",
    "game_type",
    "balls_before",
    "strikes_before",
    "outs_before",
    "run_top_before",
    "run_bot_before",
    "runner_on_1b",
    "runner_on_2b",
    "runner_on_3b",
    "pitcher_id",
    "batter_id",
    "pitcher_hand",
    "batter_hand",
    "pitcher_team_id",
    "batter_team_id",
)

PROVIDED_CALENDAR_DERIVED_COLUMNS = (
    "season",
    "game_month",
    "game_dayofweek",
)

PROVIDED_STATE_RECOMBINATION_COLUMNS = (
    "run_total_before",
    "score_diff_home",
    "score_diff_pitcher_team",
    "num_runners_on",
    "base_state",
)

PROVIDED_CONTEXT_METRIC_COLUMNS = (
    "home_win_expectancy",
    "away_win_expectancy",
    "li",
)

PROVIDED_ROW_DERIVED_COLUMNS = (
    PROVIDED_CALENDAR_DERIVED_COLUMNS
    + PROVIDED_STATE_RECOMBINATION_COLUMNS
    + PROVIDED_CONTEXT_METRIC_COLUMNS
)

REDUNDANT_PROVIDED_COLUMNS = {
    "asof_pitcher_pitchmix_n",
    "asof_pitcher_strike_rate",
    "asof_pitcher_fastball_rate",
    "run_total_before",
    "score_diff_home",
}

FINAL_CUSTOM_COLUMNS = (
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
)

RAW_EXCLUSION_REASONS = {
    "run_total_before": "run_top_before + run_bot_before로 재구성 가능",
    "score_diff_home": "run_bot_before - run_top_before로 재구성 가능",
    "asof_pitcher_pitchmix_n": "asof_pitcher_n과 동일",
    "asof_pitcher_strike_rate": "1 - asof_pitcher_ball_rate로 재구성 가능",
    "asof_pitcher_fastball_rate": "breaking_rate와 offspeed_rate로 재구성 가능",
    "asof_pitcher_prev5_game_success_rate": "복원 실험에서 2024 BSS가 하락",
}


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    features: tuple[str, ...]
    categorical: tuple[str, ...]
    description: str


def _safe_rate(series: pd.Series, prior: float) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(prior)


def _safe_count(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0)


def engineer_features(
    frame: pd.DataFrame,
    success_prior: float,
    shrinkage_k: float = 50.0,
) -> pd.DataFrame:
    """Add the 14 custom features selected by feature ablation."""

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
    out["runners_x_li"] = (out["num_runners_on"] * out["li"]).astype("float32")

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
    return out


def make_feature_specs(raw_columns: list[str]) -> dict[str, FeatureSpec]:
    """Return the compact set of controlled experiments kept for team use."""

    raw = [column for column in raw_columns if column not in {ID_COL, TARGET_COL}]
    event_state = [column for column in raw if column in PROVIDED_EVENT_STATE_COLUMNS]
    calendar = [column for column in raw if column in PROVIDED_CALENDAR_DERIVED_COLUMNS]
    recombination = [
        column for column in raw if column in PROVIDED_STATE_RECOMBINATION_COLUMNS
    ]
    context = [column for column in raw if column in PROVIDED_CONTEXT_METRIC_COLUMNS]
    non_history = [column for column in raw if not column.startswith("asof_")]
    compact = [column for column in raw if column not in REDUNDANT_PROVIDED_COLUMNS]
    selected_provided = [
        column
        for column in compact
        if column != "asof_pitcher_prev5_game_success_rate"
    ]

    def without(columns: list[str] | tuple[str, ...], excluded: set[str]) -> list[str]:
        return [column for column in columns if column not in excluded]

    def spec(
        name: str,
        base: list[str],
        extra: list[str] | tuple[str, ...],
        description: str,
    ) -> FeatureSpec:
        features = tuple(dict.fromkeys([*base, *extra]))
        categorical = tuple(
            column for column in BASE_CATEGORICAL_COLUMNS if column in features
        )
        return FeatureSpec(name, features, categorical, description)

    specs = {
        "raw47_random_forest": spec(
            "raw47_random_forest",
            raw,
            (),
            "공식 47개 입력에서 RandomForest 기준 재현",
        ),
        "raw47_catboost": spec(
            "raw47_catboost",
            raw,
            (),
            "공식 47개 입력에서 모델만 CatBoost로 변경",
        ),
        "provided_event_state17": spec(
            "provided_event_state17",
            event_state,
            (),
            "기초 관측·식별 17개만 사용",
        ),
        "event_state_plus_calendar20": spec(
            "event_state_plus_calendar20",
            [*event_state, *calendar],
            (),
            "기초 17개에 달력 파생 3개 추가",
        ),
        "event_state_plus_recombination22": spec(
            "event_state_plus_recombination22",
            [*event_state, *recombination],
            (),
            "기초 17개에 상태 재조합 5개 추가",
        ),
        "event_state_plus_context20": spec(
            "event_state_plus_context20",
            [*event_state, *context],
            (),
            "기초 17개에 계산 경기지표 3개 추가",
        ),
        "provided_non_history28": spec(
            "provided_non_history28",
            non_history,
            (),
            "기초 17개와 제공 행 파생 11개 사용",
        ),
        "selected_provided41_only": spec(
            "selected_provided41_only",
            selected_provided,
            (),
            "선택한 제공 피처 41개만 사용",
        ),
        "official47_plus_custom14": spec(
            "official47_plus_custom14",
            raw,
            FINAL_CUSTOM_COLUMNS,
            "제공 47개와 새 파생 14개 사용",
        ),
        "main55_fixed": spec(
            "main55_fixed",
            selected_provided,
            FINAL_CUSTOM_COLUMNS,
            "선택 제공 41개와 새 파생 14개 사용",
        ),
        "drop_calendar_origin": spec(
            "drop_calendar_origin",
            without(selected_provided, set(PROVIDED_CALENDAR_DERIVED_COLUMNS)),
            FINAL_CUSTOM_COLUMNS,
            "최종 55개에서 달력 파생 3개 제거",
        ),
        "drop_state_recombination_origin": spec(
            "drop_state_recombination_origin",
            without(
                selected_provided,
                {"score_diff_pitcher_team", "num_runners_on", "base_state"},
            ),
            without(FINAL_CUSTOM_COLUMNS, {"runners_x_li"}),
            "상태 재조합 3개와 의존 파생 제거",
        ),
        "drop_context_metric_origin": spec(
            "drop_context_metric_origin",
            without(selected_provided, set(PROVIDED_CONTEXT_METRIC_COLUMNS)),
            without(
                FINAL_CUSTOM_COLUMNS,
                {
                    "win_expectancy_dist50",
                    "runners_x_li",
                    "reverse_rate_x_li",
                    "offspeed_x_li",
                },
            ),
            "기대 승률·LI와 의존 파생 제거",
        ),
    }

    expected_counts = {
        "provided_event_state17": 17,
        "provided_non_history28": 28,
        "selected_provided41_only": 41,
        "official47_plus_custom14": 61,
        "main55_fixed": 55,
    }
    actual_counts = {name: len(specs[name].features) for name in expected_counts}
    if actual_counts != expected_counts:
        raise RuntimeError(
            f"Unexpected feature counts: expected={expected_counts}, actual={actual_counts}"
        )
    return specs
