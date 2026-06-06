from typing import Any

from backend.app.agents.research_agent import run_research_agent
from backend.app.agents.source_verification_agent import run_source_verification_agent
from backend.app.agents.technical_analysis_agent import run_technical_analysis_agent
from backend.app.config import settings


def run_full_research(topic: str) -> dict[str, Any]:
    """Run research → verify → analyze for a given topic."""
    research = run_research_agent(topic=topic, max_sources=settings.max_sources_per_topic)

    verification = run_source_verification_agent(
        topic=topic,
        raw_sources=research["raw_sources"],
        research_context=research["research_context"],
    )

    analysis = run_technical_analysis_agent(
        topic=topic,
        research_context=research["research_context"],
        verified_sources=verification["verified_sources"],
    )

    return {
        "research_context": research["research_context"],
        "raw_sources": research["raw_sources"],
        "verified_sources": verification["verified_sources"],
        "rejected_sources": verification["rejected_sources"],
        "source_confidence_score": verification["confidence_score"],
        "technical_analysis": analysis["technical_analysis"],
    }
