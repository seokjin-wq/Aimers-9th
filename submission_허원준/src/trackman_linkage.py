"""Target-free TrackMan-to-competition pitcher linkage.

This module keeps the two adopted research methods behind one interface:

* E00: nine-context pitch-count vectors, cosine similarity, same-hand
  candidates, score/margin thresholds, and mutual top-1 acceptance.
* E11: cutoff-safe iterative unique-row voting, based on the reproduced v3
  row-first method with one-to-one collision repair and audit variants.

Both methods use only rows whose ``season`` is strictly earlier than the
requested cutoff. They never use ``control_success``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import sparse


MAIN_ID = "pitcher_id"
TRACKMAN_ID = "pitcher_trackman_id"
MAIN_ROW_ID = "row_id"
TRACKMAN_ROW_ID = "trackman_id"

E00_CONTEXT_COLUMNS = (
    "season",
    "game_month",
    "game_dayofweek",
    "inning",
    "top_bottom",
    "balls_before",
    "strikes_before",
    "outs_before",
    "pitcher_hand",
)

E11_ROW_CONTEXT_COLUMNS = (
    *E00_CONTEXT_COLUMNS,
    "batter_hand",
)


@dataclass(frozen=True)
class E00Thresholds:
    min_cosine: float = 0.20
    min_margin: float = 0.05


@dataclass(frozen=True)
class E11Rules:
    min_votes: int = 3
    min_dominance: float = 0.70
    high_dominance: float = 0.90
    max_rounds: int = 10


@dataclass(frozen=True)
class E11Result:
    mapping: pd.DataFrame
    rounds: pd.DataFrame


@dataclass(frozen=True)
class _ContextMatrix:
    ids: np.ndarray
    hands: np.ndarray
    matrix: sparse.csr_matrix
    pitch_counts: np.ndarray


def _require_columns(frame: pd.DataFrame, columns: set[str], source: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{source} 입력 컬럼 누락: {missing}")


def _normalize_top_bottom(values: pd.Series) -> pd.Series:
    normalized = values.map({"T": "T", "Top": "T", "B": "B", "Bottom": "B"})
    if normalized.isna().any():
        invalid = sorted(values.loc[normalized.isna()].astype(str).unique())
        raise ValueError(f"지원하지 않는 top_bottom 값: {invalid}")
    return normalized


def _normalize_hand(values: pd.Series) -> pd.Series:
    normalized = values.map(
        {1: 1, 2: 2, "1": 1, "2": 2, "Left": 1, "Right": 2}
    )
    if normalized.isna().any():
        invalid = sorted(values.loc[normalized.isna()].astype(str).unique())
        raise ValueError(f"지원하지 않는 손 유형 값: {invalid}")
    return normalized.astype("Int64")


# ---------------------------------------------------------------------------
# E00: context-count cosine


def _aggregate_e00_contexts(
    frame: pd.DataFrame,
    *,
    id_column: str,
    cutoff_season: int,
) -> pd.DataFrame:
    required = {id_column, *E00_CONTEXT_COLUMNS}
    _require_columns(frame, required, id_column)
    history = frame.loc[
        frame["season"].lt(cutoff_season), [id_column, *E00_CONTEXT_COLUMNS]
    ].copy()
    if history.empty:
        raise ValueError(f"{cutoff_season}시즌 이전 연결 이력이 없습니다.")
    if history.isna().any().any():
        null_columns = history.columns[history.isna().any()].tolist()
        raise ValueError(f"E00 연결 키에 결측치가 있습니다: {null_columns}")
    history["top_bottom"] = _normalize_top_bottom(history["top_bottom"])
    history["pitcher_hand"] = _normalize_hand(history["pitcher_hand"])
    return (
        history.groupby([id_column, *E00_CONTEXT_COLUMNS], observed=True, sort=True)
        .size()
        .rename("pitch_count")
        .reset_index()
    )


def _first_observed_hands(
    frame: pd.DataFrame,
    *,
    id_column: str,
    cutoff_season: int,
) -> pd.Series:
    history = frame.loc[
        frame["season"].lt(cutoff_season), [id_column, "pitcher_hand"]
    ].copy()
    history["pitcher_hand"] = _normalize_hand(history["pitcher_hand"])
    return history.groupby(id_column, sort=True)["pitcher_hand"].first()


def _build_e00_matrices(
    main_counts: pd.DataFrame,
    trackman_counts: pd.DataFrame,
    *,
    main_hands: pd.Series,
    trackman_hands: pd.Series,
) -> tuple[_ContextMatrix, _ContextMatrix]:
    contexts = pd.concat(
        [
            main_counts.loc[:, E00_CONTEXT_COLUMNS],
            trackman_counts.loc[:, E00_CONTEXT_COLUMNS],
        ],
        ignore_index=True,
    )
    hashes = pd.util.hash_pandas_object(contexts, index=False).to_numpy()
    context_codes, unique_contexts = pd.factorize(hashes, sort=False)
    split = len(main_counts)

    def build(
        counts: pd.DataFrame,
        id_column: str,
        codes: np.ndarray,
        hands_by_id: pd.Series,
    ) -> _ContextMatrix:
        ids = np.sort(counts[id_column].unique())
        id_lookup = pd.Series(np.arange(len(ids), dtype=np.int32), index=ids)
        rows = counts[id_column].map(id_lookup).to_numpy(dtype=np.int32)
        values = counts["pitch_count"].to_numpy(dtype=np.float64)
        matrix = sparse.csr_matrix(
            (values, (rows, codes)),
            shape=(len(ids), len(unique_contexts)),
            dtype=np.float64,
        )
        hands = hands_by_id.reindex(ids).to_numpy()
        if pd.isna(hands).any():
            raise ValueError("투수 손 방향을 찾을 수 없는 ID가 있습니다.")
        return _ContextMatrix(
            ids=ids,
            hands=hands,
            matrix=matrix,
            pitch_counts=np.asarray(matrix.sum(axis=1)).ravel().astype(np.int64),
        )

    main = build(main_counts, MAIN_ID, context_codes[:split], main_hands)
    trackman = build(
        trackman_counts,
        TRACKMAN_ID,
        context_codes[split:],
        trackman_hands,
    )
    return main, trackman


def _l2_normalize(matrix: sparse.csr_matrix) -> sparse.csr_matrix:
    norms = np.sqrt(np.asarray(matrix.multiply(matrix).sum(axis=1)).ravel())
    if np.any(norms == 0):
        raise ValueError("L2 정규화할 수 없는 빈 투수 벡터가 있습니다.")
    return sparse.diags(1.0 / norms) @ matrix


def match_pitchers_e00(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
    *,
    cutoff_season: int = 2025,
    thresholds: E00Thresholds = E00Thresholds(),
) -> pd.DataFrame:
    """Run the E00 nine-context cosine linkage baseline."""

    main_counts = _aggregate_e00_contexts(
        main, id_column=MAIN_ID, cutoff_season=cutoff_season
    )
    trackman_counts = _aggregate_e00_contexts(
        trackman, id_column=TRACKMAN_ID, cutoff_season=cutoff_season
    )
    main_hands = _first_observed_hands(
        main, id_column=MAIN_ID, cutoff_season=cutoff_season
    )
    trackman_hands = _first_observed_hands(
        trackman, id_column=TRACKMAN_ID, cutoff_season=cutoff_season
    )
    main_matrix, trackman_matrix = _build_e00_matrices(
        main_counts,
        trackman_counts,
        main_hands=main_hands,
        trackman_hands=trackman_hands,
    )

    similarities = (
        _l2_normalize(main_matrix.matrix)
        @ _l2_normalize(trackman_matrix.matrix).T
    ).toarray()
    similarities = np.where(
        main_matrix.hands[:, None] == trackman_matrix.hands[None, :],
        similarities,
        -1.0,
    )
    if similarities.shape[1] < 2:
        raise ValueError("top-1/top-2 계산에는 TrackMan 투수가 2명 이상 필요합니다.")

    best_indices = np.argmax(similarities, axis=1)
    reverse_best = np.argmax(similarities, axis=0)
    row_indices = np.arange(len(main_matrix.ids))
    best_scores = similarities[row_indices, best_indices]
    alternatives = similarities.copy()
    alternatives[row_indices, best_indices] = -1.0
    second_scores = alternatives.max(axis=1)
    margins = best_scores - second_scores
    mutual = reverse_best[best_indices] == row_indices
    accepted = (
        best_scores >= thresholds.min_cosine
    ) & (margins >= thresholds.min_margin) & mutual

    confidence = np.full(len(main_matrix.ids), "low", dtype=object)
    confidence[accepted] = "medium"
    confidence[accepted & (best_scores >= 0.60) & (margins >= 0.20)] = "high"

    reasons: list[str] = []
    for score, margin, is_mutual in zip(
        best_scores, margins, mutual, strict=True
    ):
        failed = []
        if score < thresholds.min_cosine:
            failed.append("score")
        if margin < thresholds.min_margin:
            failed.append("margin")
        if not is_mutual:
            failed.append("not_mutual")
        reasons.append("accepted" if not failed else "+".join(failed))

    candidate_ids = trackman_matrix.ids[best_indices].astype(float)
    accepted_ids = candidate_ids.copy()
    accepted_ids[~accepted] = np.nan
    result = pd.DataFrame(
        {
            MAIN_ID: main_matrix.ids,
            "candidate_trackman_id": candidate_ids,
            TRACKMAN_ID: accepted_ids,
            "match_score": best_scores.astype("float32"),
            "second_score": second_scores.astype("float32"),
            "match_margin": margins.astype("float32"),
            "candidate_rank": np.ones(len(main_matrix.ids), dtype=np.int64),
            "mutual_best": mutual.astype("int8"),
            "main_pitch_count": main_matrix.pitch_counts,
            "trackman_pitch_count": trackman_matrix.pitch_counts[best_indices],
            "accepted": accepted.astype("int8"),
            "confidence": confidence,
            "decision_reason": reasons,
        }
    )
    return result.sort_values(MAIN_ID).reset_index(drop=True)


# ---------------------------------------------------------------------------
# E11: iterative row-first linkage


def _trackman_tier(team: pd.Series) -> pd.Series:
    result = pd.Series("major", index=team.index, dtype="string")
    result.loc[team.str.startswith("MIN_", na=False)] = "minor"
    result.loc[
        team.str.startswith("KBO_", na=False)
        | team.str.startswith("ACE_", na=False)
    ] = "other"
    result.loc[team.isna()] = pd.NA
    return result


def _normalize_e11_sources(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
    cutoff_season: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    main_required = {MAIN_ROW_ID, MAIN_ID, "game_type", *E11_ROW_CONTEXT_COLUMNS}
    trackman_required = {
        TRACKMAN_ROW_ID,
        TRACKMAN_ID,
        "pitcher_team",
        *E11_ROW_CONTEXT_COLUMNS,
    }
    _require_columns(main, main_required, "competition")
    _require_columns(trackman, trackman_required, "trackman")

    main_hist = main.loc[main["season"].lt(cutoff_season)].copy()
    trackman_hist = trackman.loc[trackman["season"].lt(cutoff_season)].copy()
    if main_hist.empty or trackman_hist.empty:
        raise ValueError(f"{cutoff_season}시즌 이전 E11 연결 이력이 없습니다.")

    for column in ("pitcher_hand", "batter_hand"):
        main_hist[column] = _normalize_hand(main_hist[column])
        trackman_hist[column] = _normalize_hand(trackman_hist[column])
    main_hist["top_bottom"] = _normalize_top_bottom(main_hist["top_bottom"])
    trackman_hist["top_bottom"] = _normalize_top_bottom(trackman_hist["top_bottom"])
    main_hist["game_type"] = main_hist["game_type"].astype("string")
    main_hist["team_tier"] = main_hist["game_type"].map(
        {"R": "major", "F": "minor"}
    ).astype("string")
    trackman_hist["team_tier"] = _trackman_tier(trackman_hist["pitcher_team"])
    return main_hist, trackman_hist


def _unique_direct_matches(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
    *,
    include_tier: bool,
) -> pd.DataFrame:
    key_columns = [*E11_ROW_CONTEXT_COLUMNS]
    if include_tier:
        key_columns.append("team_tier")
    main_unique = main.loc[
        ~main.duplicated(key_columns, keep=False),
        [MAIN_ROW_ID, MAIN_ID, *key_columns],
    ]
    trackman_unique = trackman.loc[
        ~trackman.duplicated(key_columns, keep=False),
        [TRACKMAN_ROW_ID, TRACKMAN_ID, *key_columns],
    ]
    return main_unique.merge(
        trackman_unique,
        on=key_columns,
        how="inner",
        validate="one_to_one",
    )


def _induce_reference_mapping(
    direct: pd.DataFrame,
    *,
    rules: E11Rules,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for pitcher_id, group in direct.groupby(MAIN_ID, sort=True):
        votes = group[TRACKMAN_ID].value_counts()
        winner = votes.index[0]
        winning_votes = int(votes.iloc[0])
        second_votes = int(votes.iloc[1]) if len(votes) > 1 else 0
        total_votes = int(len(group))
        dominance = winning_votes / total_votes
        season_winners = group.groupby("season")[TRACKMAN_ID].agg(
            lambda values: values.value_counts().index[0]
        )
        support_seasons = int(len(season_winners))
        season_consistency = float(season_winners.eq(winner).mean())
        if (
            total_votes >= rules.min_votes
            and dominance >= rules.high_dominance
            and (support_seasons == 1 or season_consistency == 1.0)
        ):
            confidence = "high"
        elif total_votes >= rules.min_votes and dominance >= rules.min_dominance:
            confidence = "medium"
        else:
            confidence = "low"
        rows.append(
            {
                MAIN_ID: pitcher_id,
                TRACKMAN_ID: winner,
                "votes": winning_votes,
                "second_votes": second_votes,
                "total_votes": total_votes,
                "dominance": dominance,
                "vote_gap": winning_votes - second_votes,
                "support_seasons": support_seasons,
                "season_consistency": season_consistency,
                "confidence": confidence,
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            MAIN_ID,
            TRACKMAN_ID,
            "votes",
            "second_votes",
            "total_votes",
            "dominance",
            "vote_gap",
            "support_seasons",
            "season_consistency",
            "confidence",
        ],
    )


def _reference_iterative_linkage(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
    *,
    include_tier: bool,
    rules: E11Rules,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    resolved_main: set[object] = set()
    resolved_trackman: set[object] = set()
    accepted_rounds: list[pd.DataFrame] = []
    round_rows: list[dict[str, object]] = []

    for round_number in range(1, rules.max_rounds + 1):
        active_main = main.loc[~main[MAIN_ID].isin(resolved_main)]
        active_trackman = trackman.loc[~trackman[TRACKMAN_ID].isin(resolved_trackman)]
        direct = _unique_direct_matches(
            active_main,
            active_trackman,
            include_tier=include_tier,
        )
        induced = _induce_reference_mapping(direct, rules=rules)
        accepted = induced.loc[
            induced["confidence"].isin(["high", "medium"])
        ].copy()
        collisions_removed = 0
        if not accepted.empty:
            accepted["_confidence_rank"] = accepted["confidence"].map(
                {"high": 2, "medium": 1}
            )
            accepted = accepted.sort_values(
                [
                    TRACKMAN_ID,
                    "_confidence_rank",
                    "dominance",
                    "votes",
                    "vote_gap",
                    MAIN_ID,
                ],
                ascending=[True, False, False, False, False, True],
            )
            before = len(accepted)
            accepted = accepted.drop_duplicates(TRACKMAN_ID, keep="first").drop(
                columns="_confidence_rank"
            )
            collisions_removed = before - len(accepted)

        round_rows.append(
            {
                "round": round_number,
                "include_tier": include_tier,
                "active_main_pitchers": int(active_main[MAIN_ID].nunique()),
                "active_trackman_pitchers": int(
                    active_trackman[TRACKMAN_ID].nunique()
                ),
                "direct_unique_rows": int(len(direct)),
                "candidate_main_pitchers": int(induced[MAIN_ID].nunique())
                if not induced.empty
                else 0,
                "accepted_pitchers": int(len(accepted)),
                "collisions_removed": int(collisions_removed),
            }
        )
        if accepted.empty:
            break
        accepted["round"] = round_number
        accepted_rounds.append(accepted)
        resolved_main.update(accepted[MAIN_ID].tolist())
        resolved_trackman.update(accepted[TRACKMAN_ID].tolist())

    mapping = (
        pd.concat(accepted_rounds, ignore_index=True)
        if accepted_rounds
        else pd.DataFrame(columns=[MAIN_ID, TRACKMAN_ID, "confidence"])
    )
    if mapping[MAIN_ID].duplicated().any() or mapping[TRACKMAN_ID].duplicated().any():
        raise RuntimeError("E11 one-to-one assignment invariant violated")
    return mapping, pd.DataFrame(round_rows)


def _aligned_context_split(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
    *,
    holdout_modulus: int = 5,
) -> tuple[pd.Series, pd.Series]:
    contexts = pd.concat(
        [
            main.loc[:, E11_ROW_CONTEXT_COLUMNS],
            trackman.loc[:, E11_ROW_CONTEXT_COLUMNS],
        ],
        ignore_index=True,
    )
    hashes = pd.util.hash_pandas_object(contexts, index=False).to_numpy()
    main_discovery = hashes[: len(main)] % holdout_modulus != 0
    trackman_discovery = hashes[len(main):] % holdout_modulus != 0
    return (
        pd.Series(main_discovery, index=main.index),
        pd.Series(trackman_discovery, index=trackman.index),
    )


def _holdout_vote_validation(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
) -> pd.DataFrame:
    direct = _unique_direct_matches(main, trackman, include_tier=False)
    votes = (
        direct.groupby([MAIN_ID, TRACKMAN_ID], observed=True)
        .size()
        .rename("holdout_votes")
        .reset_index()
    )
    if votes.empty:
        return pd.DataFrame(columns=[MAIN_ID, "holdout_top_trackman_id"])
    votes = votes.sort_values(
        [MAIN_ID, "holdout_votes", TRACKMAN_ID], ascending=[True, False, True]
    )
    votes["rank"] = votes.groupby(MAIN_ID, observed=True).cumcount() + 1
    top = votes.loc[votes["rank"].eq(1)].copy()
    second = votes.loc[
        votes["rank"].eq(2), [MAIN_ID, "holdout_votes"]
    ].rename(columns={"holdout_votes": "holdout_second_votes"})
    total = votes.groupby(MAIN_ID, observed=True)["holdout_votes"].sum().rename(
        "holdout_total_votes"
    )
    top = top.merge(second, on=MAIN_ID, how="left").join(total, on=MAIN_ID)
    top["holdout_second_votes"] = top["holdout_second_votes"].fillna(0).astype(
        "int64"
    )
    top["holdout_top_share"] = top["holdout_votes"] / top["holdout_total_votes"]
    top["holdout_top_tied"] = top["holdout_votes"].eq(
        top["holdout_second_votes"]
    )
    return top.rename(columns={TRACKMAN_ID: "holdout_top_trackman_id"})


def _compose_e11_mapping(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
    tier_assisted: pd.DataFrame,
    tier_free: pd.DataFrame,
    split_discovery: pd.DataFrame,
    holdout_validation: pd.DataFrame,
) -> pd.DataFrame:
    population = pd.DataFrame({MAIN_ID: np.sort(main[MAIN_ID].dropna().unique())})
    evidence_columns = [
        MAIN_ID,
        TRACKMAN_ID,
        "votes",
        "second_votes",
        "total_votes",
        "dominance",
        "vote_gap",
        "support_seasons",
        "season_consistency",
        "confidence",
        "round",
    ]
    assisted = tier_assisted.reindex(columns=evidence_columns).rename(
        columns={
            column: f"tier_{column}"
            for column in evidence_columns
            if column != MAIN_ID
        }
    )
    free = tier_free.reindex(columns=evidence_columns).rename(
        columns={
            column: f"free_{column}"
            for column in evidence_columns
            if column != MAIN_ID
        }
    )
    split = split_discovery.reindex(columns=[MAIN_ID, TRACKMAN_ID]).rename(
        columns={TRACKMAN_ID: "split_trackman_id"}
    )
    result = population.merge(assisted, on=MAIN_ID, how="left").merge(
        free, on=MAIN_ID, how="left"
    )
    result = result.merge(split, on=MAIN_ID, how="left").merge(
        holdout_validation, on=MAIN_ID, how="left"
    )
    result["variant_pair_agree"] = result["tier_pitcher_trackman_id"].eq(
        result["free_pitcher_trackman_id"]
    )
    result["split_discovery_agree"] = result["tier_pitcher_trackman_id"].eq(
        result["split_trackman_id"]
    )
    holdout_tied = result["holdout_top_tied"].astype("boolean").fillna(True)
    result["holdout_top_agree"] = (
        result["tier_pitcher_trackman_id"].eq(result["holdout_top_trackman_id"])
        & ~holdout_tied
    )
    result["accepted"] = result["tier_pitcher_trackman_id"].notna().astype("int8")
    result["confidence"] = result["tier_confidence"].fillna("low")
    result["audit_strong"] = (
        result["accepted"].eq(1)
        & result["variant_pair_agree"]
        & result["split_discovery_agree"]
        & result["holdout_top_agree"]
        & result["holdout_votes"].fillna(0).ge(2)
        & result["holdout_top_share"].fillna(0).ge(0.80)
    )
    result["candidate_trackman_id"] = result["tier_pitcher_trackman_id"]
    result[TRACKMAN_ID] = result["candidate_trackman_id"].where(
        result["accepted"].eq(1)
    )
    result["match_score"] = result["tier_dominance"]
    result["match_margin"] = result["tier_vote_gap"] / result["tier_total_votes"]
    result["second_score"] = result["match_score"] - result["match_margin"]
    result["candidate_rank"] = np.where(
        result["candidate_trackman_id"].notna(), 1, -1
    )
    result["mutual_best"] = result["accepted"]

    main_counts = main.groupby(MAIN_ID, observed=True).size().rename(
        "main_pitch_count"
    )
    trackman_counts = trackman.groupby(TRACKMAN_ID, observed=True).size().rename(
        "trackman_pitch_count"
    )
    result = result.join(main_counts, on=MAIN_ID).join(
        trackman_counts, on="candidate_trackman_id"
    )
    conditions = [
        result["accepted"].eq(1) & result["audit_strong"],
        result["accepted"].eq(1) & result["variant_pair_agree"],
        result["accepted"].eq(1),
    ]
    choices = [
        "accepted_reference_and_all_corroboration",
        "accepted_reference_and_tier_free_agreement",
        "accepted_reference_only",
    ]
    result["decision_reason"] = np.select(
        conditions, choices, default="not_resolved_by_reference_v3"
    )
    return result.sort_values(MAIN_ID).reset_index(drop=True)


def match_pitchers_e11(
    main: pd.DataFrame,
    trackman: pd.DataFrame,
    *,
    cutoff_season: int = 2025,
    rules: E11Rules = E11Rules(),
) -> E11Result:
    """Run the one-to-one-corrected E11 iterative row-first linkage."""

    main_hist, trackman_hist = _normalize_e11_sources(
        main, trackman, cutoff_season
    )
    tier_assisted, tier_rounds = _reference_iterative_linkage(
        main_hist,
        trackman_hist,
        include_tier=True,
        rules=rules,
    )
    tier_free, free_rounds = _reference_iterative_linkage(
        main_hist,
        trackman_hist,
        include_tier=False,
        rules=rules,
    )
    main_discovery, trackman_discovery = _aligned_context_split(
        main_hist, trackman_hist
    )
    split_discovery, split_rounds = _reference_iterative_linkage(
        main_hist.loc[main_discovery],
        trackman_hist.loc[trackman_discovery],
        include_tier=False,
        rules=rules,
    )
    holdout = _holdout_vote_validation(
        main_hist.loc[~main_discovery],
        trackman_hist.loc[~trackman_discovery],
    )
    mapping = _compose_e11_mapping(
        main_hist,
        trackman_hist,
        tier_assisted,
        tier_free,
        split_discovery,
        holdout,
    )
    rounds = pd.concat(
        [
            tier_rounds.assign(variant="tier_assisted_full"),
            free_rounds.assign(variant="tier_free_full"),
            split_rounds.assign(variant="tier_free_discovery_80pct"),
        ],
        ignore_index=True,
    )
    return E11Result(mapping=mapping, rounds=rounds)


def summarize_linkage_methods(
    e00: pd.DataFrame | None,
    e11: pd.DataFrame | None,
) -> dict[str, object]:
    """Return compact method metrics and E00/E11 agreement evidence."""

    payload: dict[str, object] = {}
    for method, mapping in (("E00", e00), ("E11", e11)):
        if mapping is None:
            continue
        accepted = mapping.loc[mapping["accepted"].eq(1)]
        payload[method] = {
            "candidate_pitchers": int(len(mapping)),
            "accepted_pitchers": int(len(accepted)),
            "pitcher_coverage": float(len(accepted) / len(mapping)),
            "unique_trackman_ids": int(accepted[TRACKMAN_ID].nunique()),
            "duplicate_assignments": int(
                accepted[TRACKMAN_ID].duplicated().sum()
            ),
            "high_confidence": int(mapping["confidence"].eq("high").sum()),
            "medium_confidence": int(mapping["confidence"].eq("medium").sum()),
        }
    if e00 is not None and e11 is not None:
        left = e00.loc[e00["accepted"].eq(1), [MAIN_ID, TRACKMAN_ID]]
        right = e11.loc[e11["accepted"].eq(1), [MAIN_ID, TRACKMAN_ID]]
        common = left.merge(
            right,
            on=MAIN_ID,
            how="inner",
            suffixes=("_e00", "_e11"),
        )
        same = common[f"{TRACKMAN_ID}_e00"].eq(
            common[f"{TRACKMAN_ID}_e11"]
        )
        payload["agreement"] = {
            "common_accepted_pitchers": int(len(common)),
            "same_pairs": int(same.sum()),
            "pair_agreement": float(same.mean()) if len(common) else None,
            "e00_only": int(len(left) - len(common)),
            "e11_only": int(len(right) - len(common)),
        }
    return payload
