# Deployment

## Local Development

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
cp ../.env.example ../.env
# Edit .env with real keys

# Run CLI test
python ../scripts/test_single_topic.py --topic "MCP for AI Agents"

# Start FastAPI
uvicorn backend.app.main:app --reload --port 8000
```

## Frontend (Phase 6)

```bash
cd frontend
npm install
npm run dev
```

## Production

- Move pipeline execution to Celery + Redis workers
- Use Supabase for state persistence instead of file checkpointer
- Use GitHub App for multi-user GitHub publishing
- Use Docker for isolated POC validation
- Set `MIN_EVAL_SCORE` and `MAX_RUN_COST_USD` appropriately
