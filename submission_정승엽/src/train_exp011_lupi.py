"""exp_011 — LUPI (Learning Using Privileged Information) via
cross-fitted knowledge distillation, using Phase 2's ROW-level trackman
match (`reports/trackman_id_mapping/tables/row_mapping.csv`, 87.23% of
train rows) as privileged information available only at train time
(confirmed allowed by DACON Q&A -- `dacon-lupi-distillation` memory).

Unlike exp_007/exp_008 (pitcher-level *as-of average* physical
intensity, usable at both train and test time since it only needs a
pitcher's OWN past history), this experiment uses each row's ACTUAL
matched trackman physical measurements for THAT SPECIFIC PITCH --
strictly richer information that literally cannot exist for 2025 test
rows (no 2025 trackman data at all), so it can only be used the LUPI
way: as an extra input to a "teacher" model at train time, whose
predictions become part of a soft training target for the real
"student" model, which uses only pre-pitch, always-available features
(so student inference at test time is identical in shape to
exp_007/exp_008 -- no privileged columns needed).

Leak-safety of the distillation itself: a naive teacher fit on all of
2019-2023 and then asked to re-predict on those same 2019-2023 rows
would echo back a memorized/overfit signal, and training the student to
imitate that would just transfer the overfitting, not real signal. So
the teacher's soft labels for the 2019-2023 rows are produced
out-of-fold (5-fold CV: each fold's teacher never sees that fold's rows
during its own fit) -- standard cross-fitting, the same principle
`features.fit_shrinkage_priors` uses to keep a prior "train-only" but
applied here across folds instead of across a season boundary. Season
2024 validation is scored purely on the TRUE label, never the teacher's
opinion, so this cannot inflate the reported validation score.
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
N_FOLDS = 5
SEED = 42
ALPHA_GRID = [0.5, 0.7, 0.85]  # blended_target = alpha*y_true + (1-alpha)*oof_teacher_prob

PRIV_COLS = [f"priv_{c}" for c in PHYSICAL_COLS]

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"), encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
EXP003_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS
STUDENT_FEATURES = EXP003_FEATURES + TRACKMAN_PITCHER_ASOF_COLS  # exp_007's 5-col champion set (exp_008's 8-col extension was rejected)
TEACHER_FEATURES = STUDENT_FEATURES + PRIV_COLS

CB_PARAMS_LOGLOSS = dict(
    iterations=2000, learning_rate=0.03, depth=6, l2_leaf_reg=3.0,
    loss_function="Logloss", eval_metric="Logloss",
    random_seed=SEED, thread_count=-1, verbose=False,
)


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


def main():
    print("=" * 80)
    print("0. 데이터 로드 + row-local 피처 + trackman as-of 피처(exp_007 5col 챔피언)")
    print("=" * 80)
    train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"), encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train = build_features(train)

    trackman_clean = pd.read_csv(os.path.join(DATA_DIR, "processed", "trackman_clean.csv"), encoding="utf-8-sig")
    pitcher_mapping = load_pitcher_mapping()
    tables = build_pitcher_physical_asof_tables(trackman_clean)

    is_val = train["season"] == 2024
    train_only_raw = train.loc[~is_val]
    val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only_raw))
    train_shrunk = apply_shrinkage(train, val_priors_recent)
    train_shrunk = attach_pitcher_physical_features(train_shrunk, tables, pitcher_mapping, shrink_k=50)
    print(f"train_shrunk: {train_shrunk.shape}")

    print()
    print("=" * 80)
    print("1. row-level privileged 피처 부착 (Phase 2 row_mapping, train-only)")
    print("=" * 80)
    # row_id는 원본 train.csv usecols에서 안 읽었으므로 다시 읽어 붙인다
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

    is_val = train_shrunk["season"] == 2024
    train_2319 = train_shrunk.loc[~is_val].reset_index(drop=True)
    val_2024 = train_shrunk.loc[is_val].reset_index(drop=True)
    y_2319 = train_2319[TARGET].to_numpy()
    y_val = val_2024[TARGET].to_numpy()

    print()
    print("=" * 80)
    print(f"2. {N_FOLDS}-fold cross-fit teacher (2019-2023만, privileged 피처 포함) -> OOF soft label")
    print("=" * 80)
    OOF_CACHE = "./output/exp011_teacher_oof_cache.npy"
    if os.path.exists(OOF_CACHE):
        oof_pred = np.load(OOF_CACHE)
        print(f"캐시에서 로드: {OOF_CACHE} (재계산 생략 -- 이 스테이지는 이전 실행에서 이미 39분 걸림)")
        assert len(oof_pred) == len(train_2319), "캐시된 oof_pred 길이가 현재 train_2319와 다름 -- 캐시 삭제 후 재실행 필요"
    else:
        kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
        oof_pred = np.zeros(len(train_2319))
        X_teacher_all = train_2319[TEACHER_FEATURES]
        t0 = time.time()
        for fold, (tr_idx, ho_idx) in enumerate(kf.split(train_2319)):
            X_tr, y_tr = X_teacher_all.iloc[tr_idx], y_2319[tr_idx]
            X_ho = X_teacher_all.iloc[ho_idx]
            train_pool = cb.Pool(X_tr, y_tr, cat_features=CAT_COLS)
            clf = cb.CatBoostClassifier(**CB_PARAMS_LOGLOSS)
            clf.fit(train_pool, verbose=False)
            oof_pred[ho_idx] = clf.predict_proba(X_ho)[:, 1]
            print(f"  fold {fold+1}/{N_FOLDS} 완료 ({time.time()-t0:.1f}s 누적)")
        os.makedirs("./output", exist_ok=True)
        np.save(OOF_CACHE, oof_pred)
        print(f"저장(캐시): {OOF_CACHE}")
    teacher_oof_brier, teacher_oof_score = official_score(oof_pred, y_2319)
    print(f"teacher OOF (2019-2023 자체, 참고용): Brier={teacher_oof_brier:.6f}, score={teacher_oof_score:.2f}")

    print()
    print("=" * 80)
    print("3. student 학습: student 피처(privileged 없음) + blended target, alpha 그리드")
    print("=" * 80)
    X_student_tr = train_2319[STUDENT_FEATURES]
    X_student_val = val_2024[STUDENT_FEATURES]

    print("\n--- control: 표준 Logloss + 실제 라벨 (exp_008 재현) ---")
    ctrl_pool = cb.Pool(X_student_tr, y_2319, cat_features=CAT_COLS)
    ctrl_val_pool = cb.Pool(X_student_val, y_val, cat_features=CAT_COLS)
    clf_ctrl = cb.CatBoostClassifier(**CB_PARAMS_LOGLOSS)
    clf_ctrl.set_params(verbose=200)
    t = time.time()
    clf_ctrl.fit(ctrl_pool, eval_set=ctrl_val_pool, early_stopping_rounds=100)
    pred_ctrl = clf_ctrl.predict_proba(X_student_val)[:, 1]
    brier_ctrl, score_ctrl = official_score(pred_ctrl, y_val)
    print(f"[control] Brier={brier_ctrl:.6f} | score={score_ctrl:.2f} | best_iter={clf_ctrl.get_best_iteration()} | {time.time()-t:.1f}s")

    results = {}
    for alpha in ALPHA_GRID:
        blended = alpha * y_2319 + (1 - alpha) * oof_pred
        cb_params_ce = dict(CB_PARAMS_LOGLOSS)
        cb_params_ce["loss_function"] = "CrossEntropy"
        cb_params_ce["eval_metric"] = "CrossEntropy"
        cb_params_ce["verbose"] = 200
        tr_pool = cb.Pool(X_student_tr, blended, cat_features=CAT_COLS)
        val_pool = cb.Pool(X_student_val, y_val.astype(float), cat_features=CAT_COLS)
        clf = cb.CatBoostClassifier(**cb_params_ce)
        t = time.time()
        clf.fit(tr_pool, eval_set=val_pool, early_stopping_rounds=100)
        pred = clf.predict_proba(X_student_val)[:, 1]
        brier, score = official_score(pred, y_val)
        elapsed = time.time() - t
        print(f"[alpha={alpha}] Brier={brier:.6f} | score={score:.2f} | Δ vs control={score-score_ctrl:+.2f} | best_iter={clf.get_best_iteration()} | {elapsed:.1f}s")
        results[alpha] = {"brier": brier, "score": score, "clf": clf}

    print()
    print("=" * 80)
    print("요약")
    print("=" * 80)
    print(f"control (표준, privileged 없음): score={score_ctrl:.2f} (Brier {brier_ctrl:.6f})")
    for alpha in ALPHA_GRID:
        r = results[alpha]
        print(f"LUPI alpha={alpha}: score={r['score']:.2f} (Brier {r['brier']:.6f}), Δ={r['score']-score_ctrl:+.2f}")
    best_alpha = max(ALPHA_GRID, key=lambda a: results[a]["score"])
    if results[best_alpha]["score"] > score_ctrl:
        print(f"\n최선: alpha={best_alpha} (score {results[best_alpha]['score']:.2f}) — control보다 개선")
    else:
        print(f"\nLUPI 개선 없음 — control(score={score_ctrl:.2f})이 모든 alpha보다 우세")

    print("\n완료.")


if __name__ == "__main__":
    main()
