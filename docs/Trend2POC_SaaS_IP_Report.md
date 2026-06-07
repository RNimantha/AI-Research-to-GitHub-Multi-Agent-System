# Trend2POC SaaS/IP Development Report

**Product:** Trend2POC  
**Tagline:** From AI Trends to Working POCs  
**Category:** AI Research Operations Platform / AI Trend Intelligence and POC Automation Platform  
**Prepared for:** SaaS/IP product planning  
**Date:** 2026-06-07

---

## 1. Executive Summary

**Trend2POC** should be developed as a small SaaS/IP product, not just a freelance automation script.

The strongest positioning is:

> **Trend2POC is an AI Research Operations Platform that discovers emerging AI trends, verifies sources, generates technical reports, creates runnable proof-of-concept projects, and publishes approved artifacts to GitHub.**

Your key differentiation is not simple web search. The stronger opportunity is:

```text
AI trend discovery
→ source verification
→ technical report
→ runnable POC
→ evaluation
→ human approval
→ GitHub / knowledge base publishing
```

This workflow is valuable for AI engineers, data scientists, freelancers, technical founders, and AI teams.

The existing feature backlog already identifies the correct SaaS gaps:

- Authentication
- Scheduled auto-discovery
- Topic watchlists
- Email / Slack notifications
- Report search and filtering
- Run comparison
- Cost budgets
- Duplicate detection
- Source freshness checks
- Audit logs

---

## 2. Market Context

The broader AI market is moving from simple chatbots toward systems that can execute workflows. Agentic AI systems are increasingly being used to automate multi-step tasks with limited human supervision.

This supports the opportunity for a product like Trend2POC because Trend2POC is not just answering a question. It is executing a complete research-to-implementation workflow.

The important market shift is:

```text
AI assistants → AI workflows → AI agents → AI operations platforms
```

Trend2POC should sit in the **AI operations platform** category for technical research and experimentation.

---

## 3. Product Vision

### Product Name

**Trend2POC**

### Tagline

> **From AI Trends to Working POCs**

### Product Category

```text
AI Research Operations Platform
```

or

```text
AI Trend Intelligence and POC Automation Platform
```

### One-Line Description

> Trend2POC helps AI engineers discover emerging AI trends, verify sources, generate technical reports, create runnable POCs, and publish approved learning artifacts to GitHub.

### Long Description

Trend2POC is a multi-agent SaaS platform that continuously monitors the AI/ML/LLM ecosystem, identifies technically valuable trends, researches them using trusted sources, verifies evidence quality, generates structured engineering reports, creates runnable proof-of-concept projects, evaluates the output, and publishes approved artifacts to GitHub or a team knowledge base.

---

## 4. Target Users

### Primary Initial Users

Start with these users:

```text
AI engineers
Data scientists
ML engineers
AI freelancers
Technical founders
AI consultants
Senior students / researchers building AI demos
```

These users have a clear pain:

```text
Too many AI tools are released every week.
It is hard to know what is real vs hype.
They need to learn fast.
They need runnable demos.
They need GitHub artifacts for clients, interviews, learning, or internal sharing.
```

### Later Users

After MVP validation, expand to:

```text
AI product teams
Innovation teams
R&D teams
Enterprise AI enablement teams
Universities / bootcamps
Consulting companies
Software agencies building AI demos
```

---

## 5. Problem Statement

AI engineers and data scientists face a growing problem:

```text
New AI models, frameworks, protocols, papers, SDKs, and tools appear every week.
Most people do not have time to track, verify, understand, and implement them.
Existing tools may summarize information, but they usually do not create working POCs or GitHub-ready learning packages.
```

This creates several pain points:

```text
Information overload
Low trust in AI trend content
Too much marketing noise
Hard to identify practical topics
Manual report writing takes time
Manual POC creation takes time
Knowledge gets scattered
No structured team learning history
No automatic tracking of topic changes over time
```

Trend2POC solves this by turning AI trend monitoring into a repeatable workflow.

---

## 6. Competitive Landscape

### Perplexity

Perplexity is strong for real-time search and answer generation.

**Difference:**

```text
Perplexity answers questions.
Trend2POC creates verified reports, runnable POCs, and GitHub artifacts.
```

### Elicit

Elicit is strong for scientific and academic research workflows.

**Difference:**

```text
Elicit is paper/research focused.
Trend2POC is AI engineering and implementation focused.
```

