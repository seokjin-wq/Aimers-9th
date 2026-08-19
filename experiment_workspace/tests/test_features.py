from __future__ import annotations

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from aimers_exp.config import DEFAULT_DATA_DIR, load_toml
from aimers_exp.features import (
    MAIN55_CUSTOM_FEATURES,
    ROW_LOCAL_CUSTOM_FEATURES,
    SEQUENTIAL_FEATURES,
    apply_official_state_reference,
    build_official_state_reference,
    engineer_features,
    engineer_official_train_target_features,
    engineer_official_train_state_features,
    engineer_official_train_progress_features,
    engineer_official_train_context_features,
    engineer_temporal_target_features,
    resolve_feature_names,
)

OPEN_DATA = DEFAULT_DATA_DIR


def test_feature_configs_have_expected_counts() -> None:
    raw_columns = [
        column
        for column in pd.read_csv(OPEN_DATA / "test.csv", nrows=0).columns
        if column != "row_id"
    ]
    expected = {
        "raw47": 47,
        "selected41": 41,
        "main55": 55,
        "main55_without_calendar": 52,
        "main55_without_state": 51,
        "main55_without_context": 48,
    }
    for name, count in expected.items():
        spec = load_toml(
            f"experiments/BASELINE_001_main55/features/{name}.toml"
        )["features"]
        features, _ = resolve_feature_names(raw_columns, spec)
        assert len(features) == count


def test_custom_features_are_row_local() -> None:
    test = pd.read_csv(OPEN_DATA / "test.csv")
    combined = engineer_features(test, success_prior=0.51)
    for index in test.index:
        isolated = engineer_features(test.loc[[index]], success_prior=0.51)
        assert_frame_equal(
            combined.loc[[index], list(ROW_LOCAL_CUSTOM_FEATURES)],
            isolated.loc[[index], list(ROW_LOCAL_CUSTOM_FEATURES)],
        )


def test_rule_invalid_custom_features_are_rejected() -> None:
    test = pd.read_csv(OPEN_DATA / "test.csv")
    with pytest.raises(ValueError, match="대회 규칙상"):
        engineer_features(
            test,
            success_prior=0.51,
            requested_custom=["global_recent100_success"],
        )


def test_season_position_features_are_not_row_local() -> None:
    assert {
        "season_pitch_index",
        "season_progress_proxy",
        "season_phase_20",
    }.issubset(SEQUENTIAL_FEATURES)


def test_main55_has_recorded_baseline_shape() -> None:
    test = pd.read_csv(OPEN_DATA / "test.csv")
    raw_columns = [column for column in test.columns if column != "row_id"]
    local_spec = load_toml(
        "experiments/BASELINE_001_main55/features/main55.toml"
    )["features"]
    local_features, _ = resolve_feature_names(raw_columns, local_spec)
    assert len(local_features) == 55
    assert local_features[-14:] == list(MAIN55_CUSTOM_FEATURES)


def test_temporal_target_features_ignore_current_season_labels() -> None:
    frame = pd.DataFrame(
        {
            "season": [2022, 2022, 2023, 2023],
            "pitcher_id": [1, 2, 1, 2],
            "batter_id": [10, 20, 10, 20],
            "pitcher_team_id": [100, 200, 100, 200],
            "batter_team_id": [200, 100, 200, 100],
        }
    )
    first = engineer_temporal_target_features(
        frame, pd.Series([1, 0, 1, 1]), success_prior=0.5
    )
    changed = engineer_temporal_target_features(
        frame, pd.Series([1, 0, 0, 0]), success_prior=0.5
    )
    temporal = [column for column in first if column not in frame]
    assert_frame_equal(first.loc[[2, 3], temporal], changed.loc[[2, 3], temporal])


