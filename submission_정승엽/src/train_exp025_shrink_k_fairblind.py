"""exp_025 -- re-tune TRACKMAN_SHRINK_K under the FAIR BLIND backtest
condition discovered in exp_024 (trackman tables built from
season<target_season only, so season-2024 validation rows are forced
onto the sentinel exactly like real season-2025 submission rows will
be -- no benefit from real in-season 2024 Trackman data that won't
exist for 2025).

exp_021 already grid-searched this k under the OPTIMISTIC condition
(season 2024 validation rows resolving through real in-season 2024
Trackman history) and found k=50 already near-optimal, all differences
<2 local points (noise). That earlier sweep is not necessarily valid
for the blind condition, since the blind condition is what ACTUALLY
governs real 2025 inference -- worth one targeted re-check before
concluding this axis really is flat.

Reuses `build_flat_blind_tables`/`evaluate_variant` from
`train_exp024_trend_trackman.py` unchanged (variant A there = flat
sentinel, exactly the production method), just sweeping shrink_k.
Single seed=42, sequential grid, no CatBoost retraining beyond what
this sweep itself runs.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import pandas as pd

from features import build_features
from trackman_pitcher_features import load_pitcher_mapping
from train_exp024_trend_trackman import build_flat_blind_tables, evaluate_variant, VAL_SEASON, ID, TARGET

DATA_DIR = "./data"
K_GRID = [20, 35, 50, 75, 100, 150, 250, 400]


def main():
    test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
    base_features = [c for c in test_cols if c != ID]
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=base_features + [TARGET])
    train = build_features(train)
    is_val = train["season"] == VAL_SEASON

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables_flat = build_flat_blind_tables(trackman_clean, VAL_SEASON)

    print("=" * 80)
    print(f"TRACKMAN_SHRINK_K 재튜닝 (fair-blind 조건, k in {K_GRID})")
    print("=" * 80)
    results = {}
    for k in K_GRID:
        import train_exp024_trend_trackman as m
        m.TRACKMAN_SHRINK_K = k
        t = time.time()
        brier, score, _ = evaluate_variant(f"k={k}", tables_flat, train, is_val, pitcher_mapping)
        results[k] = (brier, score)
        print(f"  -> k={k}: score={score:.2f} ({time.time()-t:.1f}s)")

    print()
    print("=" * 80)
    print("요약")
    print("=" * 80)
    best_k = max(results, key=lambda k: results[k][1])
    for k in K_GRID:
        brier, score = results[k]
        marker = "  <- 최선" if k == best_k else ""
        print(f"k={k}: Brier={brier:.6f} | score={score:.2f}{marker}")
    print(f"\n기준(k=50, production 값): score={results[50][1]:.2f}")
    print(f"최선: k={best_k}, score={results[best_k][1]:.2f}, Δ vs k=50 = {results[best_k][1]-results[50][1]:+.2f}")


if __name__ == "__main__":
    main()
