"""Phase 2 -- train <-> trackman pitcher identity + row-level matching.

Two stages, per `plans/swift-munching-hippo.md` Phase 2:

2-A `match_pitchers_by_season`: train has no direct pitcher_id <->
    pitcher_trackman_id key (value ranges never overlap -- confirmed in
    reports/eda_trackman/README.md §8). Instead, build a per-
    (pitcher, season) "fingerprint" (pitch count, hand, fastball/
    breaking/offspeed mix, major/minor team-tier mix) independently on
    each side and solve a min-cost bipartite assignment (Hungarian
    algorithm) within each (season, hand) candidate group. A pitcher's
    identity should be stable across seasons, so agreement across a
    pitcher's multiple active seasons becomes the main confidence signal.

2-B `match_rows`: within a confidently-matched pitcher pair, group both
    sides by `situational_key` (season+month+dayofweek+inning+top_bottom+
    count state -- see src/trackman_clean.py). A unique 1:1 group is a
    high-confidence row match. A group with more rows on one or both
    sides is disambiguated by pairing same-rank rows after sorting each
    side by its own native ascending id (train `row_id`, trackman
    `trackman_id`), on the assumption both files preserve their original
    per-pitcher event order -- an assumption this module explicitly
    checks (`order_consistency_check`) rather than takes on faith.

Nothing here is used by any training/inference code yet -- this is the
Phase 2 investigation whose output (match coverage/precision) gates
whether Phase 3 (feature engineering) proceeds at all.
"""

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

# train.csv's pitcher_hand/batter_hand are integer-coded (1/2), undocumented
# in data_description.md beyond "좌우 유형 코드". Inferred correspondence to
# trackman's Right/Left strings from matching population proportions (train:
# 2=73.9%, 1=25.8%; trackman: Right=74.9%, Left=25.1% -- see
# reports/trackman_id_mapping/README.md §1). This is a hypothesis used only
# to group candidates for matching, not asserted as confirmed fact.
TRAIN_HAND_TO_TRACKMAN = {2: "Right", 1: "Left"}


# --- 2-A. Pitcher-level season fingerprints ---------------------------------


def build_train_pitcher_fingerprints(train_raw, train_match_keys):
    """One row per (pitcher_id, season). `train_raw` supplies the asof_*
    pitch-mix columns (not present in the slim train_match_keys table);
    `train_match_keys` supplies `team_tier` (already derived from
    game_type, see trackman_clean.build_train_match_keys)."""
    df = train_raw[
        [
            "row_id",
            "pitcher_id",
            "season",
            "pitcher_hand",
            "asof_pitcher_fastball_rate",
            "asof_pitcher_breaking_rate",
            "asof_pitcher_offspeed_rate",
        ]
    ].merge(train_match_keys[["row_id", "team_tier"]], on="row_id", how="left")

    n_pitches = df.groupby(["pitcher_id", "season"]).size().rename("n_pitches")

    # Last row (by row_id) per (pitcher, season) approximates the
    # pitcher's career-cumulative pitch mix as of around that season --
    # the same approximation already used/documented in
    # plans/swift-munching-hippo.md Phase 2-A (asof_* is career-cumulative,
    # not season-reset, so this is directional, not exact).
    df_sorted = df.sort_values(["pitcher_id", "season", "row_id"])
    last_row = df_sorted.groupby(["pitcher_id", "season"]).tail(1).set_index(
        ["pitcher_id", "season"]
    )

    hand_mode = (
        df.groupby(["pitcher_id", "season"])["pitcher_hand"]
        .agg(lambda s: s.mode().iloc[0])
        .rename("hand_code")
    )
    major_rate = (
        df.groupby(["pitcher_id", "season"])["team_tier"]
        .apply(lambda s: (s == "major").mean())
        .rename("major_rate")
    )

    fp = pd.concat(
        [
            n_pitches,
            hand_mode,
            major_rate,
            last_row[
                [
                    "asof_pitcher_fastball_rate",
                    "asof_pitcher_breaking_rate",
                    "asof_pitcher_offspeed_rate",
                ]
            ].rename(
                columns={
                    "asof_pitcher_fastball_rate": "fastball_rate",
                    "asof_pitcher_breaking_rate": "breaking_rate",
                    "asof_pitcher_offspeed_rate": "offspeed_rate",
                }
            ),
        ],
        axis=1,
    ).reset_index()
    fp["hand"] = fp["hand_code"].map(TRAIN_HAND_TO_TRACKMAN)
    return fp