def test_official_train_target_features_ignore_evaluation_targets() -> None:
    frame = pd.DataFrame(
        {
            "pitcher_id": [1, 1, 1, 2],
            "batter_id": [10, 20, 10, 20],
            "pitcher_team_id": [100, 100, 100, 200],
            "batter_team_id": [200, 100, 200, 100],
        }
    )
    reference = pd.Series([True, True, False, False])
    evaluation = ~reference
    first = engineer_official_train_target_features(
        frame,
        pd.Series([1, 0, 1, 1]),
        reference_mask=reference,
        apply_mask=evaluation,
        success_prior=0.5,
        requested=["pitcher_target_effect_k50"],
    )
    changed = engineer_official_train_target_features(
        frame,
        pd.Series([1, 0, 0, 0]),
        reference_mask=reference,
        apply_mask=evaluation,
        success_prior=0.5,
        requested=["pitcher_target_effect_k50"],
    )
    assert_frame_equal(
        first.loc[evaluation, ["pitcher_target_effect_k50"]],
        changed.loc[evaluation, ["pitcher_target_effect_k50"]],
    )


def test_official_train_state_feature_is_evaluation_row_independent() -> None:
    frame = pd.read_csv(OPEN_DATA / "train.csv", nrows=3)
    evaluation = frame.iloc[[2]].drop(columns=["control_success"])
    reference = frame.iloc[:2].drop(columns=["control_success"])
    combined = pd.concat([reference, evaluation], ignore_index=True)
    first = engineer_official_train_state_features(
        combined,
        reference_mask=pd.Series([True, True, False]),
        apply_mask=pd.Series([False, False, True]),
        requested=["pitcher_season_success_rate_k20"],
    )
    duplicated = pd.concat([combined, evaluation], ignore_index=True)
    second = engineer_official_train_state_features(
        duplicated,
        reference_mask=pd.Series([True, True, False, False]),
        apply_mask=pd.Series([False, False, True, True]),
        requested=["pitcher_season_success_rate_k20"],
    )
    assert first.loc[2, "pitcher_season_success_rate_k20"] == second.loc[
        2, "pitcher_season_success_rate_k20"
    ]


def test_exact_season_snapshot_uses_only_official_reference_target() -> None:
    frame = pd.DataFrame(
        {
            "row_id": ["TRAIN_000001", "TEST_000001", "TEST_000002"],
            "season": [2023, 2024, 2024],
            "pitcher_id": [7, 7, 7],
            "asof_pitcher_n": [9.0, 10.0, 10.0],
            "asof_pitcher_success_rate": [4 / 9, 0.5, 0.5],
            "asof_pitcher_reverse_rate": [0.0, 0.0, 0.0],
            "asof_pitcher_middle_rate": [0.0, 0.0, 0.0],
            "asof_pitcher_ball_rate": [0.0, 0.0, 0.0],
            "asof_pitcher_strike_rate": [1.0, 1.0, 1.0],
            "asof_pitcher_fastball_rate": [1.0, 1.0, 1.0],
            "asof_pitcher_breaking_rate": [0.0, 0.0, 0.0],
            "asof_pitcher_offspeed_rate": [0.0, 0.0, 0.0],
        }
    )
    reference = pd.Series([True, False, False])
    evaluation = ~reference
    requested = [
        "pitcher_season_n_exact",
        "pitcher_season_success_rate_exact_k20",
    ]
    first = engineer_official_train_state_features(
        frame,
        pd.Series([1.0, 1.0, 0.0]),
        reference_mask=reference,
        apply_mask=evaluation,
        requested=requested,
    )
    changed_eval_targets = engineer_official_train_state_features(
        frame,
        pd.Series([1.0, 0.0, 1.0]),
        reference_mask=reference,
        apply_mask=evaluation,
        requested=requested,
    )
    assert_frame_equal(first.loc[evaluation, requested], changed_eval_targets.loc[evaluation, requested])
    assert first.loc[1, "pitcher_season_n_exact"] == 0.0


