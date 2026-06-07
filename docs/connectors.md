# Connectors — GitHub, Supabase, Facebook

Connectors are integrations that let the system talk to external services. Each connector has its own settings page in the dashboard. None of them are required to run the pipeline — but each one adds something useful.

---

## GitHub Connector

**What it does:** Publishes your approved research report and code to a GitHub repository. This is where your knowledge base lives.

**Where to configure:** Settings → GitHub

### What you need

A GitHub Personal Access Token (PAT) with write access to one specific repository.

### How to set it up

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Under **Repository access**, choose "Only selected repositories" and pick your knowledge-base repo
4. Under **Permissions**, set:
   - Contents → Read and write
   - Metadata → Read-only
5. Copy the token
6. Go to Settings → GitHub in the dashboard, paste the token, and save

### What gets published

When you approve a GitHub push, the system creates this folder structure in your repo:

```
reports/
└── 2026-06-07_topic-slug/
    ├── README.md           Human-friendly overview and setup instructions
    ├── report.md           Full technical report
    ├── architecture.md     Architecture and data flow explanation
    ├── implementation.md   How the POC code works
    ├── evaluation.md       Score breakdown and flags
    ├── references.md       Verified sources with links
    ├── .env.example        Required environment variables (no real values)
    ├── requirements.txt    Python dependencies
    ├── app/                Runnable POC source code
    ├── tests/              Basic tests
    └── examples/           Sample inputs and outputs
```

### Security checks before every push

Before any file reaches GitHub, the system scans for secret patterns including:

- API keys starting with `sk-`, `ghp_`, `github_pat_`
- Private key headers (`BEGIN PRIVATE KEY`)
- AWS and Anthropic key patterns

If anything is found, the push is blocked and the error is shown.

### Test connection

The settings page has a **Test connection** button. It verifies:
- Token is valid
- Repo exists and is accessible
- The token actually has write permission (it does a test write and deletes it)

---

## Supabase Connector

**What it does:** Stores all run data — reports, sources, generated files, approvals, agent logs, and costs — in a PostgreSQL database. This makes your data persistent and queryable across browser sessions.

**Where to configure:** Settings → Supabase

**Is it required?** No. Without Supabase, runs still work and state is saved locally in `.checkpoints/` files. But local files are lost if you move machines or clear the folder.

### What you need

- A Supabase project (free tier works)
- The project URL
- The anon key (for frontend)
- The service role key (for backend only)

### How to set it up

1. Create a project at supabase.com
2. Go to **Project Settings → API**
3. Copy the Project URL, anon key, and service role key
4. Go to Settings → Supabase in the dashboard, paste all three, and save
5. In the Supabase SQL editor, run the SQL from `docs/database.md` to create all tables

### What gets stored

| Table | What it holds |
|---|---|
| `research_runs` | One row per run — status, topic, cost, GitHub URL |
| `reports` | Full report JSON and markdown for each completed run |
| `sources` | Every source found and its credibility score |
| `generated_files` | Every code file generated |
| `approvals` | Every time you clicked approve or reject, with timestamp |
| `agent_logs` | Every agent call — input, output, tokens used, cost, latency |

### Row-level security

Every table has Row Level Security enabled. This means each user can only see their own data. If you log in as user A, you cannot see user B's runs, even if they are in the same database.

The service role key bypasses this — it is only used by the backend server and must never be sent to the frontend.

### Test connection

The settings page has a **Test connection** button that runs a simple read query to verify the credentials work.

---

## Facebook Connector

**What it does:** Posts an announcement to your Facebook Page when a report is published to GitHub. The post includes the topic name, a one-line summary, the eval score, tags, and a link to the GitHub folder.

**Where to configure:** Settings → Facebook

**Is it required?** No. It is completely optional. The pipeline runs fine without it.

### What you need

- A Facebook Developer App
- A Page Access Token with posting permissions
- The numeric ID of your Facebook Page

### What gets posted

When you click **Post to Facebook** in a completed run, the post looks like this:

```
New Research Report: MCP for AI Agents

A protocol that standardizes how AI agents connect to external tools,
replacing custom integrations with a single shared interface.

Eval Score: 8.4/10
Tags: #AgenticAI #MCP #LLMTools #AIEngineering

Read the full report and runnable POC: https://github.com/your-repo/...
```

### How to get a Page Access Token

1. Go to **developers.facebook.com** → your App → **Graph API Explorer**
2. Select your App in the top-right dropdown
3. Click **Generate Access Token** and grant `pages_manage_posts` and `pages_read_engagement`
4. In the Explorer, run: `GET /me/accounts` — find your Page and copy its `access_token`
5. To make it last 60 days, exchange it for a long-lived token:
   - `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN`
6. Paste the token and your Page ID into Settings → Facebook

### How to find your Page ID

Go to your Facebook Page → click **About** → scroll down to find the numeric Page ID. It looks like `123456789012345`.

### Auto-post toggle

In Settings → Facebook, there is an **Auto-post after GitHub publish** toggle. When enabled, the system automatically posts to Facebook immediately after a successful GitHub push without requiring you to click the button manually.

### Token expiry

Page Access Tokens expire after 60 days unless you generate a non-expiring one through the App Dashboard using a System User. For personal use, refreshing every 60 days is acceptable. For a production system serving multiple users, use a System User with a permanent token.

---

## Connector Comparison

| Feature | GitHub | Supabase | Facebook |
|---|---|---|---|
| Required? | Recommended | Optional | Optional |
| What it stores | Research artifacts | All run data | Nothing stored — posts only |
| Token type | Fine-grained PAT | Service role key + anon key | Page Access Token |
| Token location | `.env` / settings page | `.env` / settings page | `.env` / settings page |
| Expires? | No (until revoked) | No | Yes, 60 days |
| Test button? | Yes | Yes | Yes |
| Needs approval before action? | Yes (HITL gate) | No (automatic) | No (manual button) |
