"""Tests for workflow state and routing logic."""
import pytest

from backend.app.graph.routing import (
    MAX_CODE_REVISIONS,
    route_after_code_review,
    route_after_evaluation,
    route_after_github_approval,
    route_after_source_verification,
    route_after_topic_approval,
)
from backend.app.graph.state import RunStatus, Trend2POCState


def _make_state(**kwargs) -> Trend2POCState:
    return Trend2POCState(run_id="test-run-001", **kwargs)


def test_route_after_topic_approval_approved():
    state = _make_state(topic_approved=True)
    assert route_after_topic_approval(state) == "research"


def test_route_after_topic_approval_not_approved():
    state = _make_state(topic_approved=False)
    assert route_after_topic_approval(state) == "end_awaiting_topic"


def test_route_after_source_verification_high_confidence():
    state = _make_state(source_confidence_score=0.85)
    assert route_after_source_verification(state) == "technical_analysis"


def test_route_after_source_verification_low_confidence():
    state = _make_state(source_confidence_score=0.50)
    assert route_after_source_verification(state) == "research"


def test_route_after_code_review_approved():
    state = _make_state(code_review={"status": "approved"})
    assert route_after_code_review(state) == "evaluator"


def test_route_after_code_review_needs_revision():
    state = _make_state(
        code_review={"status": "needs_revision", "issues": ["missing dep"]},
        code_revision_count=0,
    )
    assert route_after_code_review(state) == "code_generator"


def test_route_after_code_review_max_retries():
    state = _make_state(
        code_review={"status": "needs_revision"},
        code_revision_count=MAX_CODE_REVISIONS,
    )
    assert route_after_code_review(state) == "evaluator"


def test_route_after_evaluation_passed():
    state = _make_state(evaluation={"passed": True}, eval_score=8.5)
    assert route_after_evaluation(state) == "await_github_approval"


def test_route_after_evaluation_failed():
    state = _make_state(evaluation={"passed": False}, eval_score=5.0)
    assert route_after_evaluation(state) == "end_eval_failed"


def test_route_after_github_approval_approved():
    state = _make_state(github_push_approved=True)
    assert route_after_github_approval(state) == "github_publisher"


def test_route_after_github_approval_not_approved():
    state = _make_state(github_push_approved=False)
    assert route_after_github_approval(state) == "end_awaiting_github"


def test_state_default_values():
    state = Trend2POCState(run_id="abc-123")
    assert state.status == RunStatus.PENDING
    assert state.topic_approved is False
    assert state.github_push_approved is False
    assert state.errors == []
