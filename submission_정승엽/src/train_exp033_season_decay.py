"""exp_033 -- training-time sample-weight decay by season recency,
swept on exp_030's exact architecture (single CatBoost, exp_030's
hyperparams; production would still 2-seed-bag whichever decay wins).
See experiments/exp_033_season_decay.md.
"""

import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
from sklearn.linear_model import LogisticRegression

from exp030_baseline import build_holdout_split
from features import CAT_COLS
from metrics import official_score
from model_factory import fit_catboost

DECAY_GRID = [0.80, 0.85, 0.90, 1.0]


def fit_platt_weighted(raw_pred, y, sample_weight=None, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y, sample_weight=sample_weight)
    return clf


def approx_calibrated_score(raw_val_pred, y_val):
    """Same screening approximation as exp_031 (fit Platt directly on
    2024, not full OOF) -- see that script's docstring for the caveat."""
    calibrator = fit_platt_weighted(raw_val_pred, y_val.to_numpy())
    calibrated = calibrator.predict_proba(np.asarray(raw_val_pred).reshape(-1, 1))[:, 1]
    return official_score(calibrated, y_val)


def main():
    print("=" * 80)
    print("0. 데이터/피처 구축 (exp_030과 동일 105피처, exp030_baseline 공용 헬퍼)")
    print("=" * 80)
    X_train, y_train, X_val, y_val, _ = build_holdout_split()
    # season은 이미 exp_030의 105피처 중 하나(공식 원본 컬럼)라 extra_cols
    # 없이 바로 접근 가능.
    assert list(X_train.columns).count("season") == 1
    train_season = X_train["season"].to_numpy()
    max_season = train_season.max()  # 2023, train split 자체의 최댓값 -- 누수 없음
    print(f"train={X_train.shape}, val={X_val.shape}, max_season(train)={max_season}")

    results = {}
    for decay in DECAY_GRID:
        print()
        print("=" * 80)
        print(f"decay={decay}")
        print("=" * 80)
        weight = None if decay == 1.0 else np.power(decay, max_season - train_season)
        t = time.time()
        res = fit_catboost(X_train, y_train, X_val, y_val, CAT_COLS, seed=42,
                            sample_weight=weight, name=f"CatBoost-decay{decay}")
        print(f"완료: {time.time()-t:.1f}s, best_iter={res.extra['best_iteration']}")
        raw_brier, raw_score = official_score(res.val_pred, y_val)
        cal_brier, cal_score = approx_calibrated_score(res.val_pred, y_val)
        print(f"  raw: Brier={raw_brier:.6f} score={raw_score:.2f}")
        print(f"  근사보정: Brier={cal_brier:.6f} score={cal_score:.2f}")
        results[decay] = (raw_score, cal_score)

    print()
    print("=" * 80)
    print("결과 요약 (근사보정 기준, exp_030_repro 875.00과 직접 비교는 exp_037에서 재검증)")
    print("=" * 80)
    for decay, (raw_score, cal_score) in results.items():
        marker = " <- null case(현재 exp_030과 동일)" if decay == 1.0 else ""
        print(f"  decay={decay}: raw={raw_score:.2f}  근사보정={cal_score:.2f}{marker}")
    best_decay = max(results, key=lambda d: results[d][1])
    print(f"\n최선(근사보정 기준): decay={best_decay}, score={results[best_decay][1]:.2f}")
    print("완료.")


if __name__ == "__main__":
    main()
