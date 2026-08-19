import numpy as np

from aimers_exp.metrics import probability_metrics


def test_brier_and_competition_score_match_formula() -> None:
    targets = np.array([0, 0, 1, 1])
    probabilities = np.array([0.2, 0.4, 0.6, 0.8])
    metrics = probability_metrics(targets, probabilities)
    expected_brier = float(np.mean((probabilities - targets) ** 2))
    expected_reference = 0.25
    assert np.isclose(metrics["brier"], expected_brier)
    assert np.isclose(metrics["reference_brier"], expected_reference)
    assert np.isclose(
        metrics["brier_skill_score"],
        max(0.0, 100000.0 * (1.0 - expected_brier / expected_reference)),
    )

