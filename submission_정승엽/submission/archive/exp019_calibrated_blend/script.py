# script.py — exp_003: baseline + exp_001/exp_002/exp_003 derived
# features (cold-start shrinkage 포함) + LightGBM 또는 CatBoost.
# model/model_meta.pkl의 "model_type"에 따라 실제 학습된 모델만 쓴다.
#
# lightgbm을 반드시 다른 어떤 import보다도(특히 pandas보다) 먼저
# import한다 -- 이 환경(Windows)에서 pandas(또는 catboost)가 먼저
# import/사용된 뒤 lightgbm을 쓰면 데이터 내용과 무관하게 access
# violation으로 크래시하는 DLL 로드순서 충돌이 있음(2026-08-21,
# exp_013 아카이브 격리 테스트 중 재발견 -- "lightgbm 네이티브 호출을
# catboost보다 먼저 하면 된다"는 이전 진단은 불충분했고, 진짜 원인은
# "lightgbm이 pandas보다 먼저 import돼야 한다"였음). model_type이
# lightgbm을 안 쓰는 아카이브(catboost 단독 등)에도 항상 붙지만,
# import 자체는 가벼워 설치/실행 시간에 미치는 영향은 무시할 만함.
import lightgbm as lgb

import os
import sys

import joblib
import numpy as np
import pandas as pd

# 피처 로직은 src/features.py 원본을 그대로 사용한다 (더 이상 손으로
# 복붙해서 동기화하지 않음). Dacon 공식 zip 구조(model/, script.py,
# requirements.txt만 최상위)를 그대로 지키기 위해, src/package_submission.py가
# features.py를 zip 루트가 아니라 model/ 폴더 안에 넣어둔다. script.py의
# 실행 위치(cwd)와 무관하게 항상 자기 자신 파일 기준 상대경로로
# model/ 을 찾아 sys.path에 추가해야 어디서 실행해도 import가 된다.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_SCRIPT_DIR, "model"))
from features import CAT_COLS, apply_shrinkage, build_features

ID_COL = "row_id"
TARGET_COL = "control_success"


# =======================
# 데이터 로드 유틸
# =======================

