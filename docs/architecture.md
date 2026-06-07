# How the System is Built

## The Big Picture

Trend2POC takes an AI topic — either one you give it, or one it finds itself — and turns it into three things:

1. A detailed technical report explaining what the topic is and why it matters
2. A small runnable code project that demonstrates the concept
3. A published folder in your GitHub repository with everything inside

The system does this by running a series of AI agents, one after another. Each agent has one specific job. When an agent finishes, it hands its results to the next one. You stay in control the whole time through four approval points.

---

## The Pipeline — Step by Step

```
You start a run (with or without a topic)
         ↓
Discovery Agent finds recent AI topics from the web
         ↓
Topic Selection Agent picks the most valuable one
         ↓
── YOU APPROVE THE TOPIC ──
         ↓
Research Agent searches the web deeply using AI-guided queries
         ↓
Source Verification Agent checks which sources are trustworthy
         ↓
Technical Analysis Agent turns raw research into engineer-level understanding
         ↓
Report Writer Agent writes the full structured report
         ↓
── YOU APPROVE THE REPORT ──
         ↓
POC Planner Agent designs a small runnable project
         ↓
Code Generator Agent writes the code (then critiques and fixes its own work)
         ↓
Code Reviewer Agent checks syntax, dependencies, and secrets
         ↓
Evaluator Agent scores the report and code from 0 to 10
         ↓
── YOU DECIDE WHETHER TO APPLY IMPROVEMENTS (optional) ──
         ↓
── YOU APPROVE THE GITHUB PUSH ──
         ↓
GitHub Publisher Agent uploads everything to your knowledge-base repo
         ↓
Done — report, code, and GitHub link all saved
```

---

## The Four Approval Points

You cannot accidentally publish bad research to GitHub. The system stops and waits for you at four points:

| Stop | When it happens | What you can do |
|---|---|---|
| Topic Approval | After discovery | Approve, reject, or change the topic |
| Report Review | After the report is written | Approve or send back for revision |
| Improvement Review | If the evaluator finds weak sections | Apply AI rewrites or skip |
| GitHub Push | After scoring passes | Publish, hold, or reject |

None of these steps are skipped automatically. You are always in control of what reaches GitHub.

---

## How State Works

The system keeps one object — called `Trend2POCState` — for each run. Think of it as a clipboard that gets passed from agent to agent.

- Each agent reads from the clipboard, does its work, and writes its results back
- After every step, the clipboard is saved to a file on disk (`.checkpoints/{run_id}.json`)
- If something fails, the clipboard is still there — the system can pick up from where it left off
- The frontend watches the clipboard in real time and shows you what is happening

This is why you can retry a failed run without restarting from the beginning.

---

## Real-Time Updates

The frontend connects to the backend using Server-Sent Events (SSE). This is a simple one-way stream from server to browser.

Every time an agent starts working, it immediately updates the status in the clipboard and saves it. The frontend sees this change within one second and updates the screen. You do not need to refresh the page.

---

## Key Design Decisions

**No autonomous publishing.** The system will never push to GitHub without your explicit approval. The `AUTO_PUSH_TO_GITHUB` flag defaults to `false` and cannot be bypassed.

**State on disk, not in memory.** If the server restarts mid-run, the run survives. The checkpoint file on disk is the source of truth.

**Source quality gates.** If the Research Agent finds sources with a combined confidence score below 0.70, it automatically searches again rather than using weak evidence.

**Code self-critique.** The Code Generator writes code, then reviews its own output and fixes errors before any human sees it. This catches the obvious mistakes before the external Code Reviewer runs.

**Secret scanning.** Before any file reaches GitHub, every file is scanned for API keys, tokens, and passwords. If anything suspicious is found, the push is blocked.

**Cost limits.** Every LLM call is tracked. If a run exceeds `MAX_RUN_COST_USD`, it stops automatically.

---

## The Three Source Tiers

The Discovery and Research agents classify every source they find into one of three tiers:

| Tier | Examples | How it is used |
|---|---|---|
| Tier 1 — Primary | Official docs, arXiv papers, GitHub repos, company blogs | Required — every topic must have at least one |
| Tier 2 — Supporting | Medium, Substack, Dev.to, personal engineering blogs | Supports Tier 1 evidence but cannot stand alone |
| Tier 3 — Community | Reddit, Hacker News, Twitter/X | Trend signals only — must be backed by Tier 1 |

A topic discovered only from Reddit posts will be rejected. It needs a paper, a GitHub repo, or official documentation to be considered real.

---

## Folder Structure

```
backend/app/
├── agents/          One file per agent (11 total)
├── api/             FastAPI routes — runs, reports, github, settings, social
├── core/
│   ├── schemas.py   All data shapes (ResearchReport, POCProject, etc.)
│   └── prompts/     Every LLM prompt stored as a .md file
├── graph/
│   ├── state.py     The clipboard object (Trend2POCState)
│   ├── workflow.py  The pipeline — calls each agent in order
│   └── checkpoints.py  Save/load state to disk
└── integrations/    GitHub, Supabase, Facebook, LLM, Search clients

frontend/app/
├── dashboard/       Overview of all runs
├── runs/[run_id]/   Live run detail — approvals, report, code, logs
├── reports/         Browse and read published reports
└── settings/        GitHub, Supabase, Facebook configuration
```
