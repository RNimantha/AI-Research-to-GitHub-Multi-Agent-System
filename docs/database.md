# Database — What Gets Stored and Why

The system uses Supabase (PostgreSQL) to store everything from a research run. This page explains what each table holds and how to set it up.

Supabase is optional for local development. Without it, state is saved to `.checkpoints/` files. For anything beyond personal local use, Supabase is recommended.

---

## Tables Overview

| Table | What it stores |
|---|---|
| `research_runs` | One row per run — status, topic, costs, GitHub URL |
| `reports` | The full report content for completed runs |
| `sources` | Every web source found during research |
| `generated_files` | Every code file the system generated |
| `approvals` | Every time a user clicked approve or reject |
| `agent_logs` | Every agent call — input, output, tokens, cost, time |

---

## Table Details

### research_runs

The main table. Every time you start a run, a row is created here. It gets updated as the pipeline progresses.

Key fields:
- `status` — where the run is right now (e.g. `researching`, `awaiting_topic_approval`, `complete`)
- `selected_topic` — the topic chosen by the system or provided by you
- `eval_score` — final evaluation score once complete
- `github_url` — the GitHub folder link once published
- `estimated_cost_usd` — total LLM cost for the run
- `error_log` — list of any errors that occurred

### reports

Stores the full report content after the Report Writer Agent finishes.

Key fields:
- `report_json` — the complete structured report (all fields from the `ResearchReport` schema)
- `report_markdown` — the same report rendered as Markdown
- `eval_score` — score given by the Evaluator Agent
- `eval_flags` — list of specific issues found during evaluation
- `status` — `draft` while in progress, `published` after GitHub push

### sources

Every source the Research Agent found, with quality information.

Key fields:
- `url` and `title` — the source itself
- `source_type` — `official_docs`, `paper`, `github`, `blog`, `community`, etc.
- `credibility_score` — 0 to 1 score assigned by the Source Verification Agent
- `status` — `verified` or `rejected`

### generated_files

Every file the Code Generator created.

Key fields:
- `file_path` — where the file lives in the project (e.g. `app/main.py`)
- `file_content` — the full file content
- `purpose` — one-line description of what the file does

### approvals

An audit trail of every decision you made.

Key fields:
- `gate_name` — which gate this was (`topic_approval`, `report_approval`, `poc_approval`, `github_push`)
- `action` — what you did (`approved`, `rejected`, `revision_requested`)
- `notes` — any notes you added when approving or rejecting
- `created_at` — exact timestamp

### agent_logs

A detailed log of every agent call. Used for debugging, cost tracking, and showing the agent timeline in the UI.

Key fields:
- `agent_name` — which agent ran
- `model_name` — which LLM model was used
- `input_tokens` / `output_tokens` — how many tokens were used
- `estimated_cost_usd` — cost for this specific call
- `latency_ms` — how long the call took
- `status` — `success` or `error`
- `error_message` — error details if it failed

---

## How to Set It Up

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to your project → **SQL Editor**
3. Run the SQL below to create all tables and indexes
4. Go to **Project Settings → API** and copy:
   - Project URL
   - anon (public) key
   - service_role key
5. Add these to your `.env` file
6. Or paste them in Settings → Supabase in the dashboard

---

## SQL — Create Tables

**If you already have the table**, run this first to add the state column:

```sql
ALTER TABLE research_runs ADD COLUMN IF NOT EXISTS state_json JSONB;
```

```sql
CREATE TABLE research_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    status TEXT DEFAULT 'pending',
    state_json JSONB,
    input_topic TEXT,
    selected_topic JSONB,
    approved_topic TEXT,
    eval_score FLOAT,
    github_url TEXT,
    github_folder TEXT,
    llm_provider TEXT,
    model_name TEXT,
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    estimated_cost_usd FLOAT DEFAULT 0,
    search_api_calls INT DEFAULT 0,
    error_log JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES research_runs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    topic_slug TEXT NOT NULL,
    topic_name TEXT NOT NULL,
    one_liner TEXT,
    tags TEXT[] DEFAULT '{}',
    report_json JSONB NOT NULL,
    report_markdown TEXT,
    eval_score FLOAT,
    eval_flags TEXT[] DEFAULT '{}',
    github_url TEXT,
    github_folder TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES research_runs(id) ON DELETE CASCADE,
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    source_type TEXT,
    published_date TEXT,
    accessed_at TIMESTAMPTZ DEFAULT NOW(),
    summary TEXT,
    credibility_score FLOAT,
    status TEXT DEFAULT 'verified'
);

CREATE TABLE generated_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES research_runs(id) ON DELETE CASCADE,
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_type TEXT,
    purpose TEXT,
    file_content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES research_runs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    gate_name TEXT NOT NULL,
    action TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES research_runs(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    status TEXT,
    input_json JSONB,
    output_json JSONB,
    error_message TEXT,
    model_name TEXT,
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    estimated_cost_usd FLOAT DEFAULT 0,
    latency_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_topic_slug ON reports(topic_slug);
CREATE INDEX idx_reports_tags ON reports USING GIN(tags);
CREATE INDEX idx_runs_user_id ON research_runs(user_id);
CREATE INDEX idx_runs_status ON research_runs(status);
CREATE INDEX idx_sources_run_id ON sources(run_id);
```

---

## SQL — Row Level Security

Row Level Security (RLS) means each user can only see their own data. Without this, anyone with the anon key could read all runs from all users.

```sql
ALTER TABLE research_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own research runs"
ON research_runs FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own research runs"
ON research_runs FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own reports"
ON reports FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own reports"
ON reports FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own approvals"
ON approvals FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own approvals"
ON approvals FOR INSERT WITH CHECK (auth.uid() = user_id);
```

---

## Security Rule

The `service_role` key bypasses RLS. It must only be used by the backend server. Never send it to the frontend. Never put it in any JavaScript file or API response.

The `anon` key is safe for the frontend — it follows RLS rules and can only see what the logged-in user owns.