### Tavily / Exa / Search APIs

These tools provide search infrastructure for AI agents.

**Difference:**

```text
Search APIs provide raw search capability.
Trend2POC provides the full SaaS workflow on top: discovery, verification, report, POC, evaluation, GitHub, dashboard.
```

### Generic AI Research Agents

Some open-source tools can research topics and generate reports.

**Difference:**

```text
Most generic research agents stop at text output.
Trend2POC specializes in AI engineering trends and produces versioned, approved, GitHub-ready POC projects.
```

---

## 7. Core Product Differentiation

Trend2POC should be different in 7 ways:

```text
1. Focused on AI engineering trends, not general research.
2. Converts research into runnable POCs.
3. Uses source verification and source tiering.
4. Evaluates both report and code quality.
5. Uses human approval before external publishing.
6. Publishes structured artifacts to GitHub.
7. Stores everything as a searchable team knowledge base.
```

This is the product moat.

---

## 8. Recommended Core Workflow

The full workflow should be:

```text
User creates topic / scheduled discovery starts
        ↓
Discovery Agent finds recent AI topics
        ↓
Topic Selection Agent ranks best topics
        ↓
Human approves topic
        ↓
Research Agent performs web research
        ↓
Source Verification Agent validates sources
        ↓
Report Writer Agent creates structured report
        ↓
POC Planner Agent designs project
        ↓
POC Code Generator Agent creates code
        ↓
Code Reviewer Agent checks code quality/security
        ↓
Evaluator Agent scores report + POC
        ↓
Human approves final output
        ↓
GitHub Push Agent publishes artifacts
        ↓
Supabase Logger saves all metadata
        ↓
Frontend displays report, code, score, logs, and approvals
```

---

## 9. Recommended Agent List

| Agent | Purpose |
|---|---|
| Discovery Agent | Finds recent AI trends and candidate topics |
| Topic Selection Agent | Scores and selects topics based on value |
| Research Agent | Performs deep web research |
| Source Verification Agent | Validates credibility, freshness, and source tier |
| Report Writer Agent | Generates structured technical report |
| POC Planner Agent | Designs runnable POC project structure |
| POC Code Generator Agent | Generates code and files |
| Code Reviewer Agent | Checks syntax, dependencies, security, README consistency |
| Evaluator Agent | Scores final output using rubric |
| GitHub Push Agent | Publishes approved files |
| Supabase Logger Agent | Saves run metadata, sources, files, scores, and logs |
| Notification Agent | Sends email/Slack notifications |
| Scheduler Agent | Runs scheduled discovery jobs |

---

## 10. Feature Strategy

The feature backlog can be organized into 7 product pillars.

---

### Pillar 1: Core Research-to-POC Workflow

These are the base features:

```text
Manual topic research
Auto topic discovery
Source-backed research
Structured report generation
POC planning
POC code generation
Code review
Evaluation scoring
GitHub publishing
Frontend dashboard
```

These are required before the product has real value.

---

### Pillar 2: SaaS Foundation

User authentication and accounts are required before Trend2POC can become a multi-user SaaS.

Build:

```text
User authentication
User profiles
Team/workspace model
Per-user research runs
Per-user reports
Per-user GitHub settings
Supabase RLS policies
Usage tracking
Subscription plan limits
```

Minimum SaaS data ownership:

```text
users
teams
team_members
research_runs
reports
sources
generated_files
evaluations
approval_events
cost_events
github_publications
```

---

### Pillar 3: Continuous Monitoring

This turns Trend2POC from a one-time tool into a SaaS users come back to.

Build:

```text
Daily/weekly auto-discovery
Topic watchlists
Company watchlists
Framework watchlists
Keyword tracking
Email digest
Slack alerts
New development alerts
Duplicate topic detection
```

Example watchlists:

```text
MCP
LangGraph
GraphRAG
OpenAI Agents SDK
Claude tool use
LlamaIndex
RAG evaluation
AI observability
Multimodal agents
```

---

### Pillar 4: Trust and Verification

Trust is your strongest differentiator.

Build:

```text
Source tiering
Source freshness check
Dead link detection
Primary vs supporting source labeling
Claim-to-source mapping
Rejected source list
Confidence score
Source credibility score
Technical claim audit
Report quality badge
```

Source hierarchy:

