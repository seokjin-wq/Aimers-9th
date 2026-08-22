"""exp_009 final — retrain a chosen exp_009 hyperparameter variant on the
FULL 2019-2024 train.csv (same 89-feature set as exp_007: exp_003's 84 +
5 trackman pitcher-level as-of physical features, shrink_k=50) and save
model artifacts, exactly like train_exp007_final.py does for the
baseline. exp_009's own baseline config is byte-for-byte identical to
exp_007 (same hyperparameters), so it is NOT re-archived here -- this
script is only for packaging a genuinely different exp_009 variant
(different CatBoost hyperparameters) as a distinct LB submission
candidate, per the user's "archive everything, even if it lost locally"
policy (see dacon-score-push-round2 memory).

사용법:
    python src/train_exp009_final.py <config_name>

config_name은 CONFIGS 딕셔너리의 키 중 하나 (exp_009 실험의 9개
coordinate-wise 설정과 동일한 이름/파라미터, "baseline" 제외 -- baseline은
exp_007과 완전히 같은 모델이라 여기서 재학습할 이유가 없음).
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

# exp_009 (src/train_exp009_hpo.py)와 동일한 CONFIGS 정의 (baseline 제외).
CONFIGS = {
    "depth8": {"depth": 8},
    "depth4": {"depth": 4},
    "l2reg8": {"l2_leaf_reg": 8.0},
    "l2reg1": {"l2_leaf_reg": 1.0},
    "lr002_iter3000": {"learning_rate": 0.02, "iterations": 3000},
    "randstrength5": {"random_strength": 5.0},
    "bagtemp2": {"bootstrap_type": "Bayesian", "bagging_temperature": 2.0},
    "lossguide64": {"grow_policy": "Lossguide", "max_leaves": 64},
}

if len(sys.argv) > 1 and sys.argv[1] in CONFIGS:
    CONFIG_NAME = sys.argv[1]
else:
    raise SystemExit(f"사용법: python src/train_exp009_final.py <config_name>\n선택지: {list(CONFIGS)}")

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
ALL_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def base_params():
    return dict(
        iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
        loss_function="Logloss", eval_metric="Logloss",
        random_seed=42, thread_count=-1, verbose=200,
    )


def main():
    overrides = CONFIGS[CONFIG_NAME]
    print(f"CONFIG_NAME = {CONFIG_NAME}, overrides = {overrides}")
    print("=" * 80)
    print("1. 검증 재확인 (2019-2023 학습 / 2024 검증), exp_009와 동일 설정으로")
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

    cb_params = base_params()
    cb_params.update(overrides)
    X_train, y_train = df_val.loc[~is_val, ALL_FEATURES], df_val.loc[~is_val, TARGET]
    X_val, y_val = df_val.loc[is_val, ALL_FEATURES], df_val.loc[is_val, TARGET]
    train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
    val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)
    val_clf = cb.CatBoostClassifier(**cb_params)
    val_clf.fit(train_pool, eval_set=val_pool, early_stopping_rounds=100)
    val_pred = val_clf.predict_proba(X_val)[:, 1]
    brier, score = official_score(val_pred, y_val)
    print(f"검증 재확인: Brier={brier:.6f} | score={score:.2f} | best_iter={val_clf.get_best_iteration()}")

    print()
    print("=" * 80)
    print("2. 전체 2019-2024 데이터로 최종 재학습")
    print("=" * 80)
    final_priors = fit_shrinkage_priors(recent_seasons_df(train))
    train_shrunk_final = apply_shrinkage(train, final_priors)
    train_final = attach_pitcher_physical_features(train_shrunk_final, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)

    final_params = dict(cb_params)
    final_params["iterations"] = val_clf.get_best_iteration() + 1
    final_clf = cb.CatBoostClassifier(**final_params)
    final_train_pool = cb.Pool(train_final[ALL_FEATURES], train_final[TARGET], cat_features=CAT_COLS)
    t = time.time()
    final_clf.fit(final_train_pool)
    print(f"최종 재학습 완료 :: {time.time() - t:.1f}s, iterations={final_params['iterations']}")

    print()
    print("=" * 80)
    print("3. 저장")
    print("=" * 80)
    os.makedirs(MODEL_DIR, exist_ok=True)

    lookup, league_fallback = build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({lookup.shape})")

    final_clf.save_model(os.path.join(MODEL_DIR, "catboost_model.cbm"))
    joblib.dump(
        {
            "model_type": "catboost",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "trackman_cols": TRACKMAN_PITCHER_ASOF_COLS,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
            "trackman_league_fallback": league_fallback,
            "trackman_shrink_k": TRACKMAN_SHRINK_K,
            "exp_id": f"exp_009_{CONFIG_NAME}",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: {MODEL_DIR}/catboost_model.cbm, {MODEL_DIR}/model_meta.pkl")
    print(f"\n검증 점수(참고용, 최종 모델은 전체 데이터로 재학습돼 이 점수와 다름): {score:.2f}")
    print("완료.")


if __name__ == "__main__":
    main()
