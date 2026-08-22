"""exp_031 -- heterogeneous ensemble test: CatBoost-A (exp_030's own
hyperparams) + CatBoost-B (deeper/slower-lr variant, teammate's GPU
spec run as CPU) + ExtraTrees (teammate's spec, unconstrained depth),
blended via ensemble.py's coarse_fine_blend_search over 2024 holdout
predictions. Pure structural test -- no affine correction (exp_032),
no season-decay sample weighting (exp_033), same exp_030 105-feature
set and calibration chain (to isolate the ensemble-structure effect
from everything else). See experiments/exp_031_heterogeneous_ensemble.md.
"""

import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
from sklearn.linear_model import LogisticRegression

from ensemble import blend_predict, coarse_fine_blend_search
from exp030_baseline import build_holdout_split
from features import CAT_COLS
from metrics import official_score
from model_factory import fit_catboost, fit_cat_ordinal_encoder, fit_extra_trees

WEIGHT_2024 = 100.0

CATBOOST_B_PARAMS = dict(iterations=600, learning_rate=0.025, depth=7, l2_leaf_reg=3.0,
                          bootstrap_type="Bayesian", bagging_temperature=1.0, border_count=128)


def fit_platt_weighted(raw_pred, y, sample_weight, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y, sample_weight=sample_weight)
    return clf


def approx_calibrated_score(raw_val_pred, y_val):
    """APPROXIMATION for this screening run only: refits a step1-style
    Platt calibrator directly on the 2024 holdout itself (253,507 rows,
    well-determined for a 2-parameter fit) instead of exp_030's proper
    OOF(2019-2023)+2024-weighted procedure (train_exp030_repro.py),
    because building genuine 5-fold OOF for 3 new candidate models here
    would cost 5x the training budget for what's meant to be a first
    directional screen. This is fit-and-scored on the same 2024 rows
    (mildly optimistic/circular, same caveat this project has flagged
    before for quick checks) -- if exp_031 looks promising, exp_037's
    champion assembly must redo this properly with real OOF caches
    before treating any number here as final."""
    calibrator = fit_platt_weighted(raw_val_pred, y_val.to_numpy(), sample_weight=None)
    calibrated = calibrator.predict_proba(raw_val_pred.reshape(-1, 1))[:, 1]
    brier, score = official_score(calibrated, y_val)
    return calibrated, brier, score


def main():
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축 (exp_030 아카이브에서 로드한 정확한 105피처)")
    print("=" * 80)
    X_train, y_train, X_val, y_val, all_features = build_holdout_split()
    print(f"train={X_train.shape}, val={X_val.shape}, n_features={len(all_features)}")

    print()
    print("=" * 80)
    print("1. CatBoost-A (exp_030과 동일 하이퍼파라미터, seed=42)")
    print("=" * 80)
    t = time.time()
    res_a = fit_catboost(X_train, y_train, X_val, y_val, CAT_COLS, seed=42, name="CatBoost-A")
    print(f"완료: {time.time()-t:.1f}s, best_iter={res_a.extra['best_iteration']}")
    brier_a, score_a = official_score(res_a.val_pred, y_val)
    print(f"[CatBoost-A raw] Brier={brier_a:.6f} | score={score_a:.2f}")

    print()
    print("=" * 80)
    print("2. CatBoost-B (팀원 GPU 스펙, CPU로 재현: depth=7/lr=0.025/iter=600)")
    print("=" * 80)
    t = time.time()
    res_b = fit_catboost(X_train, y_train, X_val, y_val, CAT_COLS, seed=42,
                          params=CATBOOST_B_PARAMS, name="CatBoost-B")
    print(f"완료: {time.time()-t:.1f}s, best_iter={res_b.extra['best_iteration']}")
    brier_b, score_b = official_score(res_b.val_pred, y_val)
    print(f"[CatBoost-B raw] Brier={brier_b:.6f} | score={score_b:.2f}")

    print()
    print("=" * 80)
    print("3. ExtraTrees (n_estimators=300, min_samples_leaf=20, max_features=0.7, max_depth=None)")
    print("=" * 80)
    encoder = fit_cat_ordinal_encoder(X_train, CAT_COLS)
    X_train_enc = X_train.copy()
    X_train_enc[CAT_COLS] = encoder.transform(X_train[CAT_COLS])
    X_val_enc = X_val.copy()
    X_val_enc[CAT_COLS] = encoder.transform(X_val[CAT_COLS])

    t = time.time()
    res_extra = fit_extra_trees(X_train_enc, y_train, X_val_enc, y_val, seed=42,
                                 n_estimators=300, max_depth=None, min_samples_leaf=20,
                                 max_features=0.7, n_jobs=-1)
    print(f"완료: {time.time()-t:.1f}s, model_mb={res_extra.model_mb:.1f}")
    brier_extra, score_extra = official_score(res_extra.val_pred, y_val)
    print(f"[ExtraTrees raw] Brier={brier_extra:.6f} | score={score_extra:.2f}")

    print()
    print("=" * 80)
    print("4. 블렌드 가중치 탐색 (coarse_fine_blend_search, 2024 검증 예측 위에서)")
    print("=" * 80)
    pred_dict = {"CatBoost-A": res_a.val_pred, "CatBoost-B": res_b.val_pred, "ExtraTrees": res_extra.val_pred}
    candidates = list(pred_dict.keys())
    best_weights, best_brier, best_score = coarse_fine_blend_search(pred_dict, y_val.to_numpy(), candidates)
    print(f"최적 가중치: {best_weights}")
    print(f"[블렌드, raw] Brier={best_brier:.6f} | score={best_score:.2f}")

    print()
    print("=" * 80)
    print("5. 근사 Platt 보정 (2024 자체로 직접 피팅 -- 스크리닝용 근사, 상단 docstring 참고)")
    print("=" * 80)
    blend_raw = blend_predict(pred_dict, best_weights)
    _, brier_a_cal, score_a_cal = approx_calibrated_score(res_a.val_pred, y_val)
    _, brier_blend_cal, score_blend_cal = approx_calibrated_score(blend_raw, y_val)
    print(f"  CatBoost-A(근사보정)  = {score_a_cal:.2f}")
    print(f"  블렌드(근사보정)      = {score_blend_cal:.2f}")

    print()
    print("=" * 80)
    print("결과 요약")
    print("=" * 80)
    print(f"  CatBoost-A(raw)={score_a:.2f}  CatBoost-B(raw)={score_b:.2f}  ExtraTrees(raw)={score_extra:.2f}")
    print(f"  블렌드(raw)={best_score:.2f}  가중치={best_weights}")
    print(f"  CatBoost-A(근사보정)={score_a_cal:.2f}  블렌드(근사보정)={score_blend_cal:.2f}")
    print(f"  참고: exp_030_repro의 step1-only 보정 점수(count-trend 전) = 868.07,")
    print(f"        count-trend까지 포함한 공식 기준선 = 875.00")
    print(f"        (이 스크립트의 '근사보정'은 2024로 직접 피팅한 것이라 868.07과")
    print(f"         완전히 동일한 절차는 아님 -- 방향성 판단용, exp_037에서 재검증 필요)")
    print("\n완료.")


if __name__ == "__main__":
    main()
