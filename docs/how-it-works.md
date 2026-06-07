# How It Works — Plain English Guide

This document explains what happens inside the system when you start a research run. No jargon, no assumptions about what you already know.

---

## Starting a Run

You go to the dashboard and click **New Run**.

You can either:
- Leave the topic blank — the system will find a recent AI topic itself
- Type a specific topic — the system will skip discovery and go straight to research

A run ID is created. The pipeline starts in the background. Your browser shows live updates.

---

## Step 1 — Discovery (finding topics)

**What happens:** The system runs ten web searches across different AI categories — new models, agent frameworks, RAG improvements, developer tools, and so on. It collects the results, removes duplicates, and passes them all to an LLM.

**What the LLM does:** Reads all the search results and identifies the most interesting recent topics. For each topic it finds, it scores it on six dimensions: novelty, practical usefulness, POC feasibility, technical depth, source quality, and business value. It returns a ranked list.

**What you see in the UI:** The status changes to "Discovering" and you see a live update within a second of the agent starting.

**If you typed a topic yourself:** Discovery is skipped entirely. Your topic goes straight to research after you approve it.

---

## Step 2 — Topic Approval (your first decision)

The system shows you the discovered topics with scores and summaries. You pick one, change it, or reject them all.

Until you approve a topic, nothing else happens. The run just waits.

Once you approve, the system continues automatically.

---

## Step 3 — Research (deep web search)

**What happens:** The Research Agent uses a technique called tool-use. Instead of running fixed searches, it decides its own queries based on what it finds. It starts with broad searches, identifies gaps, and drills into specifics. It keeps searching until it feels it has enough evidence.

**Minimum searches:** At least six queries covering eight angles — definition, background, architecture, tools, use cases, limitations, recent developments, and comparisons.

**When done:** The agent calls a special `finalize_research` function with structured research notes and all the sources it found.

---

## Step 4 — Source Verification

**What happens:** A separate agent reads all the sources gathered during research. It checks:

- Is this source trustworthy? (official docs > blog posts > Reddit)
- Is it recent enough?
- Does more than one source support each key claim?
- Is there anything that contradicts itself?

**Output:** A list of verified sources, a list of rejected sources, and a confidence score between 0 and 1.

**If confidence is below 0.70:** The system automatically goes back to research to find better sources. You do not need to do anything.

---

## Step 5 — Technical Analysis

An LLM reads the verified research and explains it at a senior engineer level:

- What this technology actually does
- Why it exists (what problem it solves)
- How data flows through it
- How it fits into the broader AI ecosystem
- How an engineer would build with it

This is the layer that turns raw search results into real understanding.

---

## Step 6 — Report Writing

The Report Writer takes everything from research, verification, and technical analysis, and fills in a structured report template. Every field must be filled — summary, architecture explanation, use cases, limitations, alternatives, future outlook, and full source list.

The report is validated against a Pydantic schema before it is accepted. If any required field is missing or malformed, the agent is asked to fix it.

---

## Step 7 — Report Approval (your second decision)

You read the report in the dashboard. It is displayed as formatted text with clickable source links — not raw JSON.

You can approve it as-is, or send it back with revision notes. If you send it back, the Report Writer reads your notes and tries again.

---

## Step 8 — POC Planning

The POC Planner designs a small, runnable project that demonstrates the topic.

It decides:
- Project name and goal
- What files are needed
- What Python packages to use
- What the README should say
- How to run it

It does not write code yet — it just makes a plan.

---

## Step 9 — Code Generation (with self-critique)

The Code Generator writes all the files from the plan.

Then — and this is the key part — it reads its own code and critiques it:

- Are there syntax errors?
- Are any imports missing?
- Are dependencies listed in requirements.txt?
- Are there hardcoded secrets?
- Does the README match the actual files?

If it finds errors, it fixes them. This loop runs up to twice before the code is handed to the external reviewer.

---

## Step 10 — Code Review

A separate Code Reviewer agent runs independent checks:

- Python syntax validation (`python -m py_compile`)
- Import and dependency check
- Secret pattern scan
- README accuracy check

If anything fails, the code goes back to the generator. If it passes, it moves to evaluation.

---

## Step 11 — Evaluation

The Evaluator scores the full output — report plus code — using a weighted rubric:

| What is scored | How much it counts |
|---|---|
| Research completeness | 20% |
| Technical accuracy | 25% |
| Source quality | 15% |
| Report clarity | 10% |
| POC usefulness | 10% |
| POC runnability | 10% |
| Security | 10% |

**Minimum to proceed:** 7.0 out of 10.

If the score is below 7.0, the run stops and is marked failed at evaluation.

If the score is between 7.0 and 8.0, the system suggests improvements and gives you the option to apply them.

---

## Step 12 — Improvement (optional)

If the evaluator found weak sections and you want to fix them, click **Apply Improvements**.

An Improvement Agent reads the evaluator's specific feedback and rewrites the weak sections. It does not touch the parts that scored well.

You can skip this and go straight to GitHub approval if you are happy with the report as-is.

---

## Step 13 — GitHub Push Approval (your final decision)

Before anything reaches GitHub, the system shows you:

- The final eval score
- All the files that will be pushed
- The folder path on GitHub

You click **Publish to GitHub** to proceed, or **Hold** to wait.

---

## Step 14 — GitHub Publishing

The GitHub Publisher runs these checks in order:

1. Human approval confirmed
2. Secret scan — scans all file contents for API keys, tokens, passwords
3. Required files present (README.md, requirements.txt, .env.example, app/, tests/)
4. Eval score passes minimum threshold
5. Push all files to the knowledge-base repo under `reports/{date}_{topic-slug}/`
6. Save the GitHub URL

If the secret scan finds anything suspicious, the push is blocked. Nothing reaches GitHub.

---

## Step 15 — Facebook Publishing (optional)

If you have configured the Facebook connector in Settings, a **Post to Facebook** button appears after the GitHub push.

Clicking it posts a summary of the report to your Facebook Page — title, one-liner, eval score, tags, and the GitHub link. The actual report content lives on GitHub; Facebook just gets an announcement post.

---

## What Gets Saved

After a successful run, the following are available in the dashboard:

- Full formatted report with clickable links
- Generated code files with syntax highlighting
- Verified source list with credibility scores
- Evaluation score breakdown
- Agent-by-agent log with token usage and cost
- GitHub folder URL
- Facebook post URL (if published)

All of this is also stored in Supabase if you have it configured.

---

## What Happens When Something Goes Wrong

If any agent fails — network error, LLM timeout, bad output — the error is logged and the run is marked failed.

You can click **Retry** in the run detail page. The system checks the last saved checkpoint and resumes from there. Agents that already completed successfully are not re-run.

For example: if the run failed during code review, retrying will pick up from code review. Discovery, research, report writing — all already done — are not repeated.
