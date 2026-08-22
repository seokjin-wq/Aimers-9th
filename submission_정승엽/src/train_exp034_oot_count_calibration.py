"""exp_034 -- second calibration layer: count-state OOT residual
correction, applied BEFORE the existing count-trend layer. See
experiments/exp_034_oot_count_calibration.md.

Step 1: train a CatBoost model on 2019-2022 only, predict 2023 (genuine
out-of-time -- this model has never seen 2023 or 2024). Compute
residual = y_2023 - raw_pred_2023, center by subtracting the overall
2023 mean residual (single season, so "centering by season" reduces to
subtracting one scalar -- absorbs the same global-bias component step1
Platt would otherwise correct for), group by (balls_before,
strikes_before), shrinkage-aggregate with group_shrinkage=500.

Step 2: apply that offset AS-IS (no extrapolation -- this is a static
per-group correction, unlike the OLS-trend layer) to exp_030's actual
2024 predictions (reusing the exp_027 cached val predictions, exactly
what train_exp030_repro.py scores against 875.00), on top of the
existing step1 Platt + count-trend chain, and see if the combined
score beats 875.00.
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from exp030_baseline import build_holdout_split
from features import CAT_COLS
from metrics import official_score
from model_factory import fit_catboost
from train_exp029_count_trend import GROUP_COLS, TREND_STRENGTH, apply_group_trend, compute_group_trend

DATA_DIR = "./data"
WEIGHT_2024 = 100.0
RESIDUAL_SHRINKAGE = 500.0
RESIDUAL_SCALE = 1.0


def fit_platt_weighted(raw_pred, y, sample_weight, seed=42):
    raw_pred = np.asarray(raw_pred, dtype=float).reshape(-1, 1)
    clf = LogisticRegression(random_state=seed)
    clf.fit(raw_pred, y, sample_weight=sample_weight)
    return clf


def compute_oot_offset(residual_df, group_cols=GROUP_COLS,
                        shrinkage=RESIDUAL_SHRINKAGE, scale=RESIDUAL_SCALE):
    """residual_df must have columns group_cols + ['centered_residual'].
    offset[group] = scale * sum(centered_residual) / (count + shrinkage)."""
    grp = residual_df.groupby(group_cols)["centered_residual"].agg(["sum", "count"])
    grp["offset"] = scale * grp["sum"] / (grp["count"] + shrinkage)
    return grp["offset"].to_dict()


def apply_offset(df, offset, group_cols=GROUP_COLS):
    keys = list(zip(*[df[c] for c in group_cols])) if len(group_cols) > 1 else df[group_cols[0]].tolist()
    return np.array([offset.get(k, 0.0) for k in keys])


def main():
    print("=" * 80)
    print("1. OOT 서브모델: 2019-2022 학습 -> 2023 예측 (진짜 out-of-time)")
    print("=" * 80)
    X_train, y_train, X_val, y_val, _ = build_holdout_split(val_season=2023, max_train_season=2022)
    print(f"train(2019-2022)={X_train.shape}, val(2023, OOT)={X_val.shape}")

    res_oot = fit_catboost(X_train, y_train, X_val, y_val, CAT_COLS, seed=42, name="CatBoost-OOT-2022")
    print(f"best_iter={res_oot.extra['best_iteration']}")
    raw_brier, raw_score = official_score(res_oot.val_pred, y_val)
    print(f"[2023 OOT raw] Brier={raw_brier:.6f} | score={raw_score:.2f}")

    print()
    print("=" * 80)
    print("2. count-state별 잔차 offset 계산 (중앙화 + shrinkage=500)")
    print("=" * 80)
    residual = y_val.to_numpy() - res_oot.val_pred
    centered_residual = residual - residual.mean()  # 단일 시즌(2023)이라 전체평균 하나만 뺌
    group_df = pd.DataFrame({c: X_val[c].to_numpy() for c in GROUP_COLS})
    group_df["centered_residual"] = centered_residual
    oot_offset = compute_oot_offset(group_df)
    for k, v in sorted(oot_offset.items()):
        print(f"  {GROUP_COLS}={k}: offset={v:+.5f}")

    print()
    print("=" * 80)
    print("3. exp_030 실제 2024 예측에 적용해서 검증 (exp_027 캐시 재사용)")
    print("=" * 80)
    npz42 = np.load("./output/exp027_oof_cache_seed42.npz")
    npz1 = np.load("./output/exp027_oof_cache_seed1.npz")
    oof_2319 = (npz42["pred"] + npz1["pred"]) / 2
    y_2319 = npz42["y"]
    val_pred_42 = np.load("./output/exp027_val_pred_seed42.npy")
    val_pred_1 = np.load("./output/exp027_val_pred_seed1.npy")
    val_raw_2024 = (val_pred_42 + val_pred_1) / 2

    train_full = pd.read_csv(f"{DATA_DIR}/train.csv", encoding="utf-8-sig",
                              usecols=["season", "control_success"] + GROUP_COLS)
    y_2024 = train_full.loc[train_full["season"] == 2024, "control_success"].to_numpy()

    p_combo = np.concatenate([oof_2319, val_raw_2024])
    y_combo = np.concatenate([y_2319, y_2024])
    sw = np.concatenate([np.ones(len(oof_2319)), np.full(len(val_raw_2024), WEIGHT_2024)])
    calibrator = fit_platt_weighted(p_combo, y_combo, sample_weight=sw)
    oof_calibrated = calibrator.predict_proba(oof_2319.reshape(-1, 1))[:, 1]
    val_calibrated_2024 = calibrator.predict_proba(val_raw_2024.reshape(-1, 1))[:, 1]
    step1_brier, step1_score = official_score(val_calibrated_2024, y_2024)
    print(f"[step1 only] score={step1_score:.2f}")

    train_2319 = train_full.loc[train_full["season"] < 2024].reset_index(drop=True)
    train_2319 = train_2319.copy()
    train_2319["residual"] = y_2319 - oof_calibrated
    train_2319["centered_residual"] = (
        train_2319["residual"] - train_2319["season"].map(train_2319.groupby("season")["residual"].mean())
    )
    train_2024 = train_full.loc[train_full["season"] == 2024].reset_index(drop=True)
    trend_2319_only = compute_group_trend(train_2319, target_season=2024)
    trend_correction_2024 = apply_group_trend(train_2024, trend_2319_only)
    pred_with_trend = np.clip(val_calibrated_2024 + TREND_STRENGTH * trend_correction_2024, 0.0, 1.0)
    trend_brier, trend_score = official_score(pred_with_trend, y_2024)
    print(f"[step1 + count-trend] score={trend_score:.2f} (= exp_030_repro 기준선)")

    oot_correction_2024 = apply_offset(train_2024, oot_offset)
    pred_with_oot_and_trend = np.clip(
        val_calibrated_2024 + oot_correction_2024 + TREND_STRENGTH * trend_correction_2024, 0.0, 1.0)
    final_brier, final_score = official_score(pred_with_oot_and_trend, y_2024)
    print(f"[step1 + OOT잔차 + count-trend] score={final_score:.2f}")

    print()
    print("=" * 80)
    print("결과 요약")
    print("=" * 80)
    print(f"  exp_030_repro 기준선(step1+count-trend)     = {trend_score:.2f}")
    print(f"  + OOT 잔차 보정 추가                         = {final_score:.2f}")
    print(f"  Δ(OOT 잔차 보정 단독 기여)                   = {final_score - trend_score:+.2f}")
    print("완료.")


if __name__ == "__main__":
    main()
