"""exp_018 step 1 -- calibration diagnostic for the champion (exp_010's
seed=42 single model, reproduced here; same features/hyperparameters as
every exp_007-derived script). NOT a new model -- just measures:
  (a) 0.5-threshold "accuracy" (user-requested, but only a supplementary
      stat -- Brier score cares about probability accuracy, not sign
      accuracy, so this alone can't tell us whether recalibration helps)
  (b) the real diagnostic: per-decile calibration_bins/expected_
      calibration_error (metrics.py) -- does mean_prediction actually
      diverge from actual_success_rate in any bucket, and in which
      direction?
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import catboost as cb
import numpy as np
import pandas as pd

from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRUNK_COLS,
    POST_SHRINKAGE_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)
from metrics import calibration_bins, expected_calibration_error, official_score
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
PRED_CACHE = "./output/exp018_champion_val_pred_cache.npy"

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
TRACKMAN_FEATURE_SET = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


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

    X_train = train_shrunk.loc[~is_val, TRACKMAN_FEATURE_SET]
    y_train = train_shrunk.loc[~is_val, TARGET]
    X_val = train_shrunk.loc[is_val, TRACKMAN_FEATURE_SET]
    y_val = train_shrunk.loc[is_val, TARGET].to_numpy()

    print()
    print("=" * 80)
    print("1. 챔피언(seed=42) 재현 -- 캐시 있으면 재학습 생략")
    print("=" * 80)
    if os.path.exists(PRED_CACHE):
        pred = np.load(PRED_CACHE)
        print(f"캐시에서 로드: {PRED_CACHE}")
    else:
        cb_params = dict(
            iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
            loss_function="Logloss", eval_metric="Logloss",
            random_seed=SEED, thread_count=-1, verbose=False,
        )
        train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
        val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
        t = time.time()
        clf = cb.CatBoostClassifier(**cb_params)
        clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        pred = clf.predict_proba(X_val)[:, 1]
        print(f"학습 완료 :: {time.time()-t:.1f}s")
        os.makedirs("./output", exist_ok=True)
        np.save(PRED_CACHE, pred)
        print(f"저장(캐시): {PRED_CACHE}")

    brier, score = official_score(pred, y_val)
    print(f"[챔피언(seed=42) 재현] Brier={brier:.6f} | score={score:.2f}")
    print(f"예측 통계: mean={pred.mean():.4f} min={pred.min():.4f} max={pred.max():.4f}")

    print()
    print("=" * 80)
    print("2(a). 0.5-threshold 정답률 (참고용 보조지표)")
    print("=" * 80)
    pred_class = (pred >= 0.5).astype(int)
    acc = (pred_class == y_val).mean()
    n_pred_success = (pred_class == 1).sum()
    n_pred_fail = (pred_class == 0).sum()
    print(f"0.5 기준 정답률: {acc:.4f} ({acc*100:.2f}%)")
    print(f"  예측=성공(>=0.5)인 행: {n_pred_success} ({100*n_pred_success/len(pred):.1f}%), 그중 실제 성공률: {y_val[pred_class==1].mean():.4f}")
    print(f"  예측=실패(<0.5)인 행: {n_pred_fail} ({100*n_pred_fail/len(pred):.1f}%), 그중 실제 성공률: {y_val[pred_class==0].mean():.4f}")
    print("주의: 이 수치는 참고용 -- Brier score는 방향 정답 여부가 아니라 확률 자체의")
    print("정확도를 보는 지표라, 정답률이 높다고 무조건 보정이 도움된다는 뜻은 아님.")

    print()
    print("=" * 80)
    print("2(b). 실제 보정곡선 (진짜 근거) -- 10분위 구간별 평균예측 vs 실제성공률")
    print("=" * 80)
    bins = calibration_bins(pred, y_val, n_bins=10)
    print(bins.to_string(index=False))
    ece = expected_calibration_error(pred, y_val, n_bins=10)
    print(f"\nExpected Calibration Error (가중평균 |예측-실제|): {ece:.6f}")
    bins["gap"] = bins["mean_prediction"] - bins["actual_success_rate"]
    print("\n구간별 gap(예측-실제), 양수면 과신(overconfident), 음수면 과소평가(underconfident):")
    print(bins[["bin_lo", "bin_hi", "mean_prediction", "actual_success_rate", "gap", "sample_count"]].to_string(index=False))

    print("\n완료.")


if __name__ == "__main__":
    main()
