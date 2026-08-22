"""exp_008 — extend exp_007's trackman pitcher-level as-of feature set
from 5 to 8 physical columns (`src/trackman_pitcher_features.py`
PHYSICAL_COLS now also includes rel_height, rel_side, zone_speed — the
3 trackman_history.csv physical columns exp_007 left untested). Single
change vs exp_007: everything else (season-aware shrinkage prior,
CatBoost hyperparameters, validation split, shrink_k=50 winner) is
identical.

Reports, for a fair A/B/C comparison in one run:
  A. exp_003 baseline (no trackman) reproduced
  B. exp_007's original 5-col trackman set (k=50) reproduced
  C. exp_008's new 8-col trackman set, at k in {50, 100}
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
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

ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
SHRINK_K_GRID = [50, 100]
EXP007_5COL = [
    "trackman_rel_speed_asof",
    "trackman_spin_rate_asof",
    "trackman_induced_vert_break_asof",
    "trackman_horz_break_asof",
    "trackman_extension_asof",
]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
EXP007_FEATURES = EXP003_FEATURES + EXP007_5COL
EXP008_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS

CB_PARAMS = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=42, thread_count=-1, verbose=200,
)


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


def fit_eval(X_train, y_train, X_val, y_val, cat_cols, tag):
    train_pool = cb.Pool(X_train, y_train, cat_features=cat_cols)
    val_pool = cb.Pool(X_val, y_val, cat_features=cat_cols)
    t = time.time()
    clf = cb.CatBoostClassifier(**CB_PARAMS)
    clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    elapsed = time.time() - t
    val_pred = clf.predict_proba(X_val)[:, 1]
    brier, score = official_score(val_pred, y_val)
    print(f"[{tag}] Brier={brier:.6f} | score={score:.2f} | best_iter={clf.get_best_iteration()} | {elapsed:.1f}s")
    return {"clf": clf, "brier": brier, "score": score, "val_pred": val_pred, "elapsed": elapsed}


def main():
    print("=" * 80)
    print("0. 데이터 로드 + row-local 피처")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)
    print(f"train: {train.shape}")

    print()
    print("=" * 80)
    print("1. trackman 투수 단위 as-of 테이블 구축 (8개 physical 컬럼)")
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
    print("A. exp_003 베이스라인(트랙맨 없음) 재현")
    print("=" * 80)
    res_a = fit_eval(
        train_shrunk.loc[~is_val, EXP003_FEATURES], train_shrunk.loc[~is_val, TARGET],
        train_shrunk.loc[is_val, EXP003_FEATURES], train_shrunk.loc[is_val, TARGET],
        CAT_COLS, "A: exp_003 baseline",
    )

    print()
    print("=" * 80)
    print("B. exp_007 5개 trackman 컬럼(k=50) 재현")
    print("=" * 80)
    df_5col = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=50)
    res_b = fit_eval(
        df_5col.loc[~is_val, EXP007_FEATURES], df_5col.loc[~is_val, TARGET],
        df_5col.loc[is_val, EXP007_FEATURES], df_5col.loc[is_val, TARGET],
        CAT_COLS, "B: exp_007 5col k=50",
    )

    print()
    print("=" * 80)
    print("C. exp_008 8개 trackman 컬럼, shrink_k 그리드")
    print("=" * 80)
    results_c = {}
    for k in SHRINK_K_GRID:
        df_8col = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=k)
        res = fit_eval(
            df_8col.loc[~is_val, EXP008_FEATURES], df_8col.loc[~is_val, TARGET],
            df_8col.loc[is_val, EXP008_FEATURES], df_8col.loc[is_val, TARGET],
            CAT_COLS, f"C: exp_008 8col k={k}",
        )
        results_c[k] = res

    print()
    print("=" * 80)
    print("요약")
    print("=" * 80)
    print(f"A. exp_003 baseline:      score={res_a['score']:.2f} (Brier {res_a['brier']:.6f})")
    print(f"B. exp_007 5col k=50:     score={res_b['score']:.2f} (Brier {res_b['brier']:.6f}), Δ vs A = {res_b['score']-res_a['score']:+.2f}")
    for k in SHRINK_K_GRID:
        r = results_c[k]
        print(f"C. exp_008 8col k={k}:    score={r['score']:.2f} (Brier {r['brier']:.6f}), Δ vs A = {r['score']-res_a['score']:+.2f}, Δ vs B = {r['score']-res_b['score']:+.2f}")

    best_k = max(SHRINK_K_GRID, key=lambda k: results_c[k]["score"])
    best_c = results_c[best_k]
    if best_c["score"] > res_b["score"]:
        print(f"\n최선: exp_008 8col k={best_k} (score {best_c['score']:.2f}) — exp_007(5col)보다 개선")
        print("\n--- feature importance (최선 k, top 20 / 92 피처 중 순위) ---")
        df_best = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=best_k)
        train_pool_best = cb.Pool(df_best.loc[~is_val, EXP008_FEATURES], df_best.loc[~is_val, TARGET], cat_features=CAT_COLS)
        importances = best_c["clf"].get_feature_importance(train_pool_best)
        ranked = sorted(zip(EXP008_FEATURES, importances), key=lambda x: -x[1])
        for rank, (name, imp) in enumerate(ranked[:20], start=1):
            tag = " <== trackman" if name in TRACKMAN_PITCHER_ASOF_COLS else ""
            print(f"  #{rank:2d} {name}: {imp:.2f}{tag}")
        trackman_ranks = [i + 1 for i, (name, _) in enumerate(ranked) if name in TRACKMAN_PITCHER_ASOF_COLS]
        print(f"\ntrackman 피처 8개의 전체 {len(EXP008_FEATURES)}개 중 순위: {sorted(trackman_ranks)}")
        new3_ranks = [i + 1 for i, (name, _) in enumerate(ranked) if name in ["trackman_rel_height_asof", "trackman_rel_side_asof", "trackman_zone_speed_asof"]]
        print(f"신규 3개(rel_height/rel_side/zone_speed) 순위: {sorted(new3_ranks)}")
    else:
        print(f"\nexp_008(8col)이 exp_007(5col)보다 개선 없음 — 최선 k={best_k}, score={best_c['score']:.2f} <= {res_b['score']:.2f}")

    print("\n완료. (모델 저장은 개선이 확인된 뒤 별도 스크립트로 진행)")


if __name__ == "__main__":
    main()
