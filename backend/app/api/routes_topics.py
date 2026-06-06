from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.api.deps import require_api_key

router = APIRouter(tags=["topics"])

_topic_store: list[dict[str, Any]] = []


class TopicCreate(BaseModel):
    title: str
    description: str = ""


@router.get("/topics")
async def list_topics(_: str = Depends(require_api_key)) -> dict[str, Any]:
    return {"topics": _topic_store}


@router.post("/topics")
async def create_topic(
    body: TopicCreate,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    topic = {"title": body.title, "description": body.description}
    _topic_store.append(topic)
    return topic


@router.delete("/topics/{topic_slug}")
async def delete_topic(topic_slug: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    global _topic_store
    _topic_store = [t for t in _topic_store if t.get("title", "").lower().replace(" ", "-") != topic_slug]
    return {"deleted": topic_slug}
