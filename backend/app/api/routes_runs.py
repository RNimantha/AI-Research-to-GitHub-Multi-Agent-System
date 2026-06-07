import asyncio
import json
import uuid
from typing import Any, AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.app.api.deps import require_api_key
from backend.app.config import settings
from backend.app.graph.checkpoints import checkpointer
from backend.app.graph.state import RunStatus, Trend2POCState
from backend.app.graph.workflow import Trend2POCWorkflow

TERMINAL = {RunStatus.COMPLETE, RunStatus.FAILED}

router = APIRouter(tags=["runs"])


class CreateRunRequest(BaseModel):
    topic: str | None = None
    user_id: str | None = None


class ApproveTopicRequest(BaseModel):
    approved: bool
    approved_topic: str | None = None
    notes: str = ""


class ApproveReportRequest(BaseModel):
    approved: bool
    revision_notes: str = ""


class ApprovePOCRequest(BaseModel):
    approved: bool
    notes: str = ""


class ApproveImprovementsRequest(BaseModel):
    apply: bool  # True = run improvement agent, False = skip improvements


class ApproveGithubRequest(BaseModel):
    approved: bool
    notes: str = ""


def _checkpoint(run_id: str, state: Trend2POCState) -> None:
    checkpointer.save(run_id, state)
    try:
        from backend.app.services.supabase_sync import sync_state_to_supabase
        sync_state_to_supabase(state)
    except Exception:
        pass


def _run_pipeline(run_id: str, topic: str | None, user_id: str | None) -> None:
    workflow = Trend2POCWorkflow()
    state = workflow.run(
        input_topic=topic,
        user_id=user_id,
        run_id=run_id,
        checkpoint_fn=lambda s: _checkpoint(run_id, s),
    )
    _checkpoint(run_id, state)