def build_trackman_pitcher_fingerprints(trackman_clean):
    df = trackman_clean[
        [
            "pitcher_trackman_id",
            "season",
            "pitcher_hand",
            "pitcher_team_tier",
            "is_fastball",
            "is_breaking",
        ]
    ].copy()
    df["is_offspeed"] = 1 - df["is_fastball"] - df["is_breaking"]
    # pitch_type_group has a 4th bucket ("other") outside fastball/
    # breaking/offspeed; is_offspeed as defined above would be negative
    # for "other" rows, so clip it out explicitly rather than let a
    # silent negative rate corrupt the fingerprint distance.
    other_mask = trackman_clean.loc[df.index, "pitch_type_group"] == "other"
    df.loc[other_mask, ["is_fastball", "is_breaking", "is_offspeed"]] = np.nan

    n_pitches = df.groupby(["pitcher_trackman_id", "season"]).size().rename("n_pitches")
    hand_mode = (
        df.groupby(["pitcher_trackman_id", "season"])["pitcher_hand"]
        .agg(lambda s: s.mode().iloc[0])
        .rename("hand")
    )
    major_rate = (
        df.groupby(["pitcher_trackman_id", "season"])["pitcher_team_tier"]
        .apply(lambda s: (s == "major").mean())
        .rename("major_rate")
    )
    mix = df.groupby(["pitcher_trackman_id", "season"])[
        ["is_fastball", "is_breaking", "is_offspeed"]
    ].mean().rename(
        columns={
            "is_fastball": "fastball_rate",
            "is_breaking": "breaking_rate",
            "is_offspeed": "offspeed_rate",
        }
    )

    fp = pd.concat([n_pitches, hand_mode, major_rate, mix], axis=1).reset_index()
    return fp


def _match_one_group(train_g, tm_g, w_mix=1.0, w_tier=1.0, w_rank=0.5):
    """Hungarian assignment within one (season, hand) group. Returns a
    DataFrame with one row per assigned train pitcher: matched
    pitcher_trackman_id, assignment cost, and a margin (assigned cost vs
    best cost among all *other* trackman candidates in the group, i.e. a
    runner-up gap computed independently of the global assignment)."""
    n_t, n_m = len(train_g), len(tm_g)
    if n_t == 0 or n_m == 0:
        return pd.DataFrame(
            columns=["pitcher_id", "matched_pitcher_trackman_id", "cost", "margin"]
        )

    train_rank = train_g["n_pitches"].rank(pct=True).to_numpy()
    tm_rank = tm_g["n_pitches"].rank(pct=True).to_numpy()

    train_mix = train_g[["fastball_rate", "breaking_rate", "offspeed_rate"]].fillna(0).to_numpy()
    tm_mix = tm_g[["fastball_rate", "breaking_rate", "offspeed_rate"]].fillna(0).to_numpy()
    train_tier = train_g["major_rate"].fillna(0.5).to_numpy()
    tm_tier = tm_g["major_rate"].fillna(0.5).to_numpy()

    mix_dist = np.linalg.norm(train_mix[:, None, :] - tm_mix[None, :, :], axis=2)
    tier_dist = np.abs(train_tier[:, None] - tm_tier[None, :])
    rank_dist = np.abs(train_rank[:, None] - tm_rank[None, :])
    cost = w_mix * mix_dist + w_tier * tier_dist + w_rank * rank_dist

    row_idx, col_idx = linear_sum_assignment(cost)

    out = []
    for i, j in zip(row_idx, col_idx):
        others = np.delete(cost[i], j)
        margin = (others.min() - cost[i, j]) if len(others) else np.nan
        out.append(
            {
                "pitcher_id": train_g["pitcher_id"].iloc[i],
                "matched_pitcher_trackman_id": tm_g["pitcher_trackman_id"].iloc[j],
                "cost": cost[i, j],
                "margin": margin,
            }
        )
    return pd.DataFrame(out)


