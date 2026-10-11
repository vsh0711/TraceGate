# Runbook: how to do each milestone

Set up once:

```bash
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python litellm numpy scipy statsmodels pyyaml matplotlib pytest
ollama pull llama3.2:3b          # the agent model (local, free)
export GEMINI_API_KEY=...        # the judge model (free tier). Do not write the key in a file.
```

All commands run from the repository root with `PYTHONPATH=.` (the Makefile sets it).

| Milestone | Command | Output |
|---|---|---|
| Tests | `make test` | Reference solutions and statistics pass |
| M0 | `make eval` | Prints the success rate of one trial per task |
| M1 | `python -m evals.runner --version v0 --trials 4 --salt a --run-id v0-a` then the same with `--salt b --run-id v0-b` | Two identical runs |
| M1 | `python -m evals.grade v0-a --no-judge`, `python -m evals.noise v0-a v0-b` | `results/noise.md` (flip rate) |
| M2 | `python -m evals.grade v0-a`, `python -m evals.report v0-a` | `results/v0-a/report.md` with the per-grader breakdown |
| M3 | Same as M2 (the judge runs inside `evals.grade`) | Hallucination rates and examples in the report |
| M4 | `python -m evals.label sample`, `prefetch`, `annotate` (first pass); `python -m evals.label_review select`, `annotate`, `apply` (re-review); `python -m evals.judge_validation --split judge-dev`, then `--split judge-test` once; `python -m evals.judge_validation_doc` | `docs/judge-validation.md` |
| M5 | `python -m evals.triage offline --run v0-a`, `python -m evals.taxonomy v0-a` | `docs/failure-taxonomy.md` |
| M6 | See "One iteration" below | `CHANGELOG.md`, `docs/img/improvement.png` |
| M7 | `python -m online.simulate`, `python -m online.score --judge`, `python -m online.dashboard` | `online/dashboard.html` |

## One iteration (M6)

1. Run the candidate version on all tasks: `python -m evals.runner --version v1 --trials 4 --run-id v1`.
2. Grade and report: `python -m evals.grade v1`, `python -m evals.report v1`.
3. Compare to the baseline: `python -m evals.diff v0-a v1`.
4. Gate: `python -m evals.gate v0-a v1`. The exit code is 0 when the candidate passes.
5. Write a `CHANGELOG.md` entry with the changes, the metric changes and the dataset version.

## Rules you must keep

- Never read holdout traces to make a fix.
- Never edit `evals/holdout.lock` or the holdout tasks.
- Set the number of trials and the task set before you look at results.