def test_safe_progress_is_evaluation_row_independent() -> None:
    reference = pd.DataFrame(
        {
            "row_id": ["TRAIN_000100", "TRAIN_000101", "TRAIN_000250"],
            "season": [2022, 2022, 2023],
        }
    )
    evaluation = pd.DataFrame(
        {"row_id": ["TRAIN_000251"], "season": [2024]}
    )
    combined = pd.concat([reference, evaluation], ignore_index=True)
    requested = ["season_pitch_index_safe", "season_phase_20_safe"]
    first = engineer_official_train_progress_features(
        combined,
        reference_mask=pd.Series([True, True, True, False]),
        apply_mask=pd.Series([False, False, False, True]),
        requested=requested,
    )
    duplicated = pd.concat([combined, evaluation], ignore_index=True)
    second = engineer_official_train_progress_features(
        duplicated,
        reference_mask=pd.Series([True, True, True, False, False]),
        apply_mask=pd.Series([False, False, False, True, True]),
        requested=requested,
    )
    assert_frame_equal(first.loc[[3], requested], second.loc[[3], requested])
    assert first.loc[3, "season_pitch_index_safe"] == 0


def test_context_features_ignore_evaluation_targets() -> None:
    frame = pd.read_csv(OPEN_DATA / "train.csv", nrows=6).drop(
        columns=["control_success"]
    )
    reference = pd.Series([True, True, True, True, False, False])
    evaluation = ~reference
    first = engineer_official_train_context_features(
        frame,
        pd.Series([1, 0, 1, 0, 1, 1]),
        reference_mask=reference,
        apply_mask=evaluation,
        requested=["count_hands_target_effect"],
    )
    changed = engineer_official_train_context_features(
        frame,
        pd.Series([1, 0, 1, 0, 0, 0]),
        reference_mask=reference,
        apply_mask=evaluation,
        requested=["count_hands_target_effect"],
    )
    assert_frame_equal(
        first.loc[evaluation, ["count_hands_target_effect"]],
        changed.loc[evaluation, ["count_hands_target_effect"]],
    )


def test_frozen_state_reference_matches_official_train_transform() -> None:
    frame = pd.DataFrame(
        {
            "row_id": ["A1", "A2", "A3", "T1"],
            "season": [2023, 2024, 2024, 2025],
            "pitcher_id": [7, 7, 8, 7],
            "asof_pitcher_n": [10.0, 15.0, 3.0, 21.0],
            "asof_pitcher_success_rate": [0.5, 0.6, 0.4, 13.0 / 21.0],
            "asof_pitcher_reverse_rate": [0.1, 0.1, 0.1, 0.1],
            "asof_pitcher_middle_rate": [0.2, 0.2, 0.2, 0.2],
            "asof_pitcher_ball_rate": [0.3, 0.3, 0.3, 0.3],
            "asof_pitcher_strike_rate": [0.7, 0.7, 0.7, 0.7],
            "asof_pitcher_fastball_rate": [0.5, 0.5, 0.5, 0.5],
            "asof_pitcher_breaking_rate": [0.3, 0.3, 0.3, 0.3],
            "asof_pitcher_offspeed_rate": [0.2, 0.2, 0.2, 0.2],
        }
    )
    requested = ["pitcher_season_n", "pitcher_season_success_rate_k20"]
    reference_mask = pd.Series([True, True, True, False])
    apply_mask = ~reference_mask
    expected = engineer_official_train_state_features(
        frame,
        pd.Series([1.0, 0.0, 1.0, 0.0]),
        reference_mask=reference_mask,
        apply_mask=apply_mask,
        requested=requested,
    )
    frozen = build_official_state_reference(
        frame.loc[reference_mask], requested=requested
    )
    actual = apply_official_state_reference(
        frame.loc[apply_mask], frozen, requested=requested
    )
    assert_frame_equal(expected.loc[apply_mask, requested], actual[requested])

    duplicated = pd.concat(
        [frame.loc[apply_mask], frame.loc[apply_mask]], ignore_index=True
    )
    duplicate_result = apply_official_state_reference(
        duplicated, frozen, requested=requested
    )
    assert_frame_equal(
        actual[requested].reset_index(drop=True), duplicate_result.loc[[0], requested]
    )