@router.post("/runs")
async def create_run(
    body: CreateRunRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    initial_state = Trend2POCState(
        run_id=run_id,
        user_id=body.user_id,
        input_topic=body.topic,
        status=RunStatus.PENDING,
    )
    checkpointer.save(run_id, initial_state)
    background_tasks.add_task(_run_pipeline, run_id, body.topic, body.user_id)
    return {"run_id": run_id, "status": RunStatus.PENDING}


@router.get("/runs")
async def list_runs(_: str = Depends(require_api_key)) -> dict[str, Any]:
    runs = []
    for run_id in checkpointer.list_run_ids():
        try:
            state = checkpointer.load(run_id)
            if state:
                runs.append({
                    "run_id": state.run_id,
                    "status": state.status,
                    "input_topic": state.input_topic,
                    "approved_topic": state.approved_topic,
                    "selected_topic": state.selected_topic,
                    "eval_score": state.eval_score,
                    "github_repo_url": state.github_repo_url,
                })
        except Exception:
            continue
    return {"runs": runs}


@router.get("/runs/{run_id}")
async def get_run(run_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return state.model_dump()


@router.get("/runs/{run_id}/stream")
async def stream_run(
    run_id: str,
    api_key: str = Query(default=""),
) -> StreamingResponse:
    if settings.api_secret_key and api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    async def generator() -> AsyncGenerator[str, None]:
        last_status: str | None = None
        last_log_count: int = -1
        not_found_count = 0
        while True:
            state = checkpointer.load(run_id)
            if state is None:
                not_found_count += 1
                if not_found_count > 5:
                    yield f"event: error\ndata: {json.dumps({'detail': 'Run not found'})}\n\n"
                    break
                await asyncio.sleep(1.0)
                continue
            not_found_count = 0
            log_count = len(state.agent_logs)
            if state.status != last_status or log_count != last_log_count:
                last_status = state.status
                last_log_count = log_count
                data = json.dumps(state.model_dump(), default=str)
                yield f"data: {data}\n\n"
            if state.status in TERMINAL:
                yield f"event: done\ndata: {{}}\n\n"
                break
            await asyncio.sleep(1.5)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    state.status = RunStatus.FAILED
    state.errors.append("Cancelled by user")
    checkpointer.save(run_id, state)
    return {"run_id": run_id, "status": state.status}


def _detect_retry_stage(state: Trend2POCState) -> str:
    """Determine which stage to resume from based on available state data."""
    if state.github_push_approved and not state.github_repo_url:
        return "github"
    if state.report_approved and state.report_json:
        return "poc"
    if state.topic_approved and state.approved_topic:
        return "research"
    if state.discovered_topics:
        return "awaiting_topic"
    return "full"


@router.post("/runs/{run_id}/retry")
async def retry_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if state.status not in (RunStatus.FAILED, RunStatus.COMPLETE):
        raise HTTPException(status_code=400, detail=f"Run is {state.status}, not retryable")

    stage = _detect_retry_stage(state)
    state.errors = []  # clear previous errors

    if stage == "github":
        state.status = RunStatus.AWAITING_GITHUB_APPROVAL
        checkpointer.save(run_id, state)
        # Re-trigger publish if already approved
        if state.github_push_approved:
            background_tasks.add_task(_resume_github_publish, run_id)
        return {"run_id": run_id, "retry_from": "github_publish", "status": state.status}

    if stage == "poc":
        state.status = RunStatus.AWAITING_REPORT_APPROVAL
        state.report_approved = False
        checkpointer.save(run_id, state)
        return {"run_id": run_id, "retry_from": "poc_pipeline", "status": state.status,
                "note": "Re-approve the report to trigger POC generation"}

    if stage == "research":
        state.status = RunStatus.RESEARCHING
        checkpointer.save(run_id, state)
        background_tasks.add_task(_resume_research, run_id)
        return {"run_id": run_id, "retry_from": "research", "status": state.status}

    if stage == "awaiting_topic":
        state.status = RunStatus.AWAITING_TOPIC_APPROVAL
        checkpointer.save(run_id, state)
        return {"run_id": run_id, "retry_from": "topic_approval", "status": state.status}

    # Full restart
    state.status = RunStatus.PENDING
    checkpointer.save(run_id, state)
    background_tasks.add_task(_run_pipeline, run_id, state.input_topic, state.user_id)
    return {"run_id": run_id, "retry_from": "full_restart", "status": state.status}


@router.post("/runs/{run_id}/approve-topic")
async def approve_topic(
    run_id: str,
    body: ApproveTopicRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    state.topic_approved = body.approved
    if body.approved_topic:
        state.approved_topic = body.approved_topic
    elif state.selected_topic:
        state.approved_topic = state.selected_topic.get("title", "")

    checkpointer.save(run_id, state)

    if body.approved:
        background_tasks.add_task(_resume_research, run_id)

    return {"run_id": run_id, "topic_approved": body.approved}


def _resume_research(run_id: str) -> None:
    state = checkpointer.load(run_id)
    if not state:
        return

    from backend.app.graph.workflow import (
        node_research,
        node_verify_sources,
        node_technical_analysis,
        node_write_report,
    )
    from backend.app.config import settings as cfg

    workflow = Trend2POCWorkflow()
    state = node_research(state, workflow.llm, workflow.search)
    _checkpoint(run_id, state)
    state = node_verify_sources(state, workflow.llm)
    _checkpoint(run_id, state)
    if (state.source_confidence_score or 0) < cfg.source_confidence_threshold:
        state = node_research(state, workflow.llm, workflow.search)
        _checkpoint(run_id, state)
        state = node_verify_sources(state, workflow.llm)
        _checkpoint(run_id, state)
    state = node_technical_analysis(state, workflow.llm)
    _checkpoint(run_id, state)
    state = node_write_report(state, workflow.llm)
    _checkpoint(run_id, state)


@router.post("/runs/{run_id}/approve-report")
async def approve_report(
    run_id: str,
    body: ApproveReportRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    state.report_approved = body.approved
    state.report_revision_notes = body.revision_notes
    checkpointer.save(run_id, state)

    if body.approved:
        background_tasks.add_task(_resume_poc_pipeline, run_id)

    return {"run_id": run_id, "report_approved": body.approved}


def _resume_poc_pipeline(run_id: str) -> None:
    state = checkpointer.load(run_id)
    if not state:
        return
    workflow = Trend2POCWorkflow()
    updated = workflow.resume_after_report_approval(
        state,
        checkpoint_fn=lambda s: _checkpoint(run_id, s),
    )
    _checkpoint(run_id, updated)


@router.post("/runs/{run_id}/approve-poc")
async def approve_poc(
    run_id: str,
    body: ApprovePOCRequest,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    state.poc_approved = body.approved
    checkpointer.save(run_id, state)
    return {"run_id": run_id, "poc_approved": body.approved}


@router.post("/runs/{run_id}/approve-improvements")
async def approve_improvements(
    run_id: str,
    body: ApproveImprovementsRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    state.improvement_approved = body.apply
    if body.apply:
        background_tasks.add_task(_resume_improvement, run_id)
    else:
        # Skip improvements — go straight to GitHub approval
        state.status = RunStatus.AWAITING_GITHUB_APPROVAL
        _checkpoint(run_id, state)

    return {"run_id": run_id, "apply_improvements": body.apply}


def _resume_improvement(run_id: str) -> None:
    state = checkpointer.load(run_id)
    if not state:
        return
    from backend.app.graph.workflow import node_improve
    workflow = Trend2POCWorkflow()
    state = node_improve(state, workflow.llm, ckpt=lambda s: _checkpoint(run_id, s))
    _checkpoint(run_id, state)


@router.post("/runs/{run_id}/approve-github-push")
async def approve_github_push(
    run_id: str,
    body: ApproveGithubRequest,
    background_tasks: BackgroundTasks,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    state = checkpointer.load(run_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    state.github_push_approved = body.approved
    checkpointer.save(run_id, state)

    if body.approved:
        background_tasks.add_task(_resume_github_publish, run_id)

    return {"run_id": run_id, "github_push_approved": body.approved}


def _resume_github_publish(run_id: str) -> None:
    state = checkpointer.load(run_id)
    if not state:
        return
    workflow = Trend2POCWorkflow()
    updated = workflow.resume_after_github_approval(
        state,
        checkpoint_fn=lambda s: _checkpoint(run_id, s),
    )
    _checkpoint(run_id, updated)
