# How Reports Are Scored

Every research report and code project is automatically scored before it can be published to GitHub. This page explains how the scoring works and what happens based on the result.

---

## Why Scoring Exists

The system generates reports and code automatically. Without a quality check, bad output could reach your GitHub knowledge base. The Evaluator Agent scores every output against a rubric so that only useful, accurate, and safe artifacts get published.

---

## The Scoring Rubric

The evaluator scores seven dimensions. Each has a weight that reflects how important it is:

| Dimension | Weight | What it measures |
|---|---|---|
| Technical accuracy | 25% | Are the claims correct? Are they backed by verified sources? |
| Research completeness | 20% | Does the report cover all the important angles of the topic? |
| Source quality | 15% | Are there at least five reliable sources? Are they primary sources? |
| Report clarity | 10% | Is the report readable and useful for an AI engineer? |
| POC usefulness | 10% | Does the demo project actually show the concept? |
| POC runnability | 10% | Is the code syntactically valid? Are dependencies listed? Are run instructions clear? |
| Security | 10% | No exposed secrets, no unsafe operations, no uncontrolled side effects? |

The overall score is calculated as: each dimension score (0–10) multiplied by its weight, summed together.

---

## Pass and Fail Thresholds

| Result | Score | What happens |
|---|---|---|
| Fail | Below 7.0 | Run stops. Cannot publish. Logged as failed at evaluation. |
| Pass with suggestions | 7.0 to 7.9 | Can publish, but the system offers to run the Improvement Agent first |
| Good | 8.0 and above | Can publish directly. No improvement needed. |

---

## The Improvement Option

If the score is between 7.0 and 8.0, the system shows an **Apply Improvements** button in the dashboard.

Clicking it runs the Improvement Agent, which:
- Reads the evaluator's specific feedback for each weak dimension
- Rewrites only the sections that scored poorly
- Leaves the well-scored sections unchanged

You can also skip improvements and go straight to GitHub approval if you think the report is good enough.

---

## What the Evaluator Actually Checks

Beyond the number scores, the evaluator produces a list of flags — specific things that are wrong or missing:

- Missing sections in the report
- Claims that are not backed by any source
- Sources that are not reliable enough (only Tier 3 / community signals)
- Code that references dependencies not in requirements.txt
- README that describes files that do not exist
- `.env.example` that contains real values instead of placeholders
- Any security-sensitive patterns in generated code

These flags appear in the Evaluation tab of the run detail page and in the `evaluation.md` file in the published GitHub folder.

---

## Running the Evaluator Manually

You can run evaluation on any saved output from the command line:

```bash
python evals/eval_runner.py generated_projects/2026-06-07_my-topic/report.json
```

---

## Regression Testing

The `evals/` folder contains golden test cases — known-good reports that should always score above the threshold. When you change any agent prompt, you can run:

```bash
python scripts/validate_generated_project.py generated_projects/2026-06-07_my-topic/
```

This checks that the output still meets the minimum quality bar.

---

## Viewing Scores in the Dashboard

In the run detail page, the **Evaluation** tab shows:

- Overall score with a pass/fail indicator
- Per-dimension breakdown
- All flags from the evaluator
- The evaluator's improvement suggestions

The score is also shown as a badge in the run list and in the meta strip at the top of the run detail page.
