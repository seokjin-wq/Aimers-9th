"""exp_022 -- season base-rate drift found: control_success rate falls
steadily every season (2019=0.565 -> 2024=0.486, see
`experiments/exp_022_recency_calibration.md`). exp_018/019's Platt
calibrator was fit ONLY on 2019-2023 OOF, so it reflects that period's
(higher) pooled rate; a diagnostic showed the raw champion's mean
prediction on 2024 (0.4962) overshoots 2024's true rate (0.4861) by
+1.01pp, and Platt only partially closes this (0.4936, still +0.75pp
over) -- the older-period calibrator doesn't fully track the downward
drift. If 2025 continues the trend, the real evaluation set's rate is
probably even lower than 2024's, so this residual is probably WORSE for
2025 than what we can measure on 2024.

Key insight enabling a cheap, valid test: the actual champion's 2024
predictions (val_pred_42/val_pred_1, cached) come from CatBoost models
trained ONLY on 2019-2023 -- they are already genuinely out-of-sample
for 2024, exactly like the 2019-2023 OOF is out-of-sample for its own
period. So (pred, y) pairs from 2024 can be added directly to the
calibrator's training set with NO further CatBoost retraining needed;
this script only needs numpy/sklearn on already-cached arrays.

To test honestly (not circularly) whether including/weighting 2024 in
calibration training improves generalization, this does a 5-fold CV
purely within the 2024 (pred, y) pairs: fit candidate calibrators on
[2019-2023 OOF] + [the other 4/5 of 2024], evaluate on the held-out 1/5
of 2024, and compare against the exp_019 baseline (fit on 2019-2023 OOF
only) evaluated on the same held-out fold.
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

from calibration import fit_platt, apply_platt
from metrics import official_score

DATA_DIR = "./data"
OOF_CACHE_SEED42 = "./output/exp018_oof_cache.npz"
OOF_CACHE_SEED1 = "./output/exp019_oof_seed1_cache.npz"
VAL_PRED_CACHE_SEED42 = "./output/exp018_champion_val_pred_cache.npy"
VAL_PRED_CACHE_SEED1 = "./output/exp019_champion_val_pred_seed1_cache.npy"
KFOLD_SEED = 42
N_FOLDS = 5
WEIGHT_GRID = [12, 20, 30, 50, 80, 150, 300, 1000]


def fit_platt_weighted(raw_pred, y, sample_weight=None, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y, sample_weight=sample_weight)
    return clf


def main():
    print("=" * 80)
    print("0. 시즌별 base rate 확인 (드리프트 재확인)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=["season", "control_success"])
    season_r = train.groupby("season")["control_success"].mean()
    print(season_r)
    seasons = season_r.index.to_numpy().astype(float)
    rates = season_r.to_numpy()
    slope, intercept = np.polyfit(seasons, rates, 1)
    r_2025_extrap = slope * 2025 + intercept
    print(f"\n선형 추세 기울기={slope:.5f}/season, 2025 외삽 예상 rate={r_2025_extrap:.4f}")

    print()
    print("=" * 80)
    print("1. 데이터 준비 -- 2019-2023 OOF(캐시) + 2024 실제 예측(캐시, 이미 held-out)")
    print("=" * 80)
    npz42 = np.load(OOF_CACHE_SEED42)
    npz1 = np.load(OOF_CACHE_SEED1)
    oof_2319 = (npz42["pred"] + npz1["pred"]) / 2
    y_2319 = npz42["y"]
    print(f"2019-2023 OOF: n={len(oof_2319)}")

    val_pred_42 = np.load(VAL_PRED_CACHE_SEED42)
    val_pred_1 = np.load(VAL_PRED_CACHE_SEED1)
    val_pred_2024 = (val_pred_42 + val_pred_1) / 2
    train_full = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=["season", "control_success"])
    y_2024 = train_full.loc[train_full["season"] == 2024, "control_success"].to_numpy()
    assert len(val_pred_2024) == len(y_2024)
    print(f"2024 실제 예측(이미 held-out): n={len(val_pred_2024)}")
    print(f"raw 2024 예측 평균={val_pred_2024.mean():.4f} vs 실제 2024 rate={y_2024.mean():.4f} (gap={val_pred_2024.mean()-y_2024.mean():+.4f})")

    print()
    print("=" * 80)
    print("2. 5-fold CV 순수 2024 내부에서 -- '2024를 보정기 학습에 포함하면 도움되는가?'")
    print("=" * 80)
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=KFOLD_SEED)
    idx_2024 = np.arange(len(val_pred_2024))

    baseline_scores = []
    variant_scores = {w: [] for w in WEIGHT_GRID}
    only2024_scores = []
    for fold, (tr_idx, ho_idx) in enumerate(kf.split(idx_2024)):
        p_tr_2024, y_tr_2024 = val_pred_2024[tr_idx], y_2024[tr_idx]
        p_ho_2024, y_ho_2024 = val_pred_2024[ho_idx], y_2024[ho_idx]

        platt_baseline = fit_platt(oof_2319, y_2319, seed=42)
        brier_b, score_b = official_score(apply_platt(platt_baseline, p_ho_2024), y_ho_2024)
        baseline_scores.append(score_b)

        for w in WEIGHT_GRID:
            p_combo = np.concatenate([oof_2319, p_tr_2024])
            y_combo = np.concatenate([y_2319, y_tr_2024])
            sw = np.concatenate([np.ones(len(oof_2319)), np.full(len(p_tr_2024), float(w))])
            platt_w = fit_platt_weighted(p_combo, y_combo, sample_weight=sw, seed=42)
            _, score_w = official_score(apply_platt(platt_w, p_ho_2024), y_ho_2024)
            variant_scores[w].append(score_w)

        platt_only2024 = fit_platt(p_tr_2024, y_tr_2024, seed=42)
        _, score_only2024 = official_score(apply_platt(platt_only2024, p_ho_2024), y_ho_2024)
        only2024_scores.append(score_only2024)

        print(f"  fold {fold+1}/{N_FOLDS}: baseline(2019-2023-only)={score_b:.2f}, "
              + ", ".join(f"w={w}:{variant_scores[w][-1]:.2f}" for w in WEIGHT_GRID)
              + f", 2024-only:{score_only2024:.2f}")

    print()
    print("=" * 80)
    print("요약 (fold 평균, 기준: 2019-2023-only 보정기)")
    print("=" * 80)
    base_mean = np.mean(baseline_scores)
    print(f"baseline(2019-2023 OOF만): fold평균 score={base_mean:.2f}")
    for w in WEIGHT_GRID:
        m = np.mean(variant_scores[w])
        print(f"2024 포함(weight={w}): fold평균 score={m:.2f} | Δ={m-base_mean:+.2f}")
    only2024_mean = np.mean(only2024_scores)
    print(f"2024-only(2019-2023 OOF 전혀 미사용): fold평균 score={only2024_mean:.2f} | Δ={only2024_mean-base_mean:+.2f}")

    best_w = max(WEIGHT_GRID, key=lambda w: np.mean(variant_scores[w]))
    print(f"\n최선 weight={best_w} (fold평균 score={np.mean(variant_scores[best_w]):.2f})")

    print("\n완료.")


if __name__ == "__main__":
    main()
