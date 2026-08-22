# script.py — exp_002: baseline + exp_001/exp_002 derived features
# (cold-start shrinkage 포함) + LightGBM
import os
import sys

import joblib
import lightgbm as lgb
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

def build_features_for_inference(df, cat_encoder, shrinkage_priors):
    """row_id 제거 + src/features.py의 build_features/apply_shrinkage +
    학습 때와 동일한 인코더로 범주형 정수 인코딩. 다른 행 정보는 쓰지 않음."""
    df = df.drop(columns=[ID_COL]).copy()
    df = build_features(df)
    df = apply_shrinkage(df, shrinkage_priors)

    # 학습 때와 동일한 인코더로 정수 인코딩 (category dtype은 소량 배치
    # 추론에서 LightGBM 네이티브 크래시를 일으켜 사용하지 않음)
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
    BOOSTER_PATH = os.path.join(MODEL_DIR, "lgbm_booster.txt")
    META_PATH = os.path.join(MODEL_DIR, "lgbm_meta.pkl")
    OUT_PATH = os.path.join(OUT_DIR, "submission.csv")

    # LightGBM Booster는 자체 텍스트 포맷(save_model/Booster(model_file=..))으로
    # 저장/로드한다. sklearn 래퍼(LGBMClassifier)를 joblib/pickle로 저장했다가
    # 다른 프로세스에서 로드하면 이 환경에서 네이티브 크래시가 재현되어
    # (실험 로그 참고) 이 방식을 쓰지 않는다.
    print("Load model...")
    booster = lgb.Booster(model_file=BOOSTER_PATH)
    meta = joblib.load(META_PATH)
    all_features = meta["all_features"]
    cat_encoder = meta["cat_encoder"]
    shrinkage_priors = meta["shrinkage_priors"]
    print(f" OK. n_features={len(all_features)}")

    print("Load test data...")
    test = load_test(TEST_PATH)
    sub = load_sample_submission(SAMPLE_SUB_PATH)
    print(f" test={len(test)}  submission={len(sub)}")

    print("Build features...")
    ids = test[ID_COL].tolist()
    X = build_features_for_inference(test, cat_encoder, shrinkage_priors)[all_features]
    print(f" features={X.shape[1]}")

    print("Inference model...")
    preds = booster.predict(X) if len(X) else np.array([])
    preds = np.clip(preds, 0.0, 1.0)
    print(f" preds={len(preds)}")

    print("Build submission...")
    sub = merge_predictions(sub, ids, preds)
    save_submission(OUT_PATH, sub)
    print(f"Saved: {OUT_PATH} (rows={len(sub)})")


if __name__ == "__main__":
    main()
