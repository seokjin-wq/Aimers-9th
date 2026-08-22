# script.py — exp_001: baseline features + safe derived features + LightGBM
import os

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd

ID_COL = "row_id"
TARGET_COL = "control_success"

CAT_COLS = ["top_bottom", "game_type", "base_state"]


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
# 피처 엔지니어링 (학습 때와 동일 — src/features.py와 내용 일치)
# =======================

def build_features(df, cat_encoder):
    """row_id를 제외한 원본 컬럼 + 행 단위 파생 컬럼. 다른 행 정보는 쓰지 않음."""
    df = df.drop(columns=[ID_COL]).copy()

    df["count_diff"] = df["strikes_before"] - df["balls_before"]
    df["count_total"] = df["strikes_before"] + df["balls_before"]
    df["two_strike"] = (df["strikes_before"] == 2).astype(int)
    df["three_ball"] = (df["balls_before"] == 3).astype(int)
    df["full_count"] = df["two_strike"] & df["three_ball"]

    df["late_inning"] = (df["inning"] >= 7).astype(int)

    df["score_margin_abs"] = df["score_diff_pitcher_team"].abs()
    df["is_close_game"] = (df["score_margin_abs"] <= 1).astype(int)
    df["runners_scoring_position"] = (
        (df["runner_on_2b"] == 1) | (df["runner_on_3b"] == 1)
    ).astype(int)

    df["pitcher_minus_batter_success"] = (
        df["asof_pitcher_success_rate"] - df["asof_batter_success_rate"]
    )
    df["pitcher_middle_minus_success"] = (
        df["asof_pitcher_middle_rate"] - df["asof_pitcher_success_rate"]
    )
    df["pitcher_recent_form_delta"] = (
        df["asof_pitcher_prev1_game_success_rate"]
        - df["asof_pitcher_prev5_game_success_rate"]
    )

    df["pitcher_experience_log"] = np.log1p(df["asof_pitcher_n"])
    df["batter_experience_log"] = np.log1p(df["asof_batter_n"])

    mix_cols = [
        "asof_pitcher_fastball_rate",
        "asof_pitcher_breaking_rate",
        "asof_pitcher_offspeed_rate",
    ]
    mix_sq_sum = sum(df[c].fillna(0) ** 2 for c in mix_cols)
    df["pitchmix_diversity"] = 1 - mix_sq_sum

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
    print(f" OK. n_features={len(all_features)}")

    print("Load test data...")
    test = load_test(TEST_PATH)
    sub = load_sample_submission(SAMPLE_SUB_PATH)
    print(f" test={len(test)}  submission={len(sub)}")

    print("Build features...")
    ids = test[ID_COL].tolist()
    X = build_features(test, cat_encoder)[all_features]
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
