"""Weighted probability blend: candidate selection + coarse->fine weight
search, evaluated only on already-computed validation predictions (never
re-fits a model, never touches test.csv) — doc sections 16-17.
"""

import numpy as np

from metrics import official_score as _default_official_score


def select_blend_candidates(comparison_df, corr_df, top_k=3, corr_threshold=0.98,
                             exclude=("Mean",)):
    """Greedily pick up to top_k models: highest Official_Score first,
    skipping any whose correlation with an already-selected candidate
    exceeds corr_threshold. If fewer than top_k survive that filter,
    backfill with the next-highest-score models regardless of
    correlation, so we never end up with <2 candidates to blend."""
    pool = comparison_df[
        (~comparison_df["Model"].isin(exclude)) & (comparison_df["status"] == "ok")
    ].sort_values("Official_Score", ascending=False)
    ordered = list(pool["Model"])

    selected = []
    for name in ordered:
        if len(selected) >= top_k:
            break
        if all(corr_df.loc[name, s] <= corr_threshold for s in selected):
            selected.append(name)

    if len(selected) < min(top_k, len(ordered)):
        for name in ordered:
            if name not in selected:
                selected.append(name)
            if len(selected) >= top_k:
                break

    return selected[:top_k]


def blend_predict(pred_dict, weights):
    total = np.zeros_like(next(iter(pred_dict.values())), dtype=float)
    for name, w in weights.items():
        total = total + w * np.asarray(pred_dict[name], dtype=float)
    return total


def _simplex_grid(n, step):
    """All n-tuples of non-negative multiples of `step` summing to 1."""
    levels = int(round(1 / step))

    def gen(k, remaining):
        if k == 1:
            yield (remaining,)
            return
        for i in range(remaining + 1):
            for rest in gen(k - 1, remaining - i):
                yield (i,) + rest

    for combo in gen(n, levels):
        w = tuple(c * step for c in combo)
        assert abs(sum(w) - 1.0) < 1e-9
        yield w


def coarse_fine_blend_search(pred_dict, y_val, candidates,
                              coarse_step=0.05, fine_step=0.01, fine_radius=0.05,
                              official_score_fn=None):
    """Stage 1: full simplex grid at coarse_step over `candidates`.
    Stage 2: full simplex grid at fine_step, filtered to points within
    fine_radius (per dimension) of the coarse optimum. Returns
    (best_weights: dict, best_brier, best_score)."""
    score_fn = official_score_fn or _default_official_score
    n = len(candidates)
    assert n >= 1, "need at least one blend candidate"

    def evaluate(w_tuple):
        weights = dict(zip(candidates, w_tuple))
        pred = blend_predict(pred_dict, weights)
        return score_fn(pred, y_val)  # (brier, score)

    if n == 1:
        brier, score = evaluate((1.0,))
        return {candidates[0]: 1.0}, brier, score

    best_score, best_brier, best_w = -1.0, None, None
    for w in _simplex_grid(n, coarse_step):
        brier, score = evaluate(w)
        if score > best_score:
            best_score, best_brier, best_w = score, brier, w
    coarse_w = best_w

    for w in _simplex_grid(n, fine_step):
        if all(abs(w[i] - coarse_w[i]) <= fine_radius + 1e-9 for i in range(n)):
            brier, score = evaluate(w)
            if score > best_score:
                best_score, best_brier, best_w = score, brier, w

    return dict(zip(candidates, best_w)), best_brier, best_score
