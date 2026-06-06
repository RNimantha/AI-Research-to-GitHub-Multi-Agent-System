# Architecture

## System Overview

Trend2POC is a sequential multi-agent pipeline with 4 HITL checkpoints.

```
User Input (topic or auto-discover)
         ↓
[Discovery Agent] ← search_client (Tavily)
         ↓
[Topic Selection Agent]
         ↓
HITL Gate 1: Topic Approval (CLI prompt or API endpoint)
         ↓
[Research Agent] ← search_client (Tavily, 10 queries)
         ↓
[Source Verification Agent] ← LLM
         ↓
  confidence < 0.70? → re-research
         ↓
[Technical Analysis Agent] ← LLM
         ↓
[Report Writer Agent] ← LLM → ResearchReport (Pydantic)
         ↓
HITL Gate 2: Report Approval
         ↓
[POC Planner Agent] ← LLM
         ↓
[POC Code Generator Agent] ← LLM
         ↓
[Code Reviewer Agent] ← static checks + LLM
         ↓
  needs_revision? → regenerate (max 3x)
         ↓
[Evaluator Agent] ← LLM + weighted rubric
         ↓
  score < 7.0? → halt (FAILED)
         ↓
HITL Gate 3+4: POC + GitHub Push Approval
         ↓
[GitHub Publisher Agent] ← PyGitHub
         ↓
Supabase (metadata, reports, files, logs)
         ↓
FastAPI (REST API)
         ↓
React/Next.js (frontend dashboard)
```

## Key Design Decisions

- **HITL mandatory**: No autonomous GitHub publishing in MVP.
- **State persistence**: `FileCheckpointer` for dev, Supabase for production.
- **Security**: Secret scan before every GitHub write. `.env` never touched.
- **Cost control**: `CostTracker` halts run if spend exceeds `MAX_RUN_COST_USD`.
- **Retry logic**: Code generation retries up to 3x before forcing evaluator.
- **Source threshold**: Re-research automatically if source confidence < 0.70.
