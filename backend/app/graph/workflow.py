import logging
import time
import uuid
from datetime import datetime
from typing import Any

from backend.app.agents.code_reviewer_agent import run_code_reviewer_agent
from backend.app.agents.discovery_agent import run_discovery_agent
from backend.app.agents.evaluator_agent import run_evaluator_agent
from backend.app.agents.github_publisher_agent import run_github_publisher_agent
from backend.app.agents.improvement_agent import run_improvement_agent
from backend.app.agents.poc_code_generator_agent import run_poc_code_generator_agent
from backend.app.agents.poc_planner_agent import run_poc_planner_agent
from backend.app.agents.report_writer_agent import run_report_writer_agent
from backend.app.agents.research_agent import run_research_agent
from backend.app.agents.source_verification_agent import run_source_verification_agent
from backend.app.agents.technical_analysis_agent import run_technical_analysis_agent
from backend.app.agents.topic_selection_agent import run_topic_selection_agent
from backend.app.config import settings
from backend.app.graph.state import RunStatus, Trend2POCState
from backend.app.integrations.llm_client import LLMClient
from backend.app.integrations.search_client import SearchClient

logger = logging.getLogger(__name__)


def _log_agent(state: Trend2POCState, agent_name: str, result: dict[str, Any]) -> Trend2POCState:
    usage = result.get("usage") or {}
    log_entry = {
        "run_id": state.run_id,
        "agent_name": agent_name,
        "status": "success",
        "model_name": usage.get("model"),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "estimated_cost_usd": usage.get("estimated_cost_usd", 0.0),
        "latency_ms": usage.get("latency_ms"),
        "created_at": datetime.utcnow().isoformat(),
    }
    state.agent_logs.append(log_entry)
    state.model_usage.append(usage)
    return state


def _ckpt(state: Trend2POCState, fn: Any) -> None:
    if fn:
        fn(state)


