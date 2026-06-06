"""Tests for Pydantic schema validation."""
from datetime import datetime

import pytest

from backend.app.core.schemas import (
    EvaluationResult,
    GeneratedFile,
    POCProject,
    ResearchReport,
    Source,
)


def _make_source() -> dict:
    return {
        "title": "Test Source",
        "url": "https://example.com/source",
        "source_type": "official_docs",
        "accessed_at": datetime.utcnow(),
        "credibility_score": 0.9,
        "summary": "A test source",
    }


def _make_poc() -> dict:
    return {
        "project_name": "test-poc",
        "goal": "Demonstrate the concept",
        "dependencies": ["fastapi", "uvicorn"],
        "files": [
            {"path": "app/main.py", "purpose": "entry point", "content": "print('hello')"}
        ],
        "run_instructions": "pip install -r requirements.txt && python app/main.py",
        "limitations": [],
    }


def _make_report() -> dict:
    sources = [_make_source() for _ in range(5)]
    return {
        "topic_slug": "test-topic",
        "topic_name": "Test Topic",
        "one_liner": "A test topic for validation",
        "created_at": datetime.utcnow(),
        "tags": ["test", "ai"],
        "executive_summary": "This is a test report.",
        "what_it_is": "A test technology.",
        "why_it_matters_now": "Because we are testing.",
        "problem_it_solves": "Test problem.",
        "how_it_works_simple": "Simply.",
        "how_it_works_technical": "Technically.",
        "architecture": "Monolith.",
        "ecosystem_placement": "Center.",
        "real_world_implementations": "Used by testers.",
        "use_cases": ["testing", "validation"],
        "limitations": "Limited by test scope.",
        "alternatives": ["mock framework"],
        "future_outlook": "More tests.",
        "poc": _make_poc(),
        "sources": sources,
    }


def test_source_valid():
    source = Source(**_make_source())
    assert source.credibility_score == 0.9


def test_source_credibility_out_of_range():
    data = _make_source()
    data["credibility_score"] = 1.5
    with pytest.raises(Exception):
        Source(**data)


def test_poc_project_valid():
    poc = POCProject(**_make_poc())
    assert poc.project_name == "test-poc"


def test_research_report_valid():
    report = ResearchReport(**_make_report())
    assert report.topic_slug == "test-topic"
    assert len(report.sources) == 5


def test_research_report_requires_5_sources():
    data = _make_report()
    data["sources"] = [_make_source() for _ in range(4)]
    with pytest.raises(Exception):
        ResearchReport(**data)


def test_evaluation_result_valid():
    result = EvaluationResult(
        overall_score=8.5,
        dimension_scores={"research_completeness": 8.0},
        passed=True,
        flags=[],
        improvements=[],
    )
    assert result.passed is True


def test_report_optional_fields_default():
    report = ResearchReport(**_make_report())
    assert report.eval_score is None
    assert report.github_url is None
    assert report.eval_flags == []
