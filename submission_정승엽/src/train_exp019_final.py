"""exp_019 final -- swap exp_018_final's calibrator for the blended-OOF
Platt (fit on CatBoost seed=42 + seed=1 averaged 2019-2023 5-fold OOF,
see train_exp019_calibration_blend.py: 769.87 vs exp_018's 769.12 on the
real 2024 val). The underlying models are UNCHANGED from exp_018_final.py
(same full-2019-2024-retrained seed={42,1} CatBoost pair) -- only the
calibrator object in model_meta.pkl is refit and replaced, so this
script does not retrain any model, just reuses the already-cached OOF
arrays and the already-trained seed model files sitting in ./model/.
"""

import os

import joblib
import numpy as np

from calibration import fit_platt

MODEL_DIR = "./model"
OOF_CACHE_SEED42 = "./output/exp018_oof_cache.npz"
OOF_CACHE_SEED1 = "./output/exp019_oof_seed1_cache.npz"


def main():
    meta_path = os.path.join(MODEL_DIR, "model_meta.pkl")
    meta = joblib.load(meta_path)
    assert meta["model_type"] == "catboost_seedbag"
    assert meta["seed_model_files"] == ["catboost_model_seed42.cbm", "catboost_model_seed1.cbm"], meta["seed_model_files"]

    npz42 = np.load(OOF_CACHE_SEED42)
    npz1 = np.load(OOF_CACHE_SEED1)
    assert np.array_equal(npz42["y"], npz1["y"])
    oof_blend = (npz42["pred"] + npz1["pred"]) / 2
    oof_y = npz42["y"]
    platt_blend = fit_platt(oof_blend, oof_y, seed=42)
    print(f"블렌드 OOF Platt 재학습 완료 (n={len(oof_blend)})")

    meta["calibrator"] = platt_blend
    meta["exp_id"] = "exp_019_calibrated_blend_seedbag42_1"
    joblib.dump(meta, meta_path, compress=3)
    print(f"저장: {meta_path} (calibrator=blended-OOF Platt, 모델 파일은 exp_018과 동일)")


if __name__ == "__main__":
    main()