def load_test(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    if ID_COL not in df.columns:
        raise ValueError(f"test 데이터에 {ID_COL} 컬럼이 없음: {list(df.columns)[:5]}")
    return df


def load_sample_submission(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    if list(df.columns[:2]) != [ID_COL, TARGET_COL]:
        raise ValueError(
            f"sample_submission 컬럼이 ({ID_COL}, {TARGET_COL})이 아님: "
            f"{list(df.columns)}")
    return df


# =======================
# 추론용 피처 파이프라인
# =======================

def attach_trackman_features(df, trackman_lookup, trackman_cols, league_fallback):
    """exp_007: pitcher_id -> trackman_*_asof를 평평한 lookup 테이블로
    붙인다. `data/trackman_history.csv`나 `merge_asof` 없이, 미리 계산해
    zip에 넣어둔 `model/trackman_pitcher_lookup.csv`만 읽는다 — 평가
    데이터는 항상 season 2025뿐이고, Phase 2 매핑된 모든 투수가 이
    lookup 하나로 "2019-2024 전체 이력" 값에 귀결되기 때문(학습 스크립트
    `src/trackman_pitcher_features.build_test_time_pitcher_lookup` 참고).
    lookup에 아예 없는 pitcher_id(훈련 데이터에 없던 2025 신인 등)는
    리그 전체 폴백 상수로 채운다."""
    df = df.merge(trackman_lookup, on="pitcher_id", how="left")
    for col in trackman_cols:
        df[col] = df[col].fillna(league_fallback[col])
    return df


def build_features_for_inference(df, shrinkage_priors, trackman_lookup, trackman_cols,
                                  trackman_league_fallback, cat_encoder=None):
    """row_id 제거 + src/features.py의 build_features/apply_shrinkage +
    exp_007 trackman 투수 단위 피처. 다른 행 정보는 쓰지 않음.

    cat_encoder가 주어지면(LightGBM) 학습 때와 동일한 인코더로 범주형을
    정수 인코딩한다 (category dtype은 소량 배치 추론에서 LightGBM 네이티브
    크래시를 일으켜 사용하지 않음). CatBoost는 원본 문자열 범주형을 그대로
    받으므로 인코딩하지 않는다."""
    df = df.drop(columns=[ID_COL]).copy()
    df = build_features(df)
    df = apply_shrinkage(df, shrinkage_priors)
    df = attach_trackman_features(df, trackman_lookup, trackman_cols, trackman_league_fallback)

    if cat_encoder is not None:
        df[CAT_COLS] = cat_encoder.transform(df[CAT_COLS]).astype(int)

    return df


# =======================
# 제출 파일 생성 유틸
# =======================

def merge_predictions(sub, ids, preds):
    pred_map = dict(zip(ids, preds))
    values, n_missing = [], 0
    for rid, cur in zip(sub[ID_COL], sub[TARGET_COL]):
        p = pred_map.get(rid)
        if p is None:
            n_missing += 1
            values.append(cur)
        else:
            values.append(p)
    if n_missing:
        print(f" 경고: 예측이 없어 placeholder를 유지한 row_id {n_missing}건")
    sub[TARGET_COL] = values
    return sub


def save_submission(path, sub):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sub.to_csv(path, index=False, encoding="utf-8")


# =======================
# main
# =======================

def main():
    TEST_DIR = "./data"
    MODEL_DIR = "./model"
    OUT_DIR = "./output"
    TEST_PATH = os.path.join(TEST_DIR, "test.csv")
    SAMPLE_SUB_PATH = os.path.join(TEST_DIR, "sample_submission.csv")
    META_PATH = os.path.join(MODEL_DIR, "model_meta.pkl")
    OUT_PATH = os.path.join(OUT_DIR, "submission.csv")

    print("Load model...")
    meta = joblib.load(META_PATH)
    all_features = meta["all_features"]
    shrinkage_priors = meta["shrinkage_priors"]
    model_type = meta["model_type"]
    trackman_cols = meta.get("trackman_cols", [])
    trackman_league_fallback = meta.get("trackman_league_fallback", {})
    if trackman_cols:
        trackman_lookup = pd.read_csv(os.path.join(MODEL_DIR, "trackman_pitcher_lookup.csv"), encoding="utf-8-sig")
        print(f" trackman lookup: {trackman_lookup.shape} (exp_id={meta.get('exp_id')}, shrink_k={meta.get('trackman_shrink_k')})")
    else:
        trackman_lookup = None

    if model_type == "lightgbm":
        # LightGBM Booster는 자체 텍스트 포맷(save_model/Booster(model_file=..))으로
        # 저장/로드한다. sklearn 래퍼(LGBMClassifier)를 joblib/pickle로 저장했다가
        # 다른 프로세스에서 로드하면 이 환경에서 네이티브 크래시가 재현되어
        # (실험 로그 참고) 이 방식을 쓰지 않는다. (lightgbm은 파일 맨 위에서
        # 이미 import됨 -- pandas보다 먼저 import돼야 하는 이 환경의 제약 때문.)
        booster = lgb.Booster(model_file=os.path.join(MODEL_DIR, "lgbm_booster.txt"))
        cat_encoder = meta["cat_encoder"]
    elif model_type == "catboost":
        import catboost as cb
        booster = cb.CatBoostClassifier()
        booster.load_model(os.path.join(MODEL_DIR, "catboost_model.cbm"))
        cat_encoder = None
    elif model_type == "catboost_seedbag":
        # exp_010: 동일 피처/하이퍼파라미터, 서로 다른 random_seed로 학습한
        # CatBoost 여러 개를 저장해두고 추론 시 확률을 평균한다(분산 감소
        # 목적 -- experiments/exp_010_seed_bagging.md 참고). meta에
        # "seed_weights"가 있으면 그 가중치로, 없으면 균등평균으로 합친다
        # (exp_010 자신은 균등평균 = weights 없음, exp_016은 가중치 있음).
        import catboost as cb
        booster = []
        for fname in meta["seed_model_files"]:
            clf = cb.CatBoostClassifier()
            clf.load_model(os.path.join(MODEL_DIR, fname))
            booster.append(clf)
        seed_weights = meta.get("seed_weights")
        cat_encoder = None
    elif model_type == "catboost_regressor":
        # exp_012: CatBoostRegressor(RMSE 목적함수)로 학습 -- 확률이 아닌
        # 실수 예측이므로 [0,1] 클리핑 필요(아래 추론 단계에서 처리).
        import catboost as cb
        booster = cb.CatBoostRegressor()
        booster.load_model(os.path.join(MODEL_DIR, "catboost_model.cbm"))
        cat_encoder = None
    elif model_type == "ensemble":
        # 서로 다른 종류의 모델(catboost / catboost_regressor / lightgbm)을
        # 각자의 가중치로 블렌딩(exp_013/015/016/017). meta["members"]는
        # [{"type":..., "file":..., "weight":...}, ...]. 실제 로딩+추론은
        # 아래 "Inference model" 단계에서 한다.
        cat_encoder = None
    else:
        raise ValueError(f"알 수 없는 model_type: {model_type}")
    print(f" OK. model_type={model_type}, n_features={len(all_features)}")

    print("Load test data...")
    test = load_test(TEST_PATH)
    sub = load_sample_submission(SAMPLE_SUB_PATH)
    print(f" test={len(test)}  submission={len(sub)}")

    print("Build features...")
    ids = test[ID_COL].tolist()
    X = build_features_for_inference(
        test, shrinkage_priors, trackman_lookup, trackman_cols, trackman_league_fallback,
        cat_encoder=cat_encoder,
    )[all_features]
    print(f" features={X.shape[1]}")

    print("Inference model...")
    if len(X) == 0:
        preds = np.array([])
    elif model_type == "lightgbm":
        preds = booster.predict(X)
    elif model_type == "catboost_seedbag":
        member_preds = [clf.predict_proba(X)[:, 1] for clf in booster]
        if seed_weights is not None:
            preds = np.average(member_preds, axis=0, weights=seed_weights)
        else:
            preds = np.mean(member_preds, axis=0)
    elif model_type == "catboost_regressor":
        preds = np.clip(booster.predict(X), 0.0, 1.0)
    elif model_type == "ensemble":
        preds = np.zeros(len(X))
        lgb_members = [m for m in meta["members"] if m["type"] == "lightgbm"]
        cb_members = [m for m in meta["members"] if m["type"] != "lightgbm"]
        if lgb_members:
            import lightgbm as lgb
            X_enc = X.copy()
            X_enc[CAT_COLS] = meta["lgb_cat_encoder"].transform(X_enc[CAT_COLS]).astype(int)
            for m in lgb_members:
                obj = lgb.Booster(model_file=os.path.join(MODEL_DIR, m["file"]))
                preds = preds + m["weight"] * obj.predict(X_enc)
        if cb_members:
            import catboost as cb
            for m in cb_members:
                if m["type"] == "catboost_regressor":
                    obj = cb.CatBoostRegressor()
                    obj.load_model(os.path.join(MODEL_DIR, m["file"]))
                    preds = preds + m["weight"] * np.clip(obj.predict(X), 0.0, 1.0)
                else:
                    obj = cb.CatBoostClassifier()
                    obj.load_model(os.path.join(MODEL_DIR, m["file"]))
                    preds = preds + m["weight"] * obj.predict_proba(X)[:, 1]
    else:
        preds = booster.predict_proba(X)[:, 1]

    # exp_018: model_type과 무관한 범용 사후 보정(post-hoc calibration).
    # meta["calibrator"]가 있으면 raw preds에 한 번 더 적용한다 --
    # 2019-2023 5-fold cross-fit OOF 예측으로 leak-safe하게 학습된
    # 것(2024/평가 데이터는 전혀 안 봄, experiments/exp_018_*.md 참고).
    calibrator = meta.get("calibrator")
    if calibrator is not None:
        preds = calibrator.predict_proba(np.asarray(preds, dtype=float).reshape(-1, 1))[:, 1]

    preds = np.clip(preds, 0.0, 1.0)
    print(f" preds={len(preds)}")

    print("Build submission...")
    sub = merge_predictions(sub, ids, preds)
    save_submission(OUT_PATH, sub)
    print(f"Saved: {OUT_PATH} (rows={len(sub)})")


if __name__ == "__main__":
    main()
