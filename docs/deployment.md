# Deployment Guide

This page explains how to run the system locally for development and what to do when you are ready for production.

---

## What You Need Before Starting

- Python 3.11 or later
- Node.js 18 or later
- At least one LLM API key (Anthropic or OpenAI)
- At least one search API key (Tavily is recommended)
- A GitHub repository for your knowledge base (can be created before or after setup)

Supabase and Facebook are optional — the system works without them.

---

## Local Setup

### 1. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the minimum required values:

```bash
ANTHROPIC_API_KEY=sk-ant-...        # or OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
GITHUB_TOKEN=github_pat_...
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=trend2poc-knowledge-base
API_SECRET_KEY=any-random-string-you-choose
```

Everything else has sensible defaults.

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. You can open `http://localhost:8000/docs` to see all available endpoints.

### 3. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The dashboard is now at `http://localhost:3000`.

### 4. Optional — Run a quick CLI test

To verify the pipeline works without the UI:

```bash
python scripts/test_single_topic.py --topic "MCP for AI Agents"
```

This runs the full pipeline for one topic and prints results to the terminal. GitHub push is disabled in this mode.

---

## Connector Setup

### GitHub

See [docs/github-auth.md](github-auth.md) for full instructions.

Short version: create a fine-grained PAT → paste it in Settings → GitHub → click Test connection.

### Supabase (optional)

1. Create a project at supabase.com
2. Run the SQL from [docs/database.md](database.md) in the Supabase SQL editor
3. Paste the URL and keys in Settings → Supabase
4. Click Test connection

### Facebook (optional)

See [docs/connectors.md](connectors.md) — Facebook section.

Short version: create a Facebook App → generate a Page Access Token → paste it and your Page ID in Settings → Facebook.

---

## Environment Variables Reference

| Variable | Required | What it does |
|---|---|---|
| `ANTHROPIC_API_KEY` | One of these | Uses Claude as the LLM |
| `OPENAI_API_KEY` | One of these | Uses GPT as the LLM |
| `TAVILY_API_KEY` | Recommended | Web search for research and discovery |
| `GITHUB_TOKEN` | For publishing | Fine-grained PAT for knowledge-base repo |
| `GITHUB_REPO_OWNER` | For publishing | Your GitHub username or org |
| `GITHUB_REPO_NAME` | For publishing | The repo where reports are pushed |
| `API_SECRET_KEY` | Yes | Secures the backend API |
| `SUPABASE_URL` | Optional | Supabase project URL |
| `SUPABASE_ANON_KEY` | Optional | Supabase public key (frontend) |
| `SUPABASE_SERVICE_ROLE_KEY` | Optional | Supabase admin key (backend only) |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Optional | Facebook Page posting |
| `FACEBOOK_PAGE_ID` | Optional | Your Facebook Page numeric ID |
| `MIN_EVAL_SCORE` | No | Minimum score to allow GitHub push (default: 7.0) |
| `MAX_RUN_COST_USD` | No | Cost limit per run (default: 3.00) |
| `AUTO_PUSH_TO_GITHUB` | No | Always false — human approval required |

---

## Production Considerations

The local setup uses simple background tasks and file-based checkpoints. This works fine for personal use. For a production deployment with multiple users, these things should be changed:

### Move background jobs to a queue

The pipeline currently runs in FastAPI `BackgroundTasks`. This means if the server restarts, in-flight runs are lost. For production, move to Celery + Redis:

- Runs are queued in Redis
- Worker processes pick them up and run them
- If a worker crashes, the job is retried automatically

### Use Supabase for state instead of files

File checkpoints work locally but do not scale across multiple server instances. With Supabase configured, use the Supabase checkpointer instead of the file checkpointer.

### Use a GitHub App for multi-user publishing

A Personal Access Token only works for one user's repos. For a product where each user connects their own GitHub, use a GitHub App with per-user installation tokens.

### Run generated code in Docker

Currently, generated POC code is syntax-checked but not executed. To actually verify it runs, execute it inside a Docker container with no network access and a timeout. This prevents any generated code from accessing your host system.

### Set reasonable cost limits

Before going live, set `MAX_RUN_COST_USD` to a sensible value per run (default is $3.00). Set `MIN_EVAL_SCORE` to your quality bar (default is 7.0).

### Add authentication

Currently there is no user login system. All runs belong to whoever has the API key. Adding Supabase Auth gives you proper per-user accounts, login/logout, and password reset.
