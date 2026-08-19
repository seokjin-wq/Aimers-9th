"""exp_003 — EDA-driven feature additions (reports/eda_group1-5,
reports/eda_final) + season-aware shrinkage priors + LightGBM vs
CatBoost model comparison.

This run bundles three changes at once (documented explicitly as a
deviation from the usual single-change discipline — see
experiments/exp_003_eda_features_and_model.md "실험 설계" for why):
  1. New features.py derived columns (same_hand_x_breaking_rate,
     same_hand_x_offspeed_rate, three_ball_x_risp,
     shrunk_pitcher_x_batter_success) + batter shrinkage k 50->150.
  2. Season-aware shrinkage priors: fit on the most recent 2 seasons
     of the training split instead of the full training split (2024
     is the real season 2025 is closest to; a 2019-2023 average prior
     pulls cold-start predictions toward a stale, higher baseline —
     reports/eda_final §E/§F).
  3. Model comparison: LightGBM (exp_001/exp_002's model, unchanged
     hyperparameters) vs CatBoost (native categorical handling, no
     OrdinalEncoder needed) on the *same* exp_003 feature set.

Validation: season 2019-2023 train / season 2024 held out (matches the
official baseline, CLAUDE.md "Validation Policy"). Whichever model
wins on validation is refit on the full 2019-2024 train.csv and saved
for packaging into a submission.
"""

import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import catboost as cb
import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRUNK_COLS,
    POST_SHRINKAGE_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"

ID = "row_id"
TARGET = "control_success"
RECENT_SEASONS_FOR_PRIOR = 2

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"),
                         encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
ALL_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS + POST_SHRINKAGE_COLS


def recent_seasons_df(df, n=RECENT_SEASONS_FOR_PRIOR):
    seasons = sorted(df["season"].unique())
    recent = seasons[-n:]
    return df[df["season"].isin(recent)]


def official_score(pred, y):
    r = y.mean()
    brier = ((pred - y) ** 2).mean()
    baseline_brier = r * (1 - r)
    score = max(0, 100000 * (1 - brier / baseline_brier))
    return brier, score


train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"),
                     encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
train = build_features(train)

print("train:", train.shape, "| 피처:", len(ALL_FEATURES),
      f"(범주형 {len(CAT_COLS)}, 파생 {len(DERIVED_COLS)}, shrinkage {len(SHRUNK_COLS)}, "
      f"post-shrinkage {len(POST_SHRINKAGE_COLS)})")
print("시즌:", train["season"].min(), "~", train["season"].max())
print(f"제구 성공률: {train[TARGET].mean():.4f}")

is_val = train["season"] == 2024

# Season-aware shrinkage prior (exp_003 변경점 2). fit_shrinkage_priors는
# 여전히 학습 스플릿에서만 계산하지만(누수 방지), 학습 스플릿 "전체"
# 평균 대신 학습 스플릿의 "최근 N시즌" 평균만 쓴다.
train_only = train.loc[~is_val]
val_prior_seasons = sorted(train_only["season"].unique())[-RECENT_SEASONS_FOR_PRIOR:]
print(f"\nval_priors 계산에 쓴 시즌: {val_prior_seasons} (train split={sorted(train_only['season'].unique())})")
val_priors_full = fit_shrinkage_priors(train_only)
val_priors_recent = fit_shrinkage_priors(recent_seasons_df(train_only))
print("prior 비교 (전체 학습기간 평균 vs 최근 시즌 평균), 대표 3개 컬럼:")
for rate_col in list(val_priors_full)[:3]:
    print(f"  {rate_col}: full={val_priors_full[rate_col]:.4f} -> recent={val_priors_recent[rate_col]:.4f}")

train_shrunk = apply_shrinkage(train, val_priors_recent)

X_train, y_train = train_shrunk.loc[~is_val, ALL_FEATURES], train_shrunk.loc[~is_val, TARGET]
X_val, y_val = train_shrunk.loc[is_val, ALL_FEATURES], train_shrunk.loc[is_val, TARGET]
print("train:", len(X_train), "| val:", len(X_val))

lgb_params = dict(
    objective="binary",
    metric="binary_logloss",
    n_estimators=2000,
    learning_rate=0.03,
    num_leaves=63,
    subsample=0.8,
    subsample_freq=1,
    colsample_bytree=0.8,
    min_child_samples=200,
    random_state=42,
    n_jobs=-1,
)

print("\n" + "=" * 80)
print("1) LightGBM + exp_003 피처셋 + season-aware shrinkage")
print("=" * 80)

cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
X_train_lgb = X_train.copy()
X_val_lgb = X_val.copy()
X_train_lgb[CAT_COLS] = cat_encoder.fit_transform(X_train_lgb[CAT_COLS]).astype(int)
X_val_lgb[CAT_COLS] = cat_encoder.transform(X_val_lgb[CAT_COLS]).astype(int)

# 이 환경에서 lightgbm 4.7.0이 완전히 합성된(프로젝트 코드와 무관한)
# 최소 재현 예제에서도 OSError(access violation)로 죽는 것을 확인함
# (numpy 재설치까지 시도했으나 재현됨 — 환경/DLL 수준 문제로 판단,
# exp_001/exp_002 당시엔 정상 동작했던 것과 달리 지금 이 세션에서
# 새로 깨진 것으로 보임). 여기서 죽어도 실험 전체가 멈추지 않도록
# try/except로 감싸고, 실패하면 LightGBM 비교는 건너뛴다.
lgb_clf = None
lgb_score = None
lgb_time = None
try:
    t = time.time()
    lgb_clf = lgb.LGBMClassifier(**lgb_params)
    lgb_clf.fit(
        X_train_lgb, y_train,
        eval_set=[(X_val_lgb, y_val)],
        categorical_feature=CAT_COLS,
        callbacks=[lgb.early_stopping(100), lgb.log_evaluation(200)],
    )
    lgb_time = time.time() - t
    print(f"학습 완료 :: {lgb_time:.1f}s | best_iteration={lgb_clf.best_iteration_}")

    lgb_val_pred = lgb_clf.predict_proba(X_val_lgb)[:, 1]
    lgb_brier, lgb_score = official_score(lgb_val_pred, y_val)
    print(f"[LightGBM] Brier: {lgb_brier:.6f} | Validation Score: {lgb_score:.2f}")
    print(f"pred mean/min/max: {lgb_val_pred.mean():.4f} / {lgb_val_pred.min():.4f} / {lgb_val_pred.max():.4f}")
except OSError as e:
    print(f"[LightGBM] 학습 실패 (환경 레벨 네이티브 크래시, 이 실험과 무관한 환경 문제로 판단): {e}")
    print("[LightGBM] 이 비교에서는 건너뛰고 CatBoost 결과로만 진행한다.")

print("\n" + "=" * 80)
print("2) CatBoost + exp_003 피처셋 + season-aware shrinkage (동일 피처)")
print("=" * 80)

cb_params = dict(
    iterations=2000,
    learning_rate=0.03,
    depth=6,
    l2_leaf_reg=3.0,
    loss_function="Logloss",
    eval_metric="Logloss",
    random_seed=42,
    thread_count=-1,
    verbose=200,
)

cb_train_pool = cb.Pool(X_train, y_train, cat_features=CAT_COLS)
cb_val_pool = cb.Pool(X_val, y_val, cat_features=CAT_COLS)

t = time.time()
cb_clf = cb.CatBoostClassifier(**cb_params)
cb_clf.fit(cb_train_pool, eval_set=cb_val_pool, early_stopping_rounds=100)
cb_time = time.time() - t
print(f"학습 완료 :: {cb_time:.1f}s | best_iteration={cb_clf.get_best_iteration()}")

cb_val_pred = cb_clf.predict_proba(X_val)[:, 1]
cb_brier, cb_score = official_score(cb_val_pred, y_val)
print(f"[CatBoost] Brier: {cb_brier:.6f} | Validation Score: {cb_score:.2f}")
print(f"pred mean/min/max: {cb_val_pred.mean():.4f} / {cb_val_pred.min():.4f} / {cb_val_pred.max():.4f}")

print("\n" + "=" * 80)
print("3) 모델 비교 요약")
print("=" * 80)
print(f"exp_002 (LightGBM, 구 피처셋, 참고용 기록값): local score 706.28 (Brier 0.248043)")
if lgb_score is not None:
    print(f"exp_003 LightGBM (신규 피처셋 + season-aware shrinkage): local score {lgb_score:.2f} (Brier {lgb_brier:.6f}), {lgb_time:.1f}s")
else:
    print("exp_003 LightGBM: 이 환경에서 학습 실패(네이티브 크래시) — 비교 불가")
print(f"exp_003 CatBoost (신규 피처셋 + season-aware shrinkage): local score {cb_score:.2f} (Brier {cb_brier:.6f}), {cb_time:.1f}s")

if lgb_score is None:
    winner = "catboost"
else:
    winner = "catboost" if cb_score > lgb_score else "lightgbm"
