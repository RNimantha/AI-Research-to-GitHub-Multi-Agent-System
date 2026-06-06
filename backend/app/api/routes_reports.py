from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.app.api.deps import require_api_key
from backend.app.graph.checkpoints import checkpointer

router = APIRouter(tags=["reports"])


def _extract_report(state: Any) -> dict[str, Any] | None:
    if not state or not state.report_json:
        return None
    rj = state.report_json
    return {
        "run_id": state.run_id,
        "topic_slug": rj.get("topic_slug", ""),
        "topic_name": rj.get("topic_name", state.approved_topic or state.input_topic or ""),
        "one_liner": rj.get("one_liner", ""),
        "tags": rj.get("tags", []),
        "eval_score": state.eval_score,
        "eval_flags": state.eval_flags or [],
        "github_url": state.github_repo_url,
        "status": state.status.value if hasattr(state.status, "value") else state.status,
        "report_json": rj,
        "report_markdown": state.report_markdown,
        "sources_count": len(state.verified_sources or []),
        "files_count": len(state.generated_files or []),
    }


@router.get("/reports")
async def list_reports(_: str = Depends(require_api_key)) -> dict[str, Any]:
    reports = []
    for path in sorted(checkpointer._dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            state = checkpointer.load(path.stem)
            report = _extract_report(state)
            if report:
                reports.append(report)
        except Exception:
            continue
    return {"reports": reports}


@router.get("/reports/{topic_slug}")
async def get_report(topic_slug: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    for path in checkpointer._dir.glob("*.json"):
        try:
            state = checkpointer.load(path.stem)
            if state and state.report_json and state.report_json.get("topic_slug") == topic_slug:
                report = _extract_report(state)
                if report:
                    return report
        except Exception:
            continue
    raise HTTPException(status_code=404, detail=f"Report '{topic_slug}' not found")


@router.get("/reports/{topic_slug}/markdown")
async def get_report_markdown(topic_slug: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    for path in checkpointer._dir.glob("*.json"):
        try:
            state = checkpointer.load(path.stem)
            if state and state.report_json and state.report_json.get("topic_slug") == topic_slug:
                return {"topic_slug": topic_slug, "markdown": state.report_markdown}
        except Exception:
            continue
    raise HTTPException(status_code=404, detail=f"Report '{topic_slug}' not found")


@router.get("/reports/{topic_slug}/files")
async def get_report_files(topic_slug: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    for path in checkpointer._dir.glob("*.json"):
        try:
            state = checkpointer.load(path.stem)
            if state and state.report_json and state.report_json.get("topic_slug") == topic_slug:
                return {"topic_slug": topic_slug, "files": state.generated_files or []}
        except Exception:
            continue
    raise HTTPException(status_code=404, detail=f"Report '{topic_slug}' not found")