def match_pitchers_by_season(train_fp, trackman_fp):
    """Run `_match_one_group` independently for every (season, hand)
    group. Returns one row per (pitcher_id, season) that got assigned."""
    results = []
    for (season, hand), train_g in train_fp.groupby(["season", "hand"]):
        tm_g = trackman_fp[
            (trackman_fp["season"] == season) & (trackman_fp["hand"] == hand)
        ]
        matched = _match_one_group(train_g.reset_index(drop=True), tm_g.reset_index(drop=True))
        matched["season"] = season
        matched["hand"] = hand
        results.append(matched)
    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()


def consolidate_pitcher_mapping(season_matches, margin_high=0.15, margin_low=0.0):
    """Collapse per-season matches into one row per pitcher_id: the
    across-season majority-vote trackman id, agreement rate, and a
    confidence tier.

    Confidence tiers:
    - high: >=2 seasons matched AND 100% cross-season agreement, OR
      exactly 1 season matched with a large margin (>= margin_high).
    - medium: majority agreement >=60% across seasons (some seasons
      disagree), or a single-season match with a small positive margin.
    - low: no clear majority, or the winning candidate's margin is
      non-positive (a near-tie / ambiguous single-season match).
    """
    rows = []
    for pid, g in season_matches.groupby("pitcher_id"):
        vote = g["matched_pitcher_trackman_id"].value_counts()
        winner = vote.index[0]
        agreement = vote.iloc[0] / len(g)
        n_seasons = len(g)
        avg_margin = g.loc[g["matched_pitcher_trackman_id"] == winner, "margin"].mean()

        if n_seasons >= 2 and agreement == 1.0:
            tier = "high"
        elif n_seasons == 1 and avg_margin >= margin_high:
            tier = "high"
        elif agreement >= 0.6 or (n_seasons == 1 and avg_margin > margin_low):
            tier = "medium"
        else:
            tier = "low"

        rows.append(
            {
                "pitcher_id": pid,
                "matched_pitcher_trackman_id": winner,
                "n_seasons_matched": n_seasons,
                "season_agreement_rate": agreement,
                "avg_margin": avg_margin,
                "confidence": tier,
            }
        )
    return pd.DataFrame(rows)


# --- 2-B. Row-level matching -------------------------------------------------


def order_consistency_check(train_match_keys, trackman_clean, pitcher_mapping, min_confidence="high"):
    """Sanity check for the "both files preserve original chronological
    order" assumption behind rank-based disambiguation. Restricted to
    pitchers whose identity match is already high-confidence: within
    each such pitcher, take rows whose situational_key is globally
    unique on BOTH sides (no disambiguation needed, so this is an
    independent check, not circular), rank them by train row_id and by
    trackman trackman_id, and report the Spearman correlation between
    the two rank sequences pooled across those pitchers."""
    keep_pids = set(
        pitcher_mapping.loc[pitcher_mapping["confidence"].isin(
            [min_confidence] if isinstance(min_confidence, str) else min_confidence
        ), "pitcher_id"]
    )
    pid_to_tmid = dict(
        zip(pitcher_mapping["pitcher_id"], pitcher_mapping["matched_pitcher_trackman_id"])
    )

    all_train_ranks, all_tm_ranks = [], []
    for pid in keep_pids:
        tmid = pid_to_tmid[pid]
        t = train_match_keys.loc[train_match_keys["pitcher_id"] == pid, ["row_id", "situational_key"]]
        m = trackman_clean.loc[
            trackman_clean["pitcher_trackman_id"] == tmid, ["trackman_id", "situational_key"]
        ]
        t_unique = t[~t["situational_key"].duplicated(keep=False)]
        m_unique = m[~m["situational_key"].duplicated(keep=False)]
        merged = t_unique.merge(m_unique, on="situational_key", how="inner")
        if len(merged) < 2:
            continue
        all_train_ranks.append(merged["row_id"].rank().to_numpy())
        all_tm_ranks.append(merged["trackman_id"].rank().to_numpy())

    if not all_train_ranks:
        return {"n_pitchers": 0, "n_row_pairs": 0, "spearman_r": np.nan}

    from scipy.stats import spearmanr

    n_pairs = sum(len(a) for a in all_train_ranks)
    # per-pitcher rank correlation, pooled by weighted average (weight =
    # pair count) -- avoids one high-volume pitcher dominating a naive
    # global concat, since global concat would mix independent per-
    # pitcher rank scales.
    corrs, weights = [], []
    for tr, mr in zip(all_train_ranks, all_tm_ranks):
        if len(tr) >= 3 and np.std(tr) > 0 and np.std(mr) > 0:
            r, _ = spearmanr(tr, mr)
            corrs.append(r)
            weights.append(len(tr))
    pooled = float(np.average(corrs, weights=weights)) if corrs else np.nan
    return {
        "n_pitchers": len(all_train_ranks),
        "n_row_pairs": n_pairs,
        "n_pitchers_with_corr": len(corrs),
        "spearman_r": pooled,
    }


