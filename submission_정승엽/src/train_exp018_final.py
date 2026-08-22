"""exp_018 final -- retrain the exp_010 champion (seeds {42, 1}, full
2019-2024) exactly like train_exp010_final.py, and additionally attach
a Platt calibrator as a generic post-hoc step (submission/script.py's
new `meta["calibrator"]` mechanism). The Platt calibrator is refit here
(fast, <1s) from the ALREADY-CACHED 2019-2023 5-fold OOF predictions
(`output/exp018_oof_cache.npz`, produced by train_exp018_calibration.py)
rather than re-running a fresh 5-fold cross-fit on the full 2019-2024
data -- a deliberate simplification: Platt scaling only has 2 free
parameters (slope + intercept on the logit), which are already very
precisely estimated from 1.22M OOF points, so re-deriving OOF over the
slightly larger 2019-2024 set (another ~100+ minute 5-fold cross-fit)
would cost a lot for essentially no expected precision gain.

Local validation of this exact combo (2-seed average + this same OOF-fit
Platt calibrator): experiments/exp_018_calibration_recheck.md,
`src/train_exp018_check_seedbag.py` -- score 769.12 (Brier 0.247886),
the best result this session.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import joblib
import numpy as np
import pandas as pd

from calibration import fit_platt
from features import CAT_COLS, DERIVED_COLS, SHRUNK_COLS, POST_SHRINKAGE_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    build_test_time_pitcher_lookup,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
SEED_ITERS = {42: 696, 1: 632}  # exp010_run_log.txt val best_iter+1
OOF_CACHE = "./output/exp018_oof_cache.npz"

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    if not os.path.exists(OOF_CACHE):
        raise SystemExit(f"{OOF_CACHE} 없음 -- 먼저 src/train_exp018_calibration.py 실행 필요")
    npz = np.load(OOF_CACHE)
    oof_pred, oof_y = npz["pred"], npz["y"]
    platt = fit_platt(oof_pred, oof_y, seed=42)
    print(f"Platt 보정기 재학습 완료 (OOF n={len(oof_pred)}, 캐시 재사용)")

    print("=" * 80)
    print("1. 전체 2019-2024 데이터 + 피처 구축")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    final_priors = fit_shrinkage_priors(recent_seasons_df(train))
    train_shrunk = apply_shrinkage(train, final_priors)
    train_final = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    train_pool = cb.Pool(train_final[ALL_FEATURES], train_final[TARGET], cat_features=CAT_COLS)

    print()
    print("=" * 80)
    print("2. 시드별 전체 재학습")
    print("=" * 80)
    os.makedirs(MODEL_DIR, exist_ok=True)
    seed_model_files = []
    for seed, iters in SEED_ITERS.items():
        cb_params = dict(
            iterations=iters, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=seed, thread_count=-1, verbose=200,
        )
        clf = cb.CatBoostClassifier(**cb_params)
        t = time.time()
        clf.fit(train_pool)
        print(f"[seed={seed}] 완료 :: {time.time() - t:.1f}s")
        fname = f"catboost_model_seed{seed}.cbm"
        clf.save_model(os.path.join(MODEL_DIR, fname))
        seed_model_files.append(fname)

    print()
    print("=" * 80)
    print("3. 저장")
    print("=" * 80)
    lookup, league_fallback = build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({lookup.shape})")

    for stale in ["catboost_model.cbm", "lgbm_booster.txt"]:
        p = os.path.join(MODEL_DIR, stale)
        if os.path.exists(p):
            os.remove(p)
            print(f"제거: {p} (이전 실험 아티팩트 정리)")

    joblib.dump(
        {
            "model_type": "catboost_seedbag",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "trackman_cols": TRACKMAN_PITCHER_ASOF_COLS,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
            "trackman_league_fallback": league_fallback,
            "trackman_shrink_k": TRACKMAN_SHRINK_K,
            "seed_model_files": seed_model_files,
            "calibrator": platt,
            "exp_id": "exp_018_calibrated_seedbag42_1",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: model_meta.pkl (seed_model_files={seed_model_files}, calibrator=Platt)")
    print("\n완료.")


if __name__ == "__main__":
    main()
