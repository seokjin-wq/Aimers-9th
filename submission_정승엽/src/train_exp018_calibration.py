"""exp_018 step 2 -- leak-safe recalibration test. 5-fold cross-fit
WITHIN 2019-2023 using the champion's exact model/features/
hyperparameters to get out-of-fold predictions (fixes exp_006's design
flaw: its calibrator was fit on a weaker, differently-configured
sub-model's predictions, an intentional architecture mismatch it
flagged as a risk). Those OOF (pred, y) pairs fit three calibrators:
  1. odds-power (user's proposal, derived formula): p' = p^k/(p^k+(1-p)^k)
     -- grid-searched over k, selected by OOF Brier (not assumed).
  2. Platt (src/calibration.fit_platt)
  3. Isotonic (src/calibration.fit_isotonic)
All three + raw are then applied to the REAL champion's 2024 predictions
(the actual model trained on the full 2019-2023, exactly like every
other exp_0XX validation script) -- 2024 labels are never touched by
calibrator fitting.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

from calibration import fit_platt, apply_platt, fit_isotonic, apply_isotonic
from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRUNK_COLS,
    POST_SHRINKAGE_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)
from metrics import official_score
from trackman_pitcher_features import (
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
SEED = 42
N_FOLDS = 5
K_GRID = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0]
OOF_CACHE = "./output/exp018_oof_cache.npz"
VAL_PRED_CACHE = "./output/exp018_champion_val_pred_cache.npy"

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS

CB_PARAMS = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=SEED, thread_count=-1, verbose=False,
)


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def odds_power(p, k):
    p = np.clip(np.asarray(p, dtype=float), 1e-9, 1 - 1e-9)
    pk = p**k
    return pk / (pk + (1 - p) ** k)


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    is_val = train["season"] == 2024
    train_only = train.loc[~is_val]
    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, val_priors_recent)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    train_2319 = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET + [TARGET]].reset_index(drop=True)
    X_2319 = train_2319[TRACKMAN_FEATURE_SET]
    y_2319 = train_2319[TARGET].to_numpy()

    print()
    print("=" * 80)
    print(f"1. {N_FOLDS}-fold cross-fit (2019-2023, 챔피언과 동일 설정) -> OOF 예측")
    print("=" * 80)
    if os.path.exists(OOF_CACHE):
        npz = np.load(OOF_CACHE)
        oof_pred, oof_y = npz["pred"], npz["y"]
        print(f"캐시에서 로드: {OOF_CACHE}")
    else:
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        oof_pred = np.zeros(len(train_2319))
        t0 = time.time()
        for fold, (tr_idx, ho_idx) in enumerate(kf.split(train_2319)):
            X_tr, y_tr = X_2319.iloc[tr_idx], y_2319[tr_idx]
            X_ho = X_2319.iloc[ho_idx]
            train_pool = cb.Pool(X_tr, y_tr, cat_features=CAT_COLS)
            clf = cb.CatBoostClassifier(**CB_PARAMS)
            clf.fit(train_pool, verbose=False)
            oof_pred[ho_idx] = clf.predict_proba(X_ho)[:, 1]
            print(f"  fold {fold+1}/{N_FOLDS} 완료 ({time.time()-t0:.1f}s 누적)")
        oof_y = y_2319
        os.makedirs("./output", exist_ok=True)
        np.savez(OOF_CACHE, pred=oof_pred, y=oof_y)
        print(f"저장(캐시): {OOF_CACHE}")

    oof_brier, oof_score = official_score(oof_pred, oof_y)
    print(f"OOF(2019-2023, 참고용): Brier={oof_brier:.6f}, score={oof_score:.2f}")

    print()
    print("=" * 80)
    print("2. 보정기 학습 (OOF에서만, 2024 미사용)")
    print("=" * 80)
    print("--- odds-power: OOF에서 k 그리드서치 (Brier 최소화) ---")
    best_k, best_k_brier = None, float("inf")
    for k in K_GRID:
        p = odds_power(oof_pred, k)
        brier, score = official_score(p, oof_y)
        marker = ""
        if brier < best_k_brier:
            best_k_brier, best_k = brier, k
            marker = "  <- 현재 최선"
        print(f"  k={k}: OOF Brier={brier:.6f} | OOF score={score:.2f}{marker}")
    print(f"선택된 k={best_k} (OOF Brier={best_k_brier:.6f})")

    print("\n--- Platt / Isotonic: OOF로 fit ---")
    platt = fit_platt(oof_pred, oof_y, seed=SEED)
    iso = fit_isotonic(oof_pred, oof_y)

    print()
    print("=" * 80)
    print("3. 챔피언 실제 2024 예측에 적용 (raw vs odds-power vs Platt vs Isotonic)")
    print("=" * 80)
    if not os.path.exists(VAL_PRED_CACHE):
        raise SystemExit(f"{VAL_PRED_CACHE} 없음 -- 먼저 reports/score_ceiling_analysis/run_calibration_diagnostic.py 실행 필요")
    val_pred = np.load(VAL_PRED_CACHE)
    is_val2 = train["season"] == 2024
    y_val = train.loc[is_val2, TARGET].to_numpy()
    assert len(val_pred) == len(y_val)

    variants = {
        "raw(무보정)": val_pred,
        f"odds-power(k={best_k})": odds_power(val_pred, best_k),
        "Platt": apply_platt(platt, val_pred),
        "Isotonic": apply_isotonic(iso, val_pred),
    }
    results = {}
    for name, p in variants.items():
        brier, score = official_score(p, y_val)
        results[name] = (brier, score)
        print(f"[{name}] Brier={brier:.6f} | score={score:.2f}")

    baseline_score = results["raw(무보정)"][1]
    print()
    print("=" * 80)
    print("요약 (기준: raw 챔피언)")
    print("=" * 80)
    for name, (brier, score) in results.items():
        print(f"{name}: score={score:.2f} | Δ vs raw={score-baseline_score:+.2f}")
    best_name = max(results, key=lambda n: results[n][1])
    if results[best_name][1] > baseline_score:
        print(f"\n최선: {best_name} (score={results[best_name][1]:.2f}) -- raw보다 개선")
    else:
        print(f"\n보정 개선 없음 -- raw(무보정)이 전 방식보다 우세 (exp_006과 같은 결론)")

    print("\n완료.")


if __name__ == "__main__":
    main()
