"""exp_011 final -- retrain the LUPI alpha=0.5 student (the least-bad of
the 3 rejected alphas in experiments/exp011_run_log.txt, still -5.33
below control locally) on the FULL 2019-2024 train.csv, per the user's
"archive exp_010/011 even if locally rejected" policy (dacon-score-push-
round2 memory). The student never sees privileged (trackman row-match)
columns at inference, so the saved artifact is a plain single CatBoost
model -- identical model_type="catboost" inference path as exp_007/009,
no submission/script.py changes needed.

Teacher cross-fit is redone over the FULL 2019-2024 data (not just
2019-2023) so the final blended target uses every available row's
out-of-fold teacher signal, matching how train_exp007_final.py/
train_exp009_final.py always retrain on the complete dataset for the
archived artifact.
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
from sklearn.model_selection import KFold

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
    build_test_time_pitcher_lookup,
    load_pitcher_mapping,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"
ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
TRACKMAN_SHRINK_K = 50
N_FOLDS = 5
SEED = 42
ALPHA = 0.5
FINAL_ITERATIONS = 768  # alpha=0.5 val best_iter(767)+1, exp011_run_log.txt

PRIV_COLS = [f"priv_{c}" for c in PHYSICAL_COLS]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
STUDENT_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS
TEACHER_FEATURES = STUDENT_FEATURES + PRIV_COLS

CB_PARAMS_LOGLOSS = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=SEED, thread_count=-1, verbose=False,
)


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    return df[df["season"].isin(seasons[-n:])]


def main():
    print(f"ALPHA={ALPHA}, FINAL_ITERATIONS={FINAL_ITERATIONS}")
    print("=" * 80)
    print("0. 데이터 로드 + 피처 구축 (전체 2019-2024)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    final_priors = fit_shrinkage_priors(recent_seasons_df(train))
    train_shrunk = apply_shrinkage(train, final_priors)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    print(f"train_shrunk: {train_shrunk.shape}")

    print()
    print("=" * 80)
    print("1. row-level privileged 피처 부착 (전체 2019-2024)")
    print("=" * 80)
    row_ids = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=[ID])
    train_shrunk = train_shrunk.reset_index(drop=True)
    train_shrunk[ID] = row_ids[ID].values

    row_mapping = pd.read_csv("reports/trackman_id_mapping/tables/row_mapping.csv", encoding="utf-8-sig",
                               usecols=["row_id", "trackman_id"])
    priv = row_mapping.merge(trackman_clean[["trackman_id"] + PHYSICAL_COLS], on="trackman_id", how="left")
    priv = priv.rename(columns={c: f"priv_{c}" for c in PHYSICAL_COLS}).drop(columns=["trackman_id"])
    train_shrunk = train_shrunk.merge(priv, on=ID, how="left")
    coverage = train_shrunk[PRIV_COLS[0]].notna().mean()
    print(f"privileged 컬럼 커버리지(행 기준): {coverage:.4f}")

    y_all = train_shrunk[TARGET].to_numpy()

    print()
    print("=" * 80)
    print(f"2. {N_FOLDS}-fold cross-fit teacher (전체 2019-2024, privileged 피처 포함) -> OOF soft label")
    print("=" * 80)
    OOF_CACHE = "./output/exp011_final_teacher_oof_cache.npy"
    if os.path.exists(OOF_CACHE):
        oof_pred = np.load(OOF_CACHE)
        print(f"캐시에서 로드: {OOF_CACHE}")
        assert len(oof_pred) == len(train_shrunk)
    else:
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        oof_pred = np.zeros(len(train_shrunk))
        X_teacher_all = train_shrunk[TEACHER_FEATURES]
        t0 = time.time()
        for fold, (tr_idx, ho_idx) in enumerate(kf.split(train_shrunk)):
            X_tr, y_tr = X_teacher_all.iloc[tr_idx], y_all[tr_idx]
            X_ho = X_teacher_all.iloc[ho_idx]
            train_pool = cb.Pool(X_tr, y_tr, cat_features=CAT_COLS)
            clf = cb.CatBoostClassifier(**CB_PARAMS_LOGLOSS)
            clf.fit(train_pool, verbose=False)
            oof_pred[ho_idx] = clf.predict_proba(X_ho)[:, 1]
            print(f"  fold {fold+1}/{N_FOLDS} 완료 ({time.time()-t0:.1f}s 누적)")
        os.makedirs("./output", exist_ok=True)
        np.save(OOF_CACHE, oof_pred)
        print(f"저장(캐시): {OOF_CACHE}")
    teacher_oof_brier, teacher_oof_score = official_score(oof_pred, y_all)
    print(f"teacher OOF (전체 2019-2024, 참고용): Brier={teacher_oof_brier:.6f}, score={teacher_oof_score:.2f}")

    print()
    print("=" * 80)
    print(f"3. student 최종 재학습: alpha={ALPHA} 블렌드 타겟, 전체 데이터, iterations={FINAL_ITERATIONS}")
    print("=" * 80)
    blended = ALPHA * y_all + (1 - ALPHA) * oof_pred
    X_student = train_shrunk[STUDENT_FEATURES]
    cb_params_ce = dict(CB_PARAMS_LOGLOSS)
    cb_params_ce["loss_function"] = "CrossEntropy"
    cb_params_ce["eval_metric"] = "CrossEntropy"
    cb_params_ce["iterations"] = FINAL_ITERATIONS
    cb_params_ce["verbose"] = 200
    tr_pool = cb.Pool(X_student, blended, cat_features=CAT_COLS)
    final_clf = cb.CatBoostClassifier(**cb_params_ce)
    t = time.time()
    final_clf.fit(tr_pool)
    print(f"최종 재학습 완료 :: {time.time() - t:.1f}s")

    print()
    print("=" * 80)
    print("4. 저장 (student만 -- privileged 컬럼 전혀 사용 안 함, exp_007과 동일 추론 경로)")
    print("=" * 80)
    os.makedirs(MODEL_DIR, exist_ok=True)

    lookup, league_fallback = build_test_time_pitcher_lookup(tables, pitcher_mapping, shrink_k=TRACKMAN_SHRINK_K)
    lookup_path = os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv")
    lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")
    print(f"저장: {lookup_path} ({lookup.shape})")

    # exp_010이 남긴 시드-백 아티팩트가 같은 model/에 남아있으면 정리한다.
    for stale in ["catboost_model_seed42.cbm", "catboost_model_seed1.cbm"]:
        p = os.path.join(MODEL_DIR, stale)
        if os.path.exists(p):
            os.remove(p)
            print(f"제거: {p} (exp_010 seedbag 아티팩트, 단일모델과 혼동 방지)")

    final_clf.save_model(os.path.join(MODEL_DIR, "catboost_model.cbm"))
    joblib.dump(
        {
            "model_type": "catboost",
            "base_features": BASE_FEATURES,
            "all_features": STUDENT_FEATURES,
            "trackman_cols": TRACKMAN_PITCHER_ASOF_COLS,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
            "trackman_league_fallback": league_fallback,
            "trackman_shrink_k": TRACKMAN_SHRINK_K,
            "exp_id": f"exp_011_lupi_alpha{ALPHA}",
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장: {MODEL_DIR}/catboost_model.cbm, {MODEL_DIR}/model_meta.pkl")
    print("\n완료.")


if __name__ == "__main__":
    main()
