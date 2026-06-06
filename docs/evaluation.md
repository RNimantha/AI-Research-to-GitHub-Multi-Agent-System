# Evaluation System

## Rubric

See `evals/rubric.json` for the full rubric.

| Dimension              | Weight | Min passing |
|------------------------|--------|-------------|
| research_completeness  | 20%    | —           |
| technical_accuracy     | 25%    | —           |
| source_quality         | 15%    | —           |
| report_clarity         | 10%    | —           |
| poc_usefulness         | 10%    | —           |
| poc_runnability        | 10%    | —           |
| security               | 10%    | 5.0 (hard)  |

**Overall minimum**: 7.0/10 to proceed to GitHub publishing.
**Security rule**: security score < 5.0 = automatic fail.

## Running Evaluations

```bash
python evals/eval_runner.py generated_projects/2026-06-06_my-topic/report.json
```

## Regression Testing

Run `evals/regression_cases.json` checks against any generated folder using `validate_generated_project.py`.
