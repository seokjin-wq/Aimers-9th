from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score


def probability_metrics(
    targets: np.ndarray, probabilities: np.ndarray
) -> dict[str, float | int | None]:
    targets = np.asarray(targets, dtype=float)
    probabilities = np.clip(np.asarray(probabilities, dtype=float), 0.0, 1.0)
    if targets.shape != probabilities.shape:
        raise ValueError("정답과 예측 배열의 크기가 다릅니다.")
    if len(targets) == 0:
        raise ValueError("빈 검증 데이터로 지표를 계산할 수 없습니다.")
    target_rate = float(targets.mean())
    prediction_mean = float(probabilities.mean())
    brier = float(np.mean((probabilities - targets) ** 2))
    reference = target_rate * (1.0 - target_rate)
    score = None if reference <= 0 else max(0.0, 100000.0 * (1.0 - brier / reference))
    auc = None
    if np.unique(targets).size == 2:
        auc = float(roc_auc_score(targets, probabilities))
    return {
        "rows": int(len(targets)),
        "target_rate": target_rate,
        "prediction_mean": prediction_mean,
        "bias": prediction_mean - target_rate,
        "brier": brier,
        "reference_brier": reference,
        "brier_skill_score": score,
        "roc_auc": auc,
    }

