"""exp_007 — exp_003's feature set (baseline: local score 723.17) + 5
pitcher-level trackman physical-intensity as-of features
(`src/trackman_pitcher_features.py`, Phase 2 v3 ID mapping). Single
change vs exp_003: everything else (season-aware shrinkage prior,
CatBoost hyperparameters, validation split) is identical to
`train_exp003.py`.

Tests 3 shrinkage strengths (k=50/100/300) as a small ablation, since
exp_005 explicitly flagged "stronger regularization" as the untested
next hypothesis for any new trackman feature.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import joblib
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
from metrics import official_score
from trackman_pitcher_features import (
    PHYSICAL_COLS,
    TRACKMAN_PITCHER_ASOF_COLS,
    build_pitcher_physical_asof_tables,
    attach_pitcher_physical_features,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"

ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
SHRINK_K_GRID = [50, 100, 300]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


def main():
    print("=" * 80)
    print("0. 데이터 로드 + row-local 피처(features.build_features)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)
    print(f"train: {train.shape} | exp_003 피처 {len(EXP003_FEATURES)}개 + trackman 피처 {len(TRACKMAN_PITCHER_ASOF_COLS)}개")

    print()
    print("=" * 80)
    print("1. trackman 투수 단위 as-of 테이블 구축 (Phase 2 v3 매핑)")
    print("=" * 80)
    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    print(f"매핑된 투수: {len(pitcher_mapping)} / train 고유 투수 {train['pitcher_id'].nunique()}")
    tables = build_pitcher_physical_asof_tables(trackman_clean)
    for col in PHYSICAL_COLS:
        print(f"  {col}: league_fallback={tables[col]['league_fallback']:.4f}, table rows={len(tables[col]['table'])}")

    is_val = train["season"] == 2024
    train_only = train.loc[~is_val]

    print()
    print("=" * 80)
    print("2. season-aware shrinkage prior (exp_003과 동일)")
    print("=" * 80)
    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, val_priors_recent)

    print()
    print("=" * 80)
    print("3. shrink_k 그리드로 trackman 피처 부착 + CatBoost 학습/검증")
    print("=" * 80)

    cb_params = dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=42, thread_count=-1, verbose=200,
    )

    results = {}
    for k in SHRINK_K_GRID:
        print(f"\n--- shrink_k={k} ---")
        df_k = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=k)
        X_train, y_train = df_k.loc[~is_val, ALL_FEATURES], df_k.loc[~is_val, TARGET]
        X_val, y_val = df_k.loc[is_val, ALL_FEATURES], df_k.loc[is_val, TARGET]

        train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
        val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)

        t = time.time()
        clf = cb.CatBoostClassifier(**cb_params)
        clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        elapsed = time.time() - t
        best_iter = clf.get_best_iteration()

        val_pred = clf.predict_proba(X_val)[:, 1]
        brier, score = official_score(val_pred, y_val)
        print(f"[k={k}] Brier={brier:.6f} | score={score:.2f} | best_iter={best_iter} | {elapsed:.1f}s")
        print(f"pred mean/min/max: {val_pred.mean():.4f} / {val_pred.min():.4f} / {val_pred.max():.4f}")

        results[k] = {
            "brier": brier, "score": score, "best_iter": best_iter,
            "elapsed": elapsed, "clf": clf, "val_pred": val_pred,
        }

    print()
    print("=" * 80)
    print("4. exp_003 베이스라인(트랙맨 피처 없음) 재현 — 동일 시드/파라미터로 공정 비교")
    print("=" * 80)
    X_train_b, y_train_b = train_shrunk.loc[~is_val, EXP003_FEATURES], train_shrunk.loc[~is_val, TARGET]
    X_val_b, y_val_b = train_shrunk.loc[is_val, EXP003_FEATURES], train_shrunk.loc[is_val, TARGET]
    train_pool_b = cb.Pool(X_train_b, y_train_b, cat_features=CAT_COLS)
    val_pool_b = cb.Pool(X_val_b, y_val_b, cat_features=CAT_COLS)
    t = time.time()
    clf_b = cb.CatBoostClassifier(**cb_params)
    clf_b.fit(train_pool_b, eval_set=val_pool_b, early_stopping_rounds=100)
    elapsed_b = time.time() - t
    val_pred_b = clf_b.predict_proba(X_val_b)[:, 1]
    brier_b, score_b = official_score(val_pred_b, y_val_b)
    print(f"[baseline, 이 실행 재현] Brier={brier_b:.6f} | score={score_b:.2f} | best_iter={clf_b.get_best_iteration()} | {elapsed_b:.1f}s")

    print()
    print("=" * 80)
    print("5. 요약")
    print("=" * 80)
    print(f"exp_003 기록값(참고): local score 723.17 (Brier 0.248000)")
    print(f"exp_003 이 실행 재현: local score {score_b:.2f} (Brier {brier_b:.6f})")
    for k in SHRINK_K_GRID:
        r = results[k]
        delta = r["score"] - score_b
        print(f"exp_007 (+5 trackman 피처, shrink_k={k}): local score {r['score']:.2f} (Brier {r['brier']:.6f}), Δ vs 이 실행 baseline = {delta:+.2f}")

    best_k = max(SHRINK_K_GRID, key=lambda k: results[k]["score"])
    print(f"\n최선 shrink_k: {best_k} (score {results[best_k]['score']:.2f})")

    if results[best_k]["score"] > score_b:
        print("\n--- feature importance (최선 k, top 15 / 84 exp_003 피처 중 순위) ---")
        clf_best = results[best_k]["clf"]
        df_best = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=best_k)
        train_pool_best = cb.Pool(
            df_best.loc[~is_val, ALL_FEATURES], df_best.loc[~is_val, TARGET], cat_features=CAT_COLS
        )
        importances = clf_best.get_feature_importance(train_pool_best)
        ranked = sorted(zip(ALL_FEATURES, importances), key=lambda x: -x[1])
        for rank, (name, imp) in enumerate(ranked[:20], start=1):
            tag = " <== trackman" if name in TRACKMAN_PITCHER_ASOF_COLS else ""
            print(f"  #{rank:2d} {name}: {imp:.2f}{tag}")
        trackman_ranks = [i + 1 for i, (name, _) in enumerate(ranked) if name in TRACKMAN_PITCHER_ASOF_COLS]
        print(f"\ntrackman 피처 5개의 전체 89개 중 순위: {sorted(trackman_ranks)}")

        print("\n--- 오류 분석 (최선 k, 구간별 Brier) ---")
        val_seg = df_best.loc[is_val, ["two_strike", "is_close_game", "asof_pitcher_n"]].copy()
        val_seg["pred"] = results[best_k]["val_pred"]
        val_seg["y"] = df_best.loc[is_val, TARGET].values
        val_seg["cold_start"] = val_seg["asof_pitcher_n"] < 50
        mapped_pids = set(pitcher_mapping["pitcher_id"])
        val_seg["pitcher_mapped"] = df_best.loc[is_val, "pitcher_id"].isin(mapped_pids).values
        segments = {
            "two_strike=1": val_seg["two_strike"] == 1,
            "two_strike=0": val_seg["two_strike"] == 0,
            "is_close_game=1": val_seg["is_close_game"] == 1,
            "cold_start(n<50)": val_seg["cold_start"],
            "warm(n>=50)": ~val_seg["cold_start"],
            "trackman 매핑된 투수": val_seg["pitcher_mapped"],
            "trackman 매핑 안 된 투수": ~val_seg["pitcher_mapped"],
        }
        for name, mask in segments.items():
            sub = val_seg.loc[mask]
            seg_brier = ((sub["pred"] - sub["y"]) ** 2).mean()
            print(f"  {name}: n={len(sub)}, brier={seg_brier:.6f}, 실제 성공률={sub['y'].mean():.4f}, 평균예측={sub['pred'].mean():.4f}")

    print("\n완료. (모델 저장은 개선이 확인된 뒤 별도 스크립트로 진행)")


if __name__ == "__main__":
    main()