print(f"\n선택된 모델: {winner}" + (" (검증 점수 기준)" if lgb_score is not None else " (LightGBM 학습 실패로 인한 자동 선택)"))

# 오류 분석 (선택된 모델 기준)
val_pred_final = cb_val_pred if winner == "catboost" else lgb_val_pred
val_seg = train_shrunk.loc[is_val, ["two_strike", "is_close_game", "asof_pitcher_n"]].copy()
val_seg["pred"] = val_pred_final
val_seg["y"] = y_val.values
val_seg["cold_start"] = val_seg["asof_pitcher_n"] < 50

print(f"\n오류 분석 ({winner} 기준, 구간별 Brier, n, 실제 성공률 vs 평균 예측):")
segments = {
    "two_strike=1": val_seg["two_strike"] == 1,
    "two_strike=0": val_seg["two_strike"] == 0,
    "is_close_game=1": val_seg["is_close_game"] == 1,
    "is_close_game=0": val_seg["is_close_game"] == 0,
    "cold_start(n<50)": val_seg["cold_start"],
    "warm(n>=50)": ~val_seg["cold_start"],
}
for name, mask in segments.items():
    sub = val_seg.loc[mask]
    seg_brier = ((sub["pred"] - sub["y"]) ** 2).mean()
    print(f"  {name}: n={len(sub)}, brier={seg_brier:.6f}, "
          f"실제 성공률={sub['y'].mean():.4f}, 평균예측={sub['pred'].mean():.4f}")

if winner == "catboost":
    top_importance = sorted(
        zip(ALL_FEATURES, cb_clf.get_feature_importance(cb_train_pool)), key=lambda x: -x[1]
    )[:15]
else:
    top_importance = sorted(
        zip(ALL_FEATURES, lgb_clf.feature_importances_), key=lambda x: -x[1]
    )[:15]
print(f"\nTop 15 feature importance ({winner}):")
for name, imp in top_importance:
    print(f"  {name}: {imp:.1f}" if isinstance(imp, float) else f"  {name}: {imp}")

print("\n" + "=" * 80)
print("4) 전체 데이터(2019-2024) 최종 재학습")
print("=" * 80)

final_prior_seasons = sorted(train["season"].unique())[-RECENT_SEASONS_FOR_PRIOR:]
print(f"final_priors 계산에 쓴 시즌: {final_prior_seasons}")
final_priors = fit_shrinkage_priors(recent_seasons_df(train))
train_final = apply_shrinkage(train, final_priors)

os.makedirs(MODEL_DIR, exist_ok=True)

if winner == "lightgbm":
    final_cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    train_final_enc = train_final.copy()
    train_final_enc[CAT_COLS] = final_cat_encoder.fit_transform(train_final_enc[CAT_COLS]).astype(int)

    final_params = dict(lgb_params)
    final_params["n_estimators"] = lgb_clf.best_iteration_
    final_clf = lgb.LGBMClassifier(**final_params)
    t = time.time()
    final_clf.fit(train_final_enc[ALL_FEATURES], train_final_enc[TARGET], categorical_feature=CAT_COLS)
    print(f"최종 재학습 완료(LightGBM) :: {time.time() - t:.1f}s")

    final_clf.booster_.save_model(os.path.join(MODEL_DIR, "lgbm_booster.txt"))
    joblib.dump(
        {
            "model_type": "lightgbm",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "cat_cols": CAT_COLS,
            "cat_encoder": final_cat_encoder,
            "shrinkage_priors": final_priors,
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장 완료: {MODEL_DIR}/lgbm_booster.txt, {MODEL_DIR}/model_meta.pkl")
else:
    final_params = dict(cb_params)
    final_params["iterations"] = cb_clf.get_best_iteration() + 1
    final_clf = cb.CatBoostClassifier(**final_params)
    final_train_pool = cb.Pool(train_final[ALL_FEATURES], train_final[TARGET], cat_features=CAT_COLS)
    t = time.time()
    final_clf.fit(final_train_pool)
    print(f"최종 재학습 완료(CatBoost) :: {time.time() - t:.1f}s")

    final_clf.save_model(os.path.join(MODEL_DIR, "catboost_model.cbm"))
    joblib.dump(
        {
            "model_type": "catboost",
            "base_features": BASE_FEATURES,
            "all_features": ALL_FEATURES,
            "cat_cols": CAT_COLS,
            "shrinkage_priors": final_priors,
        },
        os.path.join(MODEL_DIR, "model_meta.pkl"),
        compress=3,
    )
    print(f"저장 완료: {MODEL_DIR}/catboost_model.cbm, {MODEL_DIR}/model_meta.pkl")

print("\n완료.")
