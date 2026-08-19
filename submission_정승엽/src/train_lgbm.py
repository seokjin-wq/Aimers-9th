"""exp_002 — baseline features + exp_001/exp_002 derived features
(incl. cold-start shrinkage) + LightGBM (model/hyperparameters unchanged
from exp_001, per exp_002's single-change discipline: only the feature
set changed this round).

Validation: season 2019-2023 train / season 2024 held out (matches the
official baseline, see CLAUDE.md "Validation Policy"). After validation,
refits on the full 2019-2024 train.csv and saves the model for
packaging into a submission.
"""

import os
import time

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from features import (
    CAT_COLS,
    DERIVED_COLS,
    SHRUNK_COLS,
    apply_shrinkage,
    build_features,
    fit_shrinkage_priors,
)

DATA_DIR = "./data"
MODEL_DIR = "./model"

ID = "row_id"
TARGET = "control_success"

test_cols = pd.read_csv(os.path.join(DATA_DIR, "test.csv"),
                         encoding="utf-8-sig", nrows=0).columns
BASE_FEATURES = [c for c in test_cols if c != ID]
ALL_FEATURES = BASE_FEATURES + DERIVED_COLS + SHRUNK_COLS

train = pd.read_csv(os.path.join(DATA_DIR, "train.csv"),
                     encoding="utf-8-sig", usecols=BASE_FEATURES + [TARGET])
train = build_features(train)

# category dtype 대신 정수 인코딩 사용: pandas category dtype을 LightGBM에
# 그대로 넘기면 소량 배치 추론에서 네이티브 크래시(access violation)가
# 재현됨 (Windows, lightgbm 4.7.0). OrdinalEncoder로 정수 인코딩한 뒤
# categorical_feature로 LightGBM에 알려주면 범주형 분할은 그대로 활용하면서
# 이 문제를 피할 수 있다.
cat_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
train[CAT_COLS] = cat_encoder.fit_transform(train[CAT_COLS]).astype(int)

print("train:", train.shape, "| 피처:", len(ALL_FEATURES),
      f"(범주형 {len(CAT_COLS)}, 파생 {len(DERIVED_COLS)}, shrinkage {len(SHRUNK_COLS)})")
print("시즌:", train["season"].min(), "~", train["season"].max())
print(f"제구 성공률: {train[TARGET].mean():.4f}")

is_val = train["season"] == 2024

# Cold-start shrinkage priors (features.py의 fit_shrinkage_priors)는 반드시
# 학습 스플릿에서만 계산한다 — 검증용 실행이므로 2019-2023만 사용
# (2024 val 통계가 "학습에서 유래한" 피처로 새어 들어가면 검증 점수가
# 부정확하게 부풀려짐).
val_priors = fit_shrinkage_priors(train.loc[~is_val])
train_shrunk = apply_shrinkage(train, val_priors)

X_train, y_train = train_shrunk.loc[~is_val, ALL_FEATURES], train_shrunk.loc[~is_val, TARGET]
X_val, y_val = train_shrunk.loc[is_val, ALL_FEATURES], train_shrunk.loc[is_val, TARGET]
print("train:", len(X_train), "| val:", len(X_val))

params = dict(
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

t = time.time()
clf = lgb.LGBMClassifier(**params)
clf.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    categorical_feature=CAT_COLS,
    callbacks=[lgb.early_stopping(100), lgb.log_evaluation(200)],
)
print(f"학습 완료 :: {time.time() - t:.1f}s | best_iteration={clf.best_iteration_}")

val_pred = clf.predict_proba(X_val)[:, 1]
r = y_val.mean()
brier = ((val_pred - y_val) ** 2).mean()
baseline_brier = r * (1 - r)
score = max(0, 100000 * (1 - brier / baseline_brier))

print(f"Brier: {brier:.6f} | 기준선 r(1-r): {baseline_brier:.6f}")
print(f"Validation Score: {score:.2f}")
print(f"pred mean/min/max: {val_pred.mean():.4f} / {val_pred.min():.4f} / {val_pred.max():.4f}")

# 오류 분석: 상황별로 예측이 특히 나쁜 구간이 있는지 확인 (워크플로우
# 7단계). 각 구간의 Brier와 전체 기준선 대비 상대 점수를 같이 본다.
val_seg = train_shrunk.loc[is_val, ["two_strike", "is_close_game", "asof_pitcher_n"]].copy()
val_seg["pred"] = val_pred
val_seg["y"] = y_val.values
val_seg["cold_start"] = val_seg["asof_pitcher_n"] < 50  # shrinkage k와 동일 기준

print("오류 분석 (구간별 Brier, n, 실제 성공률 vs 평균 예측):")
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

top_importance = sorted(
    zip(ALL_FEATURES, clf.feature_importances_), key=lambda x: -x[1]
)[:15]
print("Top 15 feature importance:")
for name, imp in top_importance:
    print(f"  {name}: {imp}")

# 전체 데이터(2019~2024)로 최종 재학습, best_iteration 고정.
# 제출용 모델이므로 shrinkage prior도 전체 2019-2024로 다시 fit —
# 이제는 전체가 "학습 데이터"이므로 val_priors를 재사용하지 않는다
# (val_priors는 2019-2023만 봤으므로 2024 시즌 정보가 반영 안 됨).
final_priors = fit_shrinkage_priors(train)
print("shrinkage prior 확인 (val_priors 2019-2023 vs final_priors 2019-2024):")
for rate_col in list(val_priors)[:3]:
    print(f"  {rate_col}: {val_priors[rate_col]:.4f} -> {final_priors[rate_col]:.4f}")
train_final = apply_shrinkage(train, final_priors)

final_params = dict(params)
final_params["n_estimators"] = clf.best_iteration_
final_clf = lgb.LGBMClassifier(**final_params)

t = time.time()
final_clf.fit(train_final[ALL_FEATURES], train_final[TARGET], categorical_feature=CAT_COLS)
print(f"최종 재학습 완료 :: {time.time() - t:.1f}s")

os.makedirs(MODEL_DIR, exist_ok=True)

# LightGBM 네이티브 포맷으로 저장. joblib/pickle로 LGBMClassifier(sklearn
# 래퍼)를 통째로 저장했다가 다른 프로세스에서 로드하면 이 환경
# (Windows, lightgbm 4.7.0)에서 네이티브 크래시(access violation)가
# 재현되는 걸 확인함 (Booster의 C 핸들이 unpickle 시 제대로 복원되지 않는
# 것으로 보임). booster.save_model()/lgb.Booster(model_file=...)는
# 문제없이 동작하므로 이 방식을 사용.
final_clf.booster_.save_model(os.path.join(MODEL_DIR, "lgbm_booster.txt"))
joblib.dump(
    {
        "base_features": BASE_FEATURES,
        "all_features": ALL_FEATURES,
        "cat_cols": CAT_COLS,
        "cat_encoder": cat_encoder,
        "shrinkage_priors": final_priors,
    },
    os.path.join(MODEL_DIR, "lgbm_meta.pkl"),
    compress=3,
)
print(f"저장 완료: {MODEL_DIR}/lgbm_booster.txt, {MODEL_DIR}/lgbm_meta.pkl")