```text
Tier 1: Official docs, official blogs, research papers, GitHub repos, model cards
Tier 2: Medium, Substack, Dev.to, engineering blogs, LinkedIn posts from credible authors
Tier 3: Reddit, Hacker News, Twitter/X, comments, general newsletters
```

Product rule:

```text
LinkedIn and Medium are useful for discovery signals.
Official docs, papers, GitHub repos, and model cards are required for final confidence.
```

---

### Pillar 5: POC Quality and Execution

The phrase “Working POC” is central to your product, so the generated code must be validated.

Build:

```text
Generated POC folder
README
.env.example
requirements.txt
App code
Tests
Syntax check
Dependency check
Secret scan
Docker sandbox execution
stdout/stderr viewer
POC confidence score
```

POC confidence badge:

```text
Generated: Passed
Syntax check: Passed
Dependency check: Passed
Secret scan: Passed
Sandbox run: Passed
Overall POC Confidence: 5/5
```

---

### Pillar 6: Team Knowledge Base

Build:

```text
Report library
Search and filters
Tags
Categories
Version history
Compare two runs
Team dashboard
Collections
Export to PDF / Markdown / Notion
GitHub sync
```

This turns Trend2POC into a reusable knowledge base instead of a single-run agent.

---

### Pillar 7: Cost, Governance, and Control

AI SaaS can become expensive. Cost visibility creates trust.

Build:

```text
Run cost estimate before starting
Token usage per agent
Monthly budget per user/team
80% budget alert
100% budget block
Model selector by agent
Cheap / standard / deep research modes
Audit log
Approval roles
```

---

## 11. Recommended Feature Roadmap

### Phase 1: Private MVP

**Goal:** Prove the main workflow.

Build:

```text
Manual topic input
Auto-discovery
Research agent
Source verification
Report generation
POC generation
Evaluation
GitHub publishing after approval
Supabase storage
Basic dashboard
```

**Success metric:**

```text
A user can generate one useful report + POC in under 10 minutes.
```

---

### Phase 2: SaaS Foundation

**Goal:** Make it usable by real users.

Build:

```text
User authentication
Per-user data isolation
Report library
Run history
GitHub settings
Basic billing-ready usage tracking
```

**Success metric:**

```text
Multiple users can safely use the product without seeing each other’s data.
```

---

### Phase 3: Retention Features

**Goal:** Make users return weekly.

Build:

```text
Scheduled auto-discovery
Topic watchlist
Email/Slack notifications
Report search/filter
Weekly digest email
Duplicate topic detection
```

**Success metric:**

```text
Users receive a useful weekly AI trend digest and return to view reports.
```

---

### Phase 4: Trust Layer

**Goal:** Make outputs credible enough to share with clients/teams.

Build:

```text
Source freshness check
Source tiering
Claim-to-source mapping
Rejected source list
Evaluation details
Report versioning
Audit log
```

**Success metric:**

```text
Users trust the report enough to share it externally.
```

---

### Phase 5: Team SaaS

**Goal:** Convert individual usage into team usage.

Build:

```text
Team workspace
Collaborative review
Approval workflow with roles
Team knowledge base dashboard
Cost budget per team
Multiple GitHub repos
Slack notifications
```

**Success metric:**

```text
Teams use Trend2POC as their AI research and innovation knowledge base.
```

---

### Phase 6: Differentiation Layer

**Goal:** Make the product harder to copy.

Build:

```text
POC sandbox execution
Knowledge graph
Trend timeline
Competitor tracking mode
API access
Jira/Linear integration
Browser extension
Multi-language reports
```

**Success metric:**

```text
Trend2POC becomes part of the user’s weekly engineering workflow.
```

---

## 12. Recommended Next Sprint

### Sprint Goal

> Make Trend2POC usable as a personal SaaS product for one user with recurring value.

### Sprint Features

| Priority | Feature | Why |
|---:|---|---|
| 1 | User authentication | Required for SaaS |
| 2 | User-owned research runs | Data isolation |
| 3 | Report library | Makes outputs reusable |
| 4 | Scheduled auto-discovery | Creates passive value |
| 5 | Topic watchlist | Retention |
| 6 | Email notification | Async workflow |
| 7 | Duplicate topic detection | Saves cost |
| 8 | Run cost estimate | Builds trust |

---

## 13. MVP Feature Set

### MVP Must-Have

