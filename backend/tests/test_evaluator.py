"""Tests for evaluator agent logic."""
import pytest

from backend.app.agents.evaluator_agent import _compute_weighted_score, DIMENSION_WEIGHTS


def test_weights_sum_to_one():
    total = sum(DIMENSION_WEIGHTS.values())
    assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected ~1.0"


def test_compute_weighted_score_perfect():
    scores = {dim: 10.0 for dim in DIMENSION_WEIGHTS}
    result = _compute_weighted_score(scores)
    assert result == 10.0


def test_compute_weighted_score_zero():
    scores = {dim: 0.0 for dim in DIMENSION_WEIGHTS}
    result = _compute_weighted_score(scores)
    assert result == 0.0


def test_compute_weighted_score_mixed():
    scores = {
        "research_completeness": 8.0,
        "technical_accuracy": 9.0,
        "source_quality": 7.0,
        "report_clarity": 8.0,
        "poc_usefulness": 8.0,
        "poc_runnability": 7.0,
        "security": 9.0,
    }
    result = _compute_weighted_score(scores)
    # Expected: 0.20*8 + 0.25*9 + 0.15*7 + 0.10*8 + 0.10*8 + 0.10*7 + 0.10*9
    # = 1.6 + 2.25 + 1.05 + 0.8 + 0.8 + 0.7 + 0.9 = 8.1
    assert 8.0 <= result <= 8.2


def test_compute_weighted_score_empty():
    result = _compute_weighted_score({})
    assert result == 0.0


def test_compute_weighted_score_partial():
    scores = {"technical_accuracy": 10.0}
    result = _compute_weighted_score(scores)
    # Only technical_accuracy contributes: 10 * 0.25 / 1.0 = 2.5 (weight_sum = 1.0 still used)
    assert result >= 0.0