# --- 2-A/2-B v2: bottom-up joint-key matching ------------------------------
#
# The v1 approach above (season-fingerprint identity guess, then situational
# row matching *within* the guessed identity) turned out to have weak
# discriminating power: a season-level fingerprint (one pitch-mix snapshot +
# team-tier rate + workload rank) isn't sharp enough to pick 1 correct
# candidate out of ~250-350 same-season-same-hand pitchers, so most pitchers
# (63%) ended up "low confidence" and were dropped before ever reaching row
# matching.
#
# v2 flips the order: match ROWS first, directly, using every column both
# files share with directly-comparable values -- situational_key (season/
# month/dayofweek/inning/top_bottom/count state) *plus* team tier (R/F <->
# major/minor) *plus* pitcher_hand *plus* batter_hand, all combined into one
# key. Pitcher identity is then *induced* from which (pitcher_id,
# pitcher_trackman_id) pairs co-occur across many such row matches, rather
# than being guessed first from noisy aggregates.
#
# Two-step, not one, because a joint-key group with more than 1 row on
# either side can mix rows from *different* real pitchers/games that happen
# to share the same coarse context (e.g. every Monday in April 2022, top of
# the 3rd, 1-1 count, RHP vs RHB, major tier -- plausible across many
# distinct games) -- unlike v1's row-matching step, which only ever compared
# rows already restricted to one *known* pitcher, so rank-based positional
# pairing (same person's own chronological event stream) was a safe
# disambiguator there. It is not safe on a group that may span several
# different pitchers, so:
#   Step A (`match_rows_direct_unique`): keep ONLY joint-key groups that are
#     exactly 1-vs-1 on both sides -- a pure, assumption-free direct match.
#   Step B (`induce_pitcher_mapping`): aggregate Step A's matches into a
#     pitcher identity table (majority vote + cross-season consistency).
#   Step C: re-run `match_rows` (already defined above) with the Step B
#     identity table -- now safe to use rank-based disambiguation again,
#     since every group it looks at is restricted to one already-identified
#     pitcher's own event stream, recovering the coverage v1 lost.


def add_joint_match_key(df, hand_pitcher_col, hand_batter_col, tier_col, situational_key_col="situational_key"):
    df = df.copy()
    df["joint_match_key"] = (
        df[situational_key_col].astype(str)
        + "|" + df[tier_col].astype(str)
        + "|" + df[hand_pitcher_col].astype(str)
        + "|" + df[hand_batter_col].astype(str)
    )
    return df