def node_discover(state: Trend2POCState, llm: LLMClient, search: SearchClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.DISCOVERING
    _ckpt(state, ckpt)
    result = run_discovery_agent(llm=llm, search=search, max_topics=settings.max_topics_per_run)
    state.discovered_topics = result["discovered_topics"]
    _log_agent(state, "discovery_agent", result)

    if state.discovered_topics:
        _ckpt(state, ckpt)
        selection_result = run_topic_selection_agent(topics=state.discovered_topics, llm=llm)
        state.selected_topic = selection_result["selected_topic"]
        _log_agent(state, "topic_selection_agent", selection_result)

    state.status = RunStatus.AWAITING_TOPIC_APPROVAL
    return state


def node_research(state: Trend2POCState, llm: LLMClient, search: SearchClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.RESEARCHING
    _ckpt(state, ckpt)
    topic = state.approved_topic or (state.selected_topic or {}).get("title", state.input_topic or "")

    result = run_research_agent(
        topic=topic,
        max_sources=settings.max_sources_per_topic,
        llm=llm,
        search=search,
    )
    state.research_context = result["research_context"]
    state.raw_sources = result["raw_sources"]
    _log_agent(state, "research_agent", result)
    return state


def node_verify_sources(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.VERIFYING_SOURCES
    _ckpt(state, ckpt)
    topic = state.approved_topic or (state.selected_topic or {}).get("title", "")

    result = run_source_verification_agent(
        topic=topic,
        raw_sources=state.raw_sources,
        research_context=state.research_context or {},
        llm=llm,
    )
    state.verified_sources = result["verified_sources"]
    state.rejected_sources = result["rejected_sources"]
    state.unsupported_claims = result["unsupported_claims"]
    state.source_confidence_score = result["confidence_score"]
    _log_agent(state, "source_verification_agent", result)
    return state


def node_technical_analysis(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.ANALYZING
    _ckpt(state, ckpt)
    topic = state.approved_topic or (state.selected_topic or {}).get("title", "")

    result = run_technical_analysis_agent(
        topic=topic,
        research_context=state.research_context or {},
        verified_sources=state.verified_sources,
        llm=llm,
    )
    state.technical_analysis = result["technical_analysis"]
    _log_agent(state, "technical_analysis_agent", result)
    return state


def node_write_report(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.WRITING_REPORT
    _ckpt(state, ckpt)
    topic = state.approved_topic or (state.selected_topic or {}).get("title", "")

    result = run_report_writer_agent(
        topic=topic,
        research_context=state.research_context or {},
        technical_analysis=state.technical_analysis or {},
        verified_sources=state.verified_sources,
        poc_project=state.poc_plan,
        revision_notes=state.report_revision_notes,
        llm=llm,
    )
    state.report_json = result["report_json"]
    state.status = RunStatus.AWAITING_REPORT_APPROVAL
    _log_agent(state, "report_writer_agent", result)
    return state


def node_plan_poc(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.PLANNING_POC
    _ckpt(state, ckpt)
    topic = state.approved_topic or (state.selected_topic or {}).get("title", "")

    result = run_poc_planner_agent(
        topic=topic,
        technical_analysis=state.technical_analysis or {},
        research_context=state.research_context or {},
        llm=llm,
    )
    state.poc_plan = result["poc_plan"]
    _log_agent(state, "poc_planner_agent", result)
    return state


def node_generate_code(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.GENERATING_CODE
    _ckpt(state, ckpt)
    topic = state.approved_topic or (state.selected_topic or {}).get("title", "")
    revision_issues = (state.code_review or {}).get("issues", []) if state.code_revision_count > 0 else None

    result = run_poc_code_generator_agent(
        topic=topic,
        poc_plan=state.poc_plan or {},
        revision_issues=revision_issues,
        llm=llm,
    )
    state.generated_files = result["generated_files"]
    state.code_revision_count += 1
    _log_agent(state, "poc_code_generator_agent", result)
    return state


def node_review_code(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.REVIEWING_CODE
    _ckpt(state, ckpt)

    result = run_code_reviewer_agent(generated_files=state.generated_files, llm=llm)
    state.code_review = result
    _log_agent(state, "code_reviewer_agent", result)
    return state


def node_evaluate(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.EVALUATING
    _ckpt(state, ckpt)

    result = run_evaluator_agent(
        report_json=state.report_json or {},
        generated_files=state.generated_files,
        min_eval_score=settings.min_eval_score,
        llm=llm,
    )
    state.evaluation = result["evaluation"]
    state.eval_score = result["eval_score"]
    state.eval_flags = result["evaluation"].get("flags", [])

    if state.evaluation.get("passed"):
        improvements = state.evaluation.get("improvements", [])
        if improvements:
            state.status = RunStatus.AWAITING_IMPROVEMENT_APPROVAL
        else:
            state.status = RunStatus.AWAITING_GITHUB_APPROVAL
    _log_agent(state, "evaluator_agent", result)
    return state


def node_improve(state: Trend2POCState, llm: LLMClient, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.IMPROVING
    _ckpt(state, ckpt)

    result = run_improvement_agent(
        report_json=state.report_json or {},
        evaluation=state.evaluation or {},
        generated_files=state.generated_files,
        llm=llm,
    )
    state.report_json = result["improved_report_json"]
    state.generated_files = result["improved_files"] or state.generated_files
    state.status = RunStatus.AWAITING_GITHUB_APPROVAL
    _log_agent(state, "improvement_agent", result)
    return state


def node_publish_github(state: Trend2POCState, ckpt: Any = None) -> Trend2POCState:
    state.status = RunStatus.PUBLISHING
    _ckpt(state, ckpt)

    # Build complete artifact list: report files + generated code files
    all_files = list(state.generated_files)

    topic_slug = (state.report_json or {}).get("topic_slug", "unknown-topic")

    result = run_github_publisher_agent(
        topic_slug=topic_slug,
        generated_files=all_files,
        eval_score=state.eval_score or 0.0,
        github_push_approved=state.github_push_approved,
        min_eval_score=settings.min_eval_score,
    )

    state.github_folder_path = result["github_folder_path"]
    state.github_repo_url = result["github_repo_url"]
    state.status = RunStatus.COMPLETE
    return state


class Trend2POCWorkflow:
    """
    Orchestrates the full research-to-GitHub pipeline.

    This is the sequential orchestrator used for CLI and background tasks.
    For LangGraph integration, nodes are wired in workflow_graph.py.
    """

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.search = SearchClient()

    def run(
        self,
        input_topic: str | None = None,
        user_id: str | None = None,
        run_id: str | None = None,
        checkpoint_fn: Any = None,
    ) -> Trend2POCState:
        def ckpt(s: Trend2POCState) -> Trend2POCState:
            if checkpoint_fn:
                checkpoint_fn(s)
            return s

        state = Trend2POCState(
            run_id=run_id or str(uuid.uuid4()),
            user_id=user_id,
            input_topic=input_topic,
        )

        try:
            # Step 1: Discovery or use provided topic
            if not input_topic:
                state = node_discover(state, self.llm, self.search, ckpt=ckpt)
                ckpt(state)
                logger.info(f"Run {state.run_id}: awaiting topic approval")
                return state  # Pause for HITL Gate 1

            # If topic is provided, skip discovery
            state.approved_topic = input_topic
            state.topic_approved = True

            # Step 2: Research
            state = node_research(state, self.llm, self.search, ckpt=ckpt)
            ckpt(state)

            # Step 3: Source verification
            state = node_verify_sources(state, self.llm, ckpt=ckpt)
            ckpt(state)

            if (state.source_confidence_score or 0) < settings.source_confidence_threshold:
                logger.warning(f"Low source confidence: {state.source_confidence_score}. Re-searching.")
                state = node_research(state, self.llm, self.search, ckpt=ckpt)
                ckpt(state)
                state = node_verify_sources(state, self.llm, ckpt=ckpt)
                ckpt(state)

            # Step 4: Technical analysis
            state = node_technical_analysis(state, self.llm, ckpt=ckpt)
            ckpt(state)

            # Step 5: Write report
            state = node_write_report(state, self.llm, ckpt=ckpt)
            ckpt(state)
            logger.info(f"Run {state.run_id}: awaiting report approval")
            return state  # Pause for HITL Gate 2

        except Exception as e:
            logger.error(f"Run {state.run_id} failed: {e}")
            state.status = RunStatus.FAILED
            state.errors.append(str(e))
            ckpt(state)
            return state

    def resume_after_report_approval(
        self,
        state: Trend2POCState,
        checkpoint_fn: Any = None,
    ) -> Trend2POCState:
        """Resume pipeline after human approves the report."""
        def ckpt(s: Trend2POCState) -> Trend2POCState:
            if checkpoint_fn:
                checkpoint_fn(s)
            return s

        try:
            if not state.report_approved:
                logger.info("Report not approved. Halted.")
                return state

            # Step 6: Plan POC
            state = node_plan_poc(state, self.llm, ckpt=ckpt)
            ckpt(state)

            # Step 7: Generate and review code (with retry)
            for attempt in range(3):
                state = node_generate_code(state, self.llm, ckpt=ckpt)
                ckpt(state)
                state = node_review_code(state, self.llm, ckpt=ckpt)
                ckpt(state)
                if (state.code_review or {}).get("status") == "approved":
                    break
                logger.warning(f"Code review failed (attempt {attempt + 1})")

            # Step 8: Evaluate
            state = node_evaluate(state, self.llm, ckpt=ckpt)
            ckpt(state)
            logger.info(f"Run {state.run_id}: evaluation score={state.eval_score}")
            return state  # Pause for HITL Gate 3 & 4

        except Exception as e:
            logger.error(f"Run {state.run_id} resume failed: {e}")
            state.status = RunStatus.FAILED
            state.errors.append(str(e))
            ckpt(state)
            return state

    def resume_after_github_approval(
        self,
        state: Trend2POCState,
        checkpoint_fn: Any = None,
    ) -> Trend2POCState:
        """Resume pipeline after human approves GitHub push."""
        def ckpt(s: Trend2POCState) -> Trend2POCState:
            if checkpoint_fn:
                checkpoint_fn(s)
            return s

        try:
            state = node_publish_github(state, ckpt=ckpt)
            ckpt(state)
            logger.info(f"Run {state.run_id}: published to {state.github_repo_url}")
            return state
        except Exception as e:
            logger.error(f"GitHub publish failed: {e}")
            state.status = RunStatus.FAILED
            state.errors.append(str(e))
            ckpt(state)
            return state
