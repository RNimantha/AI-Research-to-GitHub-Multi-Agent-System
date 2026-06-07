import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes_health import router as health_router
from backend.app.api.routes_runs import router as runs_router
from backend.app.api.routes_reports import router as reports_router
from backend.app.api.routes_topics import router as topics_router
from backend.app.api.routes_github import router as github_router
from backend.app.api.routes_settings import router as settings_router
from backend.app.api.routes_social import router as social_router
from backend.app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="Trend2POC API",
    description="AI Research-to-GitHub Multi-Agent System API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(runs_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(topics_router, prefix="/api/v1")
app.include_router(github_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")
app.include_router(social_router, prefix="/api/v1")