def match_rows_direct_unique(train_match_keys, trackman_clean):
    """Step A: globally-unique joint-key row matches, no pre-established
    pitcher identity, no positional disambiguation (only 1-vs-1 groups are
    kept, so there is nothing to disambiguate)."""
    t = train_match_keys.copy()
    t["pitcher_hand_norm"] = t["pitcher_hand"].map(TRAIN_HAND_TO_TRACKMAN)
    t["batter_hand_norm"] = t["batter_hand"].map(TRAIN_HAND_TO_TRACKMAN)
    t = add_joint_match_key(t, "pitcher_hand_norm", "batter_hand_norm", "team_tier")

    m = trackman_clean.copy()
    m = add_joint_match_key(m, "pitcher_hand", "batter_hand", "pitcher_team_tier")

    t_n = t.groupby("joint_match_key")["row_id"].transform("size")
    m_n = m.groupby("joint_match_key")["trackman_id"].transform("size")
    t_unique = t[t_n == 1]
    m_unique = m[m_n == 1]

    m_slim = m_unique[["trackman_id", "pitcher_trackman_id", "joint_match_key", "is_illegal_count"]].rename(
        columns={"is_illegal_count": "trackman_is_illegal_count"}
    )
    merged = t_unique.merge(m_slim, on="joint_match_key", how="inner")
    return merged[
        [
            "row_id",
            "trackman_id",
            "pitcher_id",
            "pitcher_trackman_id",
            "season",
            "trackman_is_illegal_count",
        ]
    ].rename(columns={"pitcher_trackman_id": "matched_pitcher_trackman_id"})


def induce_pitcher_mapping(direct_matches, min_support=3):
    """Step B: aggregate Step-A direct row matches into a pitcher identity
    table. `purity` = the winning trackman id's share of that pitcher's
    total supporting rows (across all seasons pooled); `season_consistency`
    = share of the pitcher's *seasons* (each counted once) whose
    within-season majority pick agrees with the pooled winner.

    Confidence tiers:
    - high: >=min_support supporting rows, purity >= 0.9, and (only 1
      season present, or season_consistency == 1.0).
    - medium: >=min_support supporting rows and purity >= 0.7.
    - low: everything else (thin or inconsistent support).
    """
    rows = []
    for pid, g in direct_matches.groupby("pitcher_id"):
        vote = g["matched_pitcher_trackman_id"].value_counts()
        winner = vote.index[0]
        n_votes_total = len(g)
        purity = vote.iloc[0] / n_votes_total

        per_season_winner = g.groupby("season")["matched_pitcher_trackman_id"].agg(
            lambda s: s.value_counts().index[0]
        )
        n_seasons = len(per_season_winner)
        season_consistency = (per_season_winner == winner).mean()

        if n_votes_total >= min_support and purity >= 0.9 and (n_seasons == 1 or season_consistency == 1.0):
            tier = "high"
        elif n_votes_total >= min_support and purity >= 0.7:
            tier = "medium"
        else:
            tier = "low"

        rows.append(
            {
                "pitcher_id": pid,
                "matched_pitcher_trackman_id": winner,
                "n_votes_total": n_votes_total,
                "purity": purity,
                "n_seasons_in_support": n_seasons,
                "season_consistency": season_consistency,
                "confidence": tier,
            }
        )
    return pd.DataFrame(rows)


def match_rows_direct_unique_excluding(
    train_match_keys, trackman_clean, exclude_train_pitchers, exclude_trackman_pitchers
):
    """Same as `match_rows_direct_unique`, but restricted to train pitchers
    NOT already in `exclude_train_pitchers` and trackman pitchers NOT
    already in `exclude_trackman_pitchers`. Used for the iterative
    refinement below: once a batch of pitchers is confidently identified,
    removing their rows from the pool can un-hide new globally-unique
    joint-key matches for the remaining pitchers that were previously
    tied with an (already-resolved) row belonging to someone else."""
    t = train_match_keys[~train_match_keys["pitcher_id"].isin(exclude_train_pitchers)]
    m = trackman_clean[~trackman_clean["pitcher_trackman_id"].isin(exclude_trackman_pitchers)]
    return match_rows_direct_unique(t, m)


