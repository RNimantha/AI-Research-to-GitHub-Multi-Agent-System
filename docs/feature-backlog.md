# Trend2POC — Feature Backlog

> **Document type:** Product backlog  
> **Audience:** PMO, BA, Engineering, Stakeholders  
> **Last updated:** 2026-06-07  

---

## Priority Legend

| Symbol | Priority | Criteria |
|---|---|---|
| 🔴 | High | Core product gap — blocks key user journeys or multi-user use |
| 🟡 | Medium | Improves UX or unlocks team use cases |
| 🟢 | Growth | Differentiates product, drives retention or expansion |
| 🔵 | Quality | Reliability, cost control, regression safety |
| ⚪ | Future | Nice to have, low urgency |

---

## 🔴 High Priority — Core Product Gaps

| ID | Feature | Description | Why |
|---|---|---|---|
| F-01 | **User authentication & accounts** | Login, registration, per-user data isolation | Currently no auth — multi-user SaaS not possible |
| F-02 | **Scheduled auto-discovery** | Run discovery automatically on a daily or weekly schedule without manual trigger | Core value prop — users want passive updates |
| F-03 | **Topic watchlist** | User saves topics they want tracked; system alerts when new developments are found | Retains users between manual runs |
| F-04 | **Email / Slack notifications** | Alert user when run completes, HITL gate needs action, or publish succeeds | Unblocks async usage — users leave the browser |
| F-05 | **Report search & filter** | Browse published reports by tag, score, date, topic category | Currently no search — knowledge base is not browsable |
| F-06 | **Run history with comparison** | Compare two runs on the same topic side by side | Track how AI landscape changes over time |

---

## 🟡 Medium Priority — User Experience

| ID | Feature | Description | Why |
|---|---|---|---|
| F-07 | **Custom topic templates** | User pre-defines research angles for specific domains (security, fintech, healthcare AI) | Different teams need different research lenses |
| F-08 | **Report export (PDF, Markdown, Notion)** | Download report as PDF or Markdown; push to Notion | Currently only GitHub push — users need offline copies |
| F-09 | **Collaborative review** | Multiple team members leave comments on a report before approval | Teams review research together before publishing |
| F-10 | **Report versioning** | When a topic is re-researched, keep v1 and v2 as separate dated versions | AI landscape changes — old reports become stale |
| F-11 | **Approval workflow with roles** | Admin approves GitHub push; junior role can approve topic only | Enterprise teams need tiered approval controls |
| F-12 | **Cost budget per user/team** | Set monthly LLM spend limit; alert at 80%; block at 100% | Prevents unexpected bills in team environments |
| F-13 | **POC sandbox execution** | Run generated code in isolated Docker container; show stdout/stderr in UI | Currently code is generated but never verified running |
| F-14 | **Report feedback / rating** | After reading, user rates usefulness 1–5 | Ratings feed back into topic selection scoring over time |

---

## 🟢 Growth — Differentiation Features

| ID | Feature | Description | Why |
|---|---|---|---|
| F-15 | **Knowledge graph** | Visualise how topics connect (RAG → Vector DB → Embeddings → Multimodal) | Helps users discover related topics and gaps |
| F-16 | **Trend timeline** | Show when each topic was first discovered, researched, and how its score changed | Demonstrates long-term platform value |
| F-17 | **Competitor tracking mode** | Monitor what a specific company (Anthropic, OpenAI, Google) releases each week | High-value for AI product teams and founders |
| F-18 | **Team knowledge base dashboard** | Aggregated view of all team-published reports with search and tagging | Turns individual research into a shared team asset |
| F-19 | **Weekly digest email** | "Here's what's new in AI this week" auto-generated from approved reports | Drives passive re-engagement without user effort |
| F-20 | **API access** | Webhook and REST API for teams to integrate Trend2POC output into their own tools | Unlocks integration with internal portals, wikis, dashboards |
| F-21 | **Custom GitHub repo per project** | User maintains separate knowledge bases for different teams or domains | Enterprise teams work across multiple domains |

---

## 🔵 Quality & Reliability

| ID | Feature | Description | Why |
|---|---|---|---|
| F-22 | **Source freshness check** | Before publishing, verify all source URLs still resolve (HTTP 200) | Dead links in reports undermine credibility |
| F-23 | **Duplicate topic detection** | Block or warn if a closely matching topic was researched recently | Prevents wasted runs and duplicate knowledge base entries |
| F-24 | **LLM fallback routing** | If primary LLM provider is down, auto-retry with fallback provider | Currently fails hard on provider outage |
| F-25 | **Run cost estimate before starting** | Show user estimated cost ("approx $0.80") before they confirm | Builds trust; prevents surprise spend |
| F-26 | **Regression eval suite** | Run golden test cases after any prompt change to catch quality regressions | Prompt changes currently have no safety net |
| F-27 | **Audit log** | Full trail of who approved what, when, with notes — exportable | Required for compliance in regulated industries |

---

## ⚪ Future / Nice to Have

| ID | Feature | Description | Why |
|---|---|---|---|
| F-28 | **Voice briefing** | TTS audio summary of report — listen on commute | Accessibility and passive consumption |
| F-29 | **LLM model selector per agent** | Use cheap model for discovery, expensive for report writing | Cost optimisation for high-volume teams |
| F-30 | **Browser extension** | Clip an article → trigger a research run on that topic instantly | Zero-friction topic discovery from existing workflows |
| F-31 | **Jira / Linear integration** | Auto-create implementation tickets from POC task list | Connects research output to engineering workflow |
| F-32 | **Multi-language reports** | Generate reports in Japanese, German, Spanish, etc. | Global teams with non-English working language |

---

## Recommended Next Sprint

Based on impact vs engineering effort:

| Priority | Feature ID | Feature | Rationale |
|---|---|---|---|
| 1 | F-02 | Scheduled auto-discovery | Highest user value, medium effort — unlocks passive use |
| 2 | F-04 | Email / Slack notifications | Unblocks async usage without requiring the user to watch the dashboard |
| 3 | F-05 | Report search & filter | Product feels incomplete without basic browsability |
| 4 | F-23 | Duplicate topic detection | Prevents wasted runs and LLM cost |
| 5 | F-25 | Run cost estimate | Builds user trust before spend commits |

---

## Out of Scope (Current MVP)

The following are explicitly deferred:

- Mobile app
- On-premise / self-hosted enterprise deployment
- Fine-tuning any LLM on internal reports
- Real-time collaborative editing of reports
- Automated A/B testing of prompts in production

---

## Notes

- All features requiring user accounts (F-01) are blocked until F-01 is delivered.
- F-13 (sandbox execution) requires Docker infrastructure and security review before implementation.
- F-11 (approval roles) depends on F-01 (auth) being in place first.
- F-20 (API access) should be scoped carefully to avoid exposing Supabase service role keys.
