"""exp_010 final — retrain the champion seed-bagging combo (seeds {42, 1},
picked because their 2-seed average validation score 749.58 beat every
other cumulative subset in experiments/exp010_run_log.txt, including the
full 5-seed average 741.15 and the best single seed 745.51) on the FULL
2019-2024 train.csv, and save BOTH models for averaged inference:
  model/catboost_model_seed42.cbm
  model/catboost_model_seed1.cbm
  model/model_meta.pkl              (model_type="catboost_seedbag",
                                      seed_model_files=[...])
  model/trackman_pitcher_lookup.csv (same as exp_007, shrink_k=50)

submission/script.py already knows how to load+average a
"catboost_seedbag" model_type (see the `elif model_type ==
"catboost_seedbag"` branches).
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

from features import CAT_COLS, DERIVED_COLS, SHRUNK_COLS, POST_SHRINKAGE_COLS, apply_shrinkage, build_features, fit_shrinkage_priors
from metrics import official_score
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
SEEDS = [42, 1]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def base_params(seed):
    return dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=seed, thread_count=-1, verbose=200,
    )


def main():
    print(f"SEEDS = {SEEDS}")
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
    val_priors = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk_val = apply_shrinkage(train, val_priors)
    df_val = attach_pitcher_physical_features(train_shrunk_val, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    X_train, y_train = df_val.loc[~is_val, ALL_FEATURES], df_val.loc[~is_val, TARGET]
    X_val, y_val = df_val.loc[is_val, ALL_FEATURES], df_val.loc[is_val, TARGET]
    train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)

    print()
    print("=" * 80)
    print("1. 검증 재확인 (2019-2023 학습 / 2024 검증), 시드별 + 평균")
    print("=" * 80)
    best_iters = {}
    val_preds = {}
    for seed in SEEDS:
        val_clf = cb.CatBoostClassifier(**base_params(seed))
        val_clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
        pred = val_clf.predict_proba(X_val)[:, 1]
        brier, score = official_score(pred, y_val)
        best_iters[seed] = val_clf.get_best_iteration()
        val_preds[seed] = pred
        print(f"[seed={seed}] Brier={brier:.6f} | score={score:.2f} | best_iter={best_iters[seed]}")
    avg_pred = sum(val_preds.values()) / len(SEEDS)
    avg_brier, avg_score = official_score(avg_pred, y_val)
    print(f"[{len(SEEDS)}개 시드 평균] Brier={avg_brier:.6f} | score={avg_score:.2f}")

    print()
    print("=" * 80)
    print("2. 전체 2019-2024 데이터로 시드별 최종 재학습")
    print("=" * 80)
    final_priors = fit_shrinkage_priors(recent_seasons_df(train))
    train_shrunk_final = apply_shrinkage(train, final_priors)
    train_final = attach_pitcher_physical_features(train_shrunk_final, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    final_train_pool = cb.Pool(train_final[ALL_FEATURES], train_final[TARGET], cat_features=CAT_COLS)

    os.makedirs(MODEL_DIR, exist_ok=True)
    seed_model_files = []
    for seed in SEEDS:
        final_params = base_params(seed)
        final_params["iterations"] = best_iters[seed] + 1
        final_clf = cb.CatBoostClassifier(**final_params)
        t = time.time()
        final_clf.fit(final_train_pool)
        print(f"[seed={seed}] 최종 재학습 완료 :: {time.time() - t:.1f}s, iterations={final_params['iterations']}")
        fname = f"catboost_model_seed{seed}.cbm"
        final_clf.save_model(os.path.join(MODEL_DIR, fname))
        seed_model_files.append(fname)

    print()
    print("=" * 80)
    print("3. 저장")
    print("=" * 80)
    lookup, league_fallback = build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({lookup.shape})")

    # 예전 단일-모델 아티팩트가 같은 model/ 폴더에 남아있으면 package_submission.py가
    # 그대로 같이 zip에 넣어버려 혼동을 줄 수 있으니 제거한다.
    stale = os.path.join(MODEL_DIR, "catboost_model.cbm")
    if os.path.exists(stale):
        os.remove(stale)
        print(f"제거: {stale} (단일-모델 exp_007/009 아티팩트, seedbag과 혼동 방지)")

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
            "exp_id": "exp_010_seedbag_42_1",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: {MODEL_DIR}/model_meta.pkl (seed_model_files={seed_model_files})")
    print(f"\n검증 점수(참고용, 최종 모델은 전체 데이터로 재학습돼 이 점수와 다름): {avg_score:.2f}")
    print("완료.")


if __name__ == "__main__":
    main()
