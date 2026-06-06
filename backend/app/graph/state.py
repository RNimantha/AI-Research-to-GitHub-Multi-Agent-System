from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    PENDING = "pending"
    DISCOVERING = "discovering"
    AWAITING_TOPIC_APPROVAL = "awaiting_topic_approval"
    RESEARCHING = "researching"
    VERIFYING_SOURCES = "verifying_sources"
    ANALYZING = "analyzing"
    WRITING_REPORT = "writing_report"
    AWAITING_REPORT_APPROVAL = "awaiting_report_approval"
    PLANNING_POC = "planning_poc"
    GENERATING_CODE = "generating_code"
    REVIEWING_CODE = "reviewing_code"
    EVALUATING = "evaluating"
    AWAITING_IMPROVEMENT_APPROVAL = "awaiting_improvement_approval"
    IMPROVING = "improving"
    AWAITING_GITHUB_APPROVAL = "awaiting_github_approval"
    PUBLISHING = "publishing"
    COMPLETE = "complete"
    FAILED = "failed"


class Trend2POCState(BaseModel):
    run_id: str
    user_id: Optional[str] = None
    status: RunStatus = RunStatus.PENDING

    input_topic: Optional[str] = None
    discovered_topics: list[dict[str, Any]] = Field(default_factory=list)
    selected_topic: Optional[dict[str, Any]] = None
    approved_topic: Optional[str] = None

    raw_sources: list[dict[str, Any]] = Field(default_factory=list)
    verified_sources: list[dict[str, Any]] = Field(default_factory=list)
    rejected_sources: list[dict[str, Any]] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    source_confidence_score: Optional[float] = None

    research_context: Optional[dict[str, Any]] = None
    technical_analysis: Optional[dict[str, Any]] = None
    report_json: Optional[dict[str, Any]] = None
    report_markdown: Optional[str] = None
    report_revision_notes: str = ""

    poc_plan: Optional[dict[str, Any]] = None
    generated_files: list[dict[str, str]] = Field(default_factory=list)
    code_review: Optional[dict[str, Any]] = None
    code_revision_count: int = 0

    evaluation: Optional[dict[str, Any]] = None
    eval_score: Optional[float] = None
    eval_flags: list[str] = Field(default_factory=list)

    topic_approved: bool = False
    report_approved: bool = False
    poc_approved: bool = False
    improvement_approved: Optional[bool] = None  # None=pending, True=apply, False=skip
    github_push_approved: bool = False

    github_repo_url: Optional[str] = None
    github_folder_path: Optional[str] = None

    model_usage: list[dict[str, Any]] = Field(default_factory=list)
    agent_logs: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
