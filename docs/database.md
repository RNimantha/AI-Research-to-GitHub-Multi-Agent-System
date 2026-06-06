# Database — Supabase Schema

Run these SQL statements in the Supabase SQL editor.

## Tables

```sql
CREATE TABLE research_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    status TEXT DEFAULT 'pending',
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

## Row Level Security

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
