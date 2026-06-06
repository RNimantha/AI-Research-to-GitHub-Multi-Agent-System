from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class Source(BaseModel):
    title: str
    url: HttpUrl
    source_type: str
    published_date: Optional[str] = None
    accessed_at: datetime
    credibility_score: float = Field(ge=0, le=1)
    summary: str


class GeneratedFile(BaseModel):
    path: str
    purpose: str
    content: str


class POCProject(BaseModel):
    project_name: str
    goal: str
    dependencies: list[str]
    files: list[GeneratedFile]
    run_instructions: str
    limitations: list[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    schema_version: str = "1.0"
    topic_slug: str
    topic_name: str
    one_liner: str
    created_at: datetime
    tags: list[str]

    executive_summary: str
    what_it_is: str
    why_it_matters_now: str
    problem_it_solves: str
    how_it_works_simple: str
    how_it_works_technical: str
    architecture: str
    ecosystem_placement: str
    real_world_implementations: str
    use_cases: list[str]
    limitations: str
    alternatives: list[str]
    future_outlook: str

    poc: POCProject
    sources: list[Source] = Field(min_length=5)

    eval_score: Optional[float] = Field(default=None, ge=0, le=10)
    eval_flags: list[str] = Field(default_factory=list)
    github_folder: Optional[str] = None
    github_url: Optional[str] = None


class EvaluationResult(BaseModel):
    overall_score: float = Field(ge=0, le=10)
    dimension_scores: dict[str, float]
    passed: bool
    flags: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class CodeReviewResult(BaseModel):
    status: str  # "approved" | "needs_revision"
    issues: list[str] = Field(default_factory=list)


class DiscoveredTopic(BaseModel):
    title: str
    summary: str
    source_urls: list[str] = Field(default_factory=list)
    novelty_score: float = Field(ge=0, le=10)
    poc_feasibility_score: float = Field(ge=0, le=10)
    business_value_score: float = Field(ge=0, le=10)


class SelectedTopic(BaseModel):
    title: str
    reason: str
    difficulty: str
    expected_poc: str


class SourceVerificationResult(BaseModel):
    verified_sources: list[dict]
    rejected_sources: list[dict]
    unsupported_claims: list[str]
    confidence_score: float = Field(ge=0, le=1)


class AgentLog(BaseModel):
    run_id: str
    agent_name: str
    status: str
    input_json: Optional[dict] = None
    output_json: Optional[dict] = None
    error_message: Optional[str] = None
    model_name: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
