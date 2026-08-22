"""exp_006 — Phase A~D model comparison (Mean / Logistic / RandomForest /
ExtraTrees / CatBoost / LightGBM), prediction correlation, weighted
blend search, and leak-free Platt/Isotonic calibration.

Feature set identical to exp_003's 84-feature bundle (same
build_features + season-aware shrinkage priors), so every model here is
compared apples-to-apples on the current champion's own features —
Trackman (Phase E) is explicitly out of scope this run (see
experiments/exp_006_model_selection.md).

A hard sanity-check gate right after the CatBoost arm finishes verifies
this script's shared pipeline reproduces exp_003's exact numbers
(Brier 0.248000 / score 723.17) before any downstream comparison,
blend, or calibration result is trusted.

Never writes to model/ (that directory holds the current submission
champion's artifacts) — this script is measurement-only.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import calibration
import ensemble
import metrics
import model_factory
import validation
from features import (
    ALL_DERIVED_COLS,
    CAT_COLS,
    DERIVED_COLS,
    POST_SHRINKAGE_COLS,
    SHRUNK_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)

DATA_DIR = "./data"
OUT_DIR = "./reports/model_selection"
MODEL_DIR = "./model"  # read-only sanity check target, never written here

ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2
SEED = 42

LOW_CARD_ID_COLS = ["pitcher_team_id", "batter_team_id"]
HIGH_CARD_ID_COLS = ["pitcher_id", "batter_id"]

os.makedirs(OUT_DIR, exist_ok=True)


def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


# ---------------------------------------------------------------------
# Step 0 — data type summary
# ---------------------------------------------------------------------

def _semantic_type(col, dtype, n_unique, cat_cols, high_card_cols, low_card_override,
                    id_cols, target_col, time_cols=()):
    if col in id_cols:
        return "identifier"
    if col == target_col:
        return "target"
    if col in time_cols:
        return "time"
    if col in cat_cols or col in low_card_override:
        return "categorical_low_cardinality"
    if col in high_card_cols:
        return "categorical_high_cardinality"
    if dtype == object:
        return "categorical_high_cardinality" if n_unique > 20 else "categorical_low_cardinality"
    if n_unique <= 15:
        return "ordinal_numeric"
    return "continuous_numeric"


def build_data_type_summary(df, cat_cols, high_card_cols, low_card_override,
                             id_cols, target_col, time_cols=()):
    rows = []
    for col in df.columns:
        dtype = df[col].dtype
        n_unique = df[col].nunique(dropna=True)
        missing_rate = df[col].isna().mean()
        rows.append({
            "column": col,
            "dtype": str(dtype),
            "n_unique": n_unique,
            "missing_rate": missing_rate,
            "semantic_type": _semantic_type(col, dtype, n_unique, cat_cols, high_card_cols,
                                             low_card_override, id_cols, target_col, time_cols),
        })
    return pd.DataFrame(rows)


def main():
    section("Step 0 — 데이터 타입 요약")

    test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"),
                             encoding="utf-8-sig", nrows=0).columns
    BASE_FEATURES = [c for c in test_cols if c != ID]
    ALL_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS

    train_raw = pd.read_csv(os.path.join(DATA_DIR, "train.csv"),
                             encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
    train_type_summary = build_data_type_summary(
        train_raw, cat_cols=CAT_COLS,
        high_card_cols=HIGH_CARD_ID_COLS,
        low_card_override=LOW_CARD_ID_COLS + ["pitcher_hand", "batter_hand"],
        id_cols=[ID], target_col=TARGET,
    )
    train_type_summary.to_csv(os.path.join(OUT_DIR, "data_type_summary.csv"), index=False)
    print(f"train.csv 컬럼 {len(train_type_summary)}개 -> data_type_summary.csv 저장")

    trackman_head = pd.read_csv(os.path.join(DATA_DIR, "trackman_history.csv"),
                                 encoding="utf-8-sig", nrows=200000)
    trackman_type_summary = build_data_type_summary(
        trackman_head, cat_cols=[],
        high_card_cols=["pitcher_trackman_id", "batter_trackman_id"],
        low_card_override=[],
        id_cols=["trackman_id", "trackman_game_id"], target_col=None,
        time_cols=["game_date"],
    )
    trackman_type_summary["note"] = "참고용 — 이번 Phase A~D에서 미사용 (Trackman은 Phase E로 연기)"
    trackman_type_summary.to_csv(
        os.path.join(OUT_DIR, "data_type_summary_trackman.csv"), index=False)
    print(f"trackman_history.csv 컬럼 {len(trackman_type_summary)}개 "
          "(200k행 샘플, 참고용) -> data_type_summary_trackman.csv 저장")
    del trackman_head

    # -------------------------------------------------------------
    # Step 1 — feature build + season-aware shrinkage (exp_003와 동일)
    # -------------------------------------------------------------
    section("Step 1 — 피처 구축 + season-aware shrinkage priors")

    train = build_features(train_raw)
    print("train:", train.shape, "| 피처:", len(ALL_FEATURES))
    print("시즌:", train["season"].min(), "~", train["season"].max())

    train_mask, val_mask = validation.get_main_split(train, val_season=2024)
    train_only = train.loc[train_mask]
    priors = fit_shrinkage_priors(recent_seasons_df(train_only))
    train_shrunk = apply_shrinkage(train, priors)

    X_train = train_shrunk.loc[train_mask, ALL_FEATURES]
    y_train = train_shrunk.loc[train_mask, TARGET]
    X_val = train_shrunk.loc[val_mask, ALL_FEATURES]
    y_val = train_shrunk.loc[val_mask, TARGET]
    print(f"train: {len(X_train)} | val: {len(X_val)}")

    # -------------------------------------------------------------
    # Step 2 — Phase A: 6개 모델
    # -------------------------------------------------------------
    section("Step 2 — Phase A: 모델 6종 학습")

    results = {}

    results["Mean"] = model_factory.fit_mean_baseline(y_train, X_val)
    print(f"[A0 Mean] p={results['Mean'].extra['p']:.4f}")

    feasible, total_unique = model_factory.check_id_cardinality_feasible(
        X_train, HIGH_CARD_ID_COLS, max_unique_sum=5000)
    print(f"[LR cardinality check] pitcher_id+batter_id unique 합계={total_unique} "
          f"(임계값 5000) -> LR-2 {'가능' if feasible else '건너뜀'}")

    results["Logistic_LR1"] = model_factory.fit_logistic_regression(
        X_train, y_train, X_val, y_val, CAT_COLS, LOW_CARD_ID_COLS, HIGH_CARD_ID_COLS,
        ALL_FEATURES, include_high_card_ids=False, seed=SEED)
    print(f"[A1 LR-1] best_C={results['Logistic_LR1'].extra['best_C']} "
          f"C_grid_scores={results['Logistic_LR1'].extra['C_grid_scores']}")

    if feasible:
        results["Logistic_LR2"] = model_factory.fit_logistic_regression(
            X_train, y_train, X_val, y_val, CAT_COLS, LOW_CARD_ID_COLS, HIGH_CARD_ID_COLS,
            ALL_FEATURES, include_high_card_ids=True, seed=SEED)
        print(f"[A1 LR-2] best_C={results['Logistic_LR2'].extra['best_C']} "
              f"C_grid_scores={results['Logistic_LR2'].extra['C_grid_scores']}")
    else:
        results["Logistic_LR2"] = model_factory.ModelResult(
            name="Logistic_LR2", status="skipped:cardinality")

    cat_encoder = model_factory.fit_cat_ordinal_encoder(X_train, CAT_COLS)
    X_train_enc = X_train.copy()
    X_val_enc = X_val.copy()
    X_train_enc[CAT_COLS] = cat_encoder.transform(X_train_enc[CAT_COLS]).astype(int)
    X_val_enc[CAT_COLS] = cat_encoder.transform(X_val_enc[CAT_COLS]).astype(int)

    results["RandomForest"] = model_factory.fit_random_forest(
        X_train_enc, y_train, X_val_enc, y_val, seed=SEED)
    print(f"[A2 RandomForest] train_sec={results['RandomForest'].train_seconds:.1f}s")

    results["ExtraTrees"] = model_factory.fit_extra_trees(
        X_train_enc, y_train, X_val_enc, y_val, seed=SEED)
    print(f"[A3 ExtraTrees] train_sec={results['ExtraTrees'].train_seconds:.1f}s")

    results["CatBoost"] = model_factory.fit_catboost(
        X_train, y_train, X_val, y_val, CAT_COLS, seed=SEED)
    print(f"[A4 CatBoost] train_sec={results['CatBoost'].train_seconds:.1f}s "
          f"best_iter={results['CatBoost'].extra['best_iteration']}")

    # --- 필수 sanity-check gate: exp_003 챔피언 수치를 그대로 재현하는지 ---
    cb_brier, cb_score = metrics.official_score(results["CatBoost"].val_pred, y_val)
    print(f"\n[sanity check] CatBoost brier={cb_brier:.6f} score={cb_score:.2f} "
          f"(exp_003 기록값: brier=0.248000, score=723.17)")
    assert abs(cb_brier - 0.248000) < 1e-6, (
        f"CatBoost sanity check FAILED: brier={cb_brier} (expected 0.248000) — "
        "공유 파이프라인이 exp_003과 다르게 동작하고 있으므로 이후 결과를 신뢰할 수 없음")
    assert abs(cb_score - 723.17) < 0.05, (
        f"CatBoost sanity check FAILED: score={cb_score} (expected 723.17)")
    print("[sanity check] PASSED — 공유 파이프라인이 exp_003을 정확히 재현함, 계속 진행.")

    results["LightGBM"] = model_factory.fit_lightgbm(
        X_train_enc, y_train, X_val_enc, y_val, CAT_COLS, seed=SEED)
    if results["LightGBM"].status == "ok":
        print(f"[A5 LightGBM] train_sec={results['LightGBM'].train_seconds:.1f}s "
              f"best_iter={results['LightGBM'].extra['best_iteration']}")
    else:
        print(f"[A5 LightGBM] 건너뜀: {results['LightGBM'].status} "
              f"({results['LightGBM'].extra.get('error', '')})")

    # -------------------------------------------------------------
    # Step 3 — Phase B: 비교표 + calibration bins + correlation
    # -------------------------------------------------------------
    section("Step 3 — Phase B: 모델 비교표 / calibration / correlation")

    comparison_rows = []
    pred_dict = {}
    for name, r in results.items():
        if r.status != "ok":
            comparison_rows.append({
                "Model": name, "status": r.status, "Brier": np.nan, "Official_Score": np.nan,
                "LogLoss": np.nan, "Calibration_Error": np.nan,
                "Train_sec": np.nan, "Infer_sec": np.nan, "Model_MB": np.nan,
                "pred_mean": np.nan, "pred_std": np.nan, "pred_min": np.nan, "pred_max": np.nan,
            })
            continue
        pred = r.val_pred
        brier, score = metrics.official_score(pred, y_val)
        logloss = metrics.log_loss_safe(pred, y_val)
        cal_err = metrics.expected_calibration_error(pred, y_val)
        pred_dict[name] = pred

        bins_df = metrics.calibration_bins(pred, y_val)
        bins_df.to_csv(os.path.join(OUT_DIR, f"calibration_{name}.csv"), index=False)

        comparison_rows.append({
            "Model": name, "status": "ok", "Brier": brier, "Official_Score": score,
            "LogLoss": logloss, "Calibration_Error": cal_err,
            "Train_sec": r.train_seconds, "Infer_sec": r.infer_seconds, "Model_MB": r.model_mb,
            "pred_mean": float(np.mean(pred)), "pred_std": float(np.std(pred)),
            "pred_min": float(np.min(pred)), "pred_max": float(np.max(pred)),
        })

    comparison_df = pd.DataFrame(comparison_rows).sort_values(
        "Official_Score", ascending=False, na_position="last")
    comparison_df.to_csv(os.path.join(OUT_DIR, "model_comparison.csv"), index=False)
    print(comparison_df.to_string(index=False))

    pred_df = pd.DataFrame(pred_dict)
    corr_df = pred_df.corr(method="pearson")
    corr_df.to_csv(os.path.join(OUT_DIR, "prediction_correlation.csv"))

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr_df.values, vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(len(corr_df.columns)))
    ax.set_xticklabels(corr_df.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr_df.index)))
    ax.set_yticklabels(corr_df.index)
    for i in range(len(corr_df.index)):
        for j in range(len(corr_df.columns)):
            ax.text(j, i, f"{corr_df.values[i, j]:.2f}", ha="center", va="center",
                     color="white" if corr_df.values[i, j] < 0.7 else "black", fontsize=8)
    fig.colorbar(im, ax=ax, label="Pearson correlation")
    ax.set_title("Validation prediction correlation (2024)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "prediction_correlation.png"), dpi=150)
    plt.close(fig)
    print("prediction_correlation.csv / .png 저장 완료")

    # -------------------------------------------------------------
    # Step 4 — Phase C: 블렌드 탐색
    # -------------------------------------------------------------
    section("Step 4 — Phase C: 가중 확률 블렌드 탐색")

    candidates = ensemble.select_blend_candidates(comparison_df, corr_df, top_k=3)
    print(f"블렌드 후보: {candidates}")

    best_weights, best_brier, best_score = ensemble.coarse_fine_blend_search(
        pred_dict, y_val, candidates)
    print(f"최적 블렌드 weights={best_weights} brier={best_brier:.6f} score={best_score:.2f}")

    constituent_scores = [comparison_df.set_index("Model").loc[c, "Official_Score"]
                           for c in candidates]
    if best_score < max(constituent_scores) - 1.0:
        print(f"[경고] 블렌드 점수({best_score:.2f})가 최고 구성모델({max(constituent_scores):.2f})보다 "
              "뚜렷이 낮음 — blend_predict 배선 버그 가능성, 재확인 필요")

    blend_rows = [{"model": name, "weight": w} for name, w in best_weights.items()]
    blend_rows.append({"model": "_summary_brier", "weight": best_brier})
    blend_rows.append({"model": "_summary_official_score", "weight": best_score})
    pd.DataFrame(blend_rows).to_csv(os.path.join(OUT_DIR, "best_blend.csv"), index=False)

    # -------------------------------------------------------------
    # Step 5 — Phase D: calibration (leak-free two-stage)
    # -------------------------------------------------------------
    section("Step 5 — Phase D: calibration (2019-2022 fit / 2023 calibrate / 2024 eval)")

    fit_mask, calib_mask, eval_mask = validation.get_calibration_split(
        train_shrunk, calib_season=2023, val_season=2024)
    print(f"fit(2019-2022)={fit_mask.sum()} | calib(2023)={calib_mask.sum()} | "
          f"eval(2024)={eval_mask.sum()} (== val_mask: {(eval_mask == val_mask).all()})")

    def make_catboost_train_fn():
        return lambda Xf, yf, Xc, yc: model_factory.fit_catboost(Xf, yf, Xc, yc, CAT_COLS, seed=SEED)

    def make_encoded_train_fn(fit_fn):
        def _fn(Xf, yf, Xc, yc):
            enc = model_factory.fit_cat_ordinal_encoder(Xf, CAT_COLS)
            Xf_enc, Xc_enc = Xf.copy(), Xc.copy()
            Xf_enc[CAT_COLS] = enc.transform(Xf_enc[CAT_COLS]).astype(int)
            Xc_enc[CAT_COLS] = enc.transform(Xc_enc[CAT_COLS]).astype(int)
            return fit_fn(Xf_enc, yf, Xc_enc, yc, seed=SEED)
        return _fn

    def make_logistic_train_fn(include_high_card_ids):
        return lambda Xf, yf, Xc, yc: model_factory.fit_logistic_regression(
            Xf, yf, Xc, yc, CAT_COLS, LOW_CARD_ID_COLS, HIGH_CARD_ID_COLS,
            ALL_FEATURES, include_high_card_ids=include_high_card_ids, seed=SEED)

    TRAIN_FN_BY_MODEL = {
        "CatBoost": make_catboost_train_fn(),
        "RandomForest": make_encoded_train_fn(model_factory.fit_random_forest),
        "ExtraTrees": make_encoded_train_fn(model_factory.fit_extra_trees),
        "LightGBM": make_encoded_train_fn(
            lambda Xt, yt, Xv, yv, seed: model_factory.fit_lightgbm(Xt, yt, Xv, yv, CAT_COLS, seed=seed)),
        "Logistic_LR1": make_logistic_train_fn(False),
        "Logistic_LR2": make_logistic_train_fn(True),
    }

    best_standalone_name = comparison_df[comparison_df["Model"] != "Mean"].iloc[0]["Model"]
    print(f"최고 단일 모델: {best_standalone_name}")

    models_to_calibrate = sorted(set([best_standalone_name] + list(best_weights.keys())))
    calib_results = {}
    for name in models_to_calibrate:
        if name not in TRAIN_FN_BY_MODEL:
            print(f"[calibration] {name}: train_fn 없음, 건너뜀")
            continue
        print(f"[calibration] {name} 2단계 calibration 실행 중...")
        out = calibration.run_two_stage_calibration(
            name, TRAIN_FN_BY_MODEL[name], train_shrunk, ALL_FEATURES, TARGET,
            fit_mask, calib_mask, pred_dict[name], y_val, seed=SEED)
        calib_results[name] = out
        for method in ("raw", "platt", "isotonic"):
            m = out[method]
            print(f"  {name}/{method}: brier={m['brier']:.6f} score={m['official_score']:.2f} "
                  f"cal_err={m['calibration_error']:.4f}")

    summary_rows = []
    for name, out in calib_results.items():
        for method in ("raw", "platt", "isotonic"):
            m = out[method]
            summary_rows.append({
                "target": "standalone" if name == best_standalone_name else "blend_constituent",
                "model": name, "method": method,
                "brier": m["brier"], "official_score": m["official_score"],
                "calibration_error": m["calibration_error"],
            })

    if all(name in calib_results for name in best_weights):
        for method in ("raw", "platt", "isotonic"):
            combined_pred = ensemble.blend_predict(
                {name: calib_results[name][method]["pred"] for name in best_weights}, best_weights)
            brier, score = metrics.official_score(combined_pred, y_val)
            summary_rows.append({
                "target": "blend", "model": "+".join(best_weights.keys()), "method": method,
                "brier": brier, "official_score": score,
                "calibration_error": metrics.expected_calibration_error(combined_pred, y_val),
            })

    pd.DataFrame(summary_rows).to_csv(os.path.join(OUT_DIR, "calibration_summary.csv"), index=False)
    print("calibration_summary.csv 저장 완료")

    # -------------------------------------------------------------
    # Step 6 — model/ 디렉터리 무결성 확인
    # -------------------------------------------------------------
    section("Step 6 — model/ 디렉터리 변경 여부 확인 (변경되면 안 됨)")
    for fname in ("catboost_model.cbm", "model_meta.pkl"):
        path = os.path.join(MODEL_DIR, fname)
        if os.path.exists(path):
            print(f"{path}: mtime={time.ctime(os.path.getmtime(path))} (스크립트가 이 파일을 쓴 적 없음)")
        else:
            print(f"{path}: 없음")

    print("\n완료. reports/model_selection/*.csv, *.png 를 바탕으로 "
          "experiments/exp_006_model_selection.md 를 작성하라.")


if __name__ == "__main__":
    main()