def induce_pitcher_mapping_iterative(train_match_keys, trackman_clean, n_rounds=3, min_support=3):
    """Repeats Step A (unique joint-key matching) + Step B (vote-based
    identity induction) up to `n_rounds` times, excluding already-resolved
    (high/medium confidence) pitchers from the pool each round. Returns
    the union of all rounds' pitcher mappings (one row per pitcher_id,
    kept from whichever round first resolved them) plus per-round
    diagnostics.
    """
    resolved = pd.DataFrame(columns=["pitcher_id", "matched_pitcher_trackman_id", "confidence"])
    round_logs = []
    excl_train, excl_tm = set(), set()

    for r in range(1, n_rounds + 1):
        direct = match_rows_direct_unique_excluding(train_match_keys, trackman_clean, excl_train, excl_tm)
        if len(direct) == 0:
            round_logs.append({"round": r, "n_direct_rows": 0, "n_new_confident": 0})
            break
        mapping_r = induce_pitcher_mapping(direct, min_support=min_support)
        new_confident = mapping_r[mapping_r["confidence"].isin(["high", "medium"])]
        round_logs.append(
            {
                "round": r,
                "n_direct_rows": len(direct),
                "n_pitchers_in_pool": direct["pitcher_id"].nunique(),
                "n_new_confident": len(new_confident),
            }
        )
        if len(new_confident) == 0:
            break
        resolved = pd.concat([resolved, new_confident], ignore_index=True)
        excl_train |= set(new_confident["pitcher_id"])
        excl_tm |= set(new_confident["matched_pitcher_trackman_id"])

    return resolved, pd.DataFrame(round_logs)


def match_rows(train_match_keys, trackman_clean, pitcher_mapping, confidences=("high", "medium")):
    """2-B row-level matching for pitchers whose identity match is in
    `confidences`. Returns a DataFrame with one row per matched train
    row_id: `trackman_id`, `pitcher_confidence` (from pitcher_mapping),
    and `row_confidence` ("high" = unique on both sides within the
    (pitcher, situational_key) group, "medium" = disambiguated by
    matching same-rank position after sorting each side by its own
    native ascending id)."""
    keep = pitcher_mapping[pitcher_mapping["confidence"].isin(confidences)]
    pid_to_tmid = dict(zip(keep["pitcher_id"], keep["matched_pitcher_trackman_id"]))
    pid_to_conf = dict(zip(keep["pitcher_id"], keep["confidence"]))

    t = train_match_keys[train_match_keys["pitcher_id"].isin(pid_to_tmid)].copy()
    t["matched_pitcher_trackman_id"] = t["pitcher_id"].map(pid_to_tmid)
    t["pitcher_confidence"] = t["pitcher_id"].map(pid_to_conf)

    m = trackman_clean[
        trackman_clean["pitcher_trackman_id"].isin(set(pid_to_tmid.values()))
    ][["trackman_id", "pitcher_trackman_id", "situational_key", "is_illegal_count"]].copy()

    # group size on each side (for row_confidence classification)
    t["_t_group_n"] = t.groupby(["matched_pitcher_trackman_id", "situational_key"])[
        "row_id"
    ].transform("size")
    m["_m_group_n"] = m.groupby(["pitcher_trackman_id", "situational_key"])[
        "trackman_id"
    ].transform("size")

    # rank within (pitcher, situational_key) group, sorted by each side's
    # own native ascending id -- this is the positional-disambiguation key.
    t = t.sort_values(["matched_pitcher_trackman_id", "situational_key", "row_id"])
    t["_rank"] = t.groupby(["matched_pitcher_trackman_id", "situational_key"]).cumcount()
    m = m.sort_values(["pitcher_trackman_id", "situational_key", "trackman_id"])
    m["_rank"] = m.groupby(["pitcher_trackman_id", "situational_key"]).cumcount()

    merged = t.merge(
        m,
        left_on=["matched_pitcher_trackman_id", "situational_key", "_rank"],
        right_on=["pitcher_trackman_id", "situational_key", "_rank"],
        how="inner",
        suffixes=("", "_tm"),
    )
    merged["row_confidence"] = np.where(
        (merged["_t_group_n"] == 1) & (merged["_m_group_n"] == 1), "high", "medium"
    )

    return merged[
        [
            "row_id",
            "trackman_id",
            "pitcher_id",
            "matched_pitcher_trackman_id",
            "pitcher_confidence",
            "row_confidence",
            "is_illegal_count",
        ]
    ].rename(columns={"is_illegal_count": "trackman_is_illegal_count"})