```text
User login
Start research run
Auto-discover or manual topic
Agent execution timeline
Source verification
Structured report
POC generation
Evaluation score
Human approval before GitHub push
GitHub publishing
Report library
Run history
Basic cost tracking
```

### MVP Should-Have

```text
Topic watchlist
Scheduled discovery
Email notification
Report search/filter
Duplicate topic detection
Markdown export
Source freshness check
```

### Later

```text
Slack integration
Team workspace
Role-based approvals
POC sandbox execution
Knowledge graph
Competitor tracking
API access
Browser extension
Jira/Linear integration
```

---

## 14. UX / Frontend Strategy

The frontend should feel like:

```text
AI research operations dashboard
```

Not:

```text
AI chatbot wrapper
```

### Important UI Pages

```text
Dashboard
Runs list
Run detail
Reports library
Report detail
Settings / GitHub
Topic watchlist
Scheduled discovery
```

### Most Important Page

```text
/runs/:runId
```

This page should show:

```text
Agent timeline
Current running agent
Step details
Source evidence
HITL approval panel
Evaluation result
GitHub status
Run logs
Cost estimate
```

### Trust UI Elements

Show:

```text
Verified Sources: 8
Rejected Sources: 4
Source Freshness: Passed
Secret Scan: Passed
Code Review: Passed
Evaluation Score: 8.6/10
GitHub Push: Requires Approval
```

This builds user confidence.

---

## 15. Architecture Recommendation

### Backend

```text
FastAPI
LangGraph
Celery/Redis for background jobs
Supabase PostgreSQL
Supabase Auth
GitHub API
Search API such as Tavily/Exa/Brave
LLM provider: Claude/OpenAI/Gemini
```

### Frontend

```text
React or Next.js
Dashboard UI
Polling first
SSE later for live agent events
```

### Data Storage

```text
Supabase tables:
users
teams
team_members
research_runs
topics
topic_watchlists
sources
source_scores
claims
claim_sources
reports
report_versions
generated_files
poc_runs
evaluations
agent_logs
approval_events
notifications
cost_events
github_publications
```

---

## 16. Technical Architecture

### Event Flow

```text
User starts run
→ FastAPI creates research_run
→ Background worker starts LangGraph workflow
→ Agents update run state
→ Supabase stores progress and logs
→ Frontend polls or receives SSE events
→ User approves HITL gates
→ GitHub push happens only after approval
→ Final report stored and displayed
```

### Recommended Execution Model

For MVP:

```text
FastAPI + background task
Supabase for state
Polling frontend every 2–3 seconds
```

For production:

```text
FastAPI + Celery + Redis
SSE for live updates
Supabase for persistence
Worker queue for long-running research jobs
```

---

## 17. Database Design

Minimum tables:

```text
users
research_runs
topics
topic_watchlists
sources
reports
generated_files
evaluations
approval_events
agent_logs
github_publications
cost_events
notifications
```

### `research_runs`

```text
id
user_id
topic
status
current_agent
progress
started_at
completed_at
estimated_cost_usd
actual_cost_usd
github_url
error_message
```

### `reports`

```text
id
user_id
run_id
topic_slug
title
report_markdown
report_json
eval_score
version
github_url
created_at
```

### `sources`

```text
id
run_id
title
url
source_type
source_tier
published_date
credibility_score
used_in_report
rejected_reason
```

### `approval_events`

```text
id
run_id
user_id
approval_type
status
notes
created_at
```

### `cost_events`

```text
id
run_id
agent_name
model
input_tokens
output_tokens
estimated_cost_usd
latency_ms
created_at
```

---

## 18. IP / Moat Strategy

Your protectable IP is not basic LangGraph code.

### Weak IP

Easy to copy:

```text
Web search
Basic report generation
Basic GitHub push
Generic agent orchestration
```

### Strong IP

Harder to copy:

```text
Source scoring system
Topic ranking algorithm
POC feasibility scoring
Claim-to-source mapping
Evaluation rubric
POC sandbox validation
Prompt/eval dataset
Historical trend database
User feedback loop
Domain templates
Team knowledge graph
```

Build your IP around these.

---

## 19. Monetization Strategy

### Free Plan

```text
3 runs/month
Manual topic only
Markdown export
Limited report history
No scheduled discovery
```

### Pro Plan — USD 19–29/month

```text
50 runs/month
Scheduled discovery
Topic watchlist
GitHub publishing
PDF/Markdown export
Weekly digest
Basic POC generation
```

### Team Plan — USD 99–299/month

```text
Team workspace
Shared report library
Slack notifications
Collaborative review
Approval workflow
Cost budgets
Multiple GitHub repos
Custom templates
```

### Enterprise

```text
SSO
Custom source policies
Private deployment
Audit exports
Advanced API access
Dedicated support
Compliance controls
```

---

## 20. Go-To-Market Strategy

### Start Narrow

Start with:

```text
AI engineers and freelancers who need to quickly learn and demo new AI technologies.
```

### First Use Cases

```text
Generate weekly AI engineering reports
Build client demo POCs
Prepare for AI interviews
Create GitHub learning portfolio
Track new AI frameworks
Track competitor releases
```

### Marketing Channels

```text
LinkedIn technical posts
GitHub repo examples
YouTube demos
AI newsletters
Reddit r/LocalLLaMA and r/MachineLearning
Hacker News launch
Indie Hackers
Product Hunt
Medium/Substack technical articles
```

### Demo Strategy

Show a simple demo:

```text
Input: “MCP for AI Agents”
Output:
- verified sources
- full technical report
- runnable FastAPI/LangGraph POC
- evaluation score
- GitHub folder
```

This demo will communicate the value quickly.

---

## 21. Risk Analysis

### Risk 1: It becomes just another AI search tool

Mitigation:

```text
Focus on POC generation, GitHub publishing, evaluation, and team knowledge base.
```

### Risk 2: Generated reports are not trusted

Mitigation:

```text
Source tiering
Claim-to-source mapping
Source freshness check
Rejected source list
Evaluation score
```

### Risk 3: Generated POC does not run

Mitigation:

```text
Syntax check
Dependency validation
Secret scan
Sandbox execution
Test generation
```

### Risk 4: LLM costs become high

Mitigation:

```text
Cost estimate before run
Budget limits
Model routing
Caching
Duplicate topic detection
Scheduled run limits
```

### Risk 5: GitHub publishing is unsafe

Mitigation:

```text
Human approval
Secret scanning
Fine-grained GitHub PAT
No .env push
Audit log
```

### Risk 6: SaaS has low retention

Mitigation:

```text
Scheduled discovery
Topic watchlist
Weekly digest
Report library
Trend timeline
Competitor tracking
```

---

## 22. What Not to Build First

Avoid these in the first version:

```text
Mobile app
Enterprise SSO
Browser extension
Complex knowledge graph
Fine-tuning models
On-prem deployment
Real-time collaborative editing
Huge marketplace
Multi-language support
```

These can come later.

---

## 23. Success Metrics

### Activation Metrics

```text
User creates first research run
User generates first report
User generates first POC
User publishes to GitHub
```

### Retention Metrics

```text
User creates watchlist
User opens weekly digest
User returns within 7 days
User re-runs same topic later
```

### Quality Metrics

```text
Average evaluation score
Source verification pass rate
POC syntax pass rate
POC sandbox pass rate
Report usefulness rating
```

### Business Metrics

```text
Free-to-paid conversion
Monthly active users
Runs per user
Cost per run
Gross margin per run
Team workspace adoption
```

---

## 24. Recommended Final Product Scope

For the first SaaS/IP version, build:

```text
1. Auth and user accounts
2. Manual + auto topic discovery
3. Topic watchlist
4. Scheduled weekly discovery
5. Multi-agent research workflow
6. Source verification
7. Structured technical reports
8. POC code generation
9. Evaluation scoring
10. Human approval gates
11. GitHub publishing
12. Supabase report library
13. Report search/filter
14. Email notifications
15. Cost estimate before run
16. Duplicate topic detection
```

This gives you a real SaaS product, not just a demo.

---

## 25. Final Recommendation

Build Trend2POC as your IP.

But be very clear:

```text
Do not sell it as a web search agent.
Do not sell it as a chatbot.
Do not sell it as a generic research assistant.
```

Sell it as:

> **A research-to-implementation engine for AI teams.**

Your best first product wedge is:

> **AI engineering trend monitoring that creates verified reports and runnable POCs.**

Your strongest differentiators are:

```text
Source verification
POC generation
POC validation
GitHub publishing
Human approval
Team knowledge base
Trend tracking over time
```

If you build those well, Trend2POC can become a real small SaaS product and a valuable personal IP asset.

