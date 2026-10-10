# Project status and how to resume

Last updated: 2026-10-10 (end of day 1). Read this file first when you resume.

## Done

| Milestone | State |
|---|---|
| M0 agent and 50 tasks (32 dev, 18 frozen holdout) | Done. Holdout hash lock in `evals/holdout.lock`. |
| M1 runner, logs, noise floor | Done. Flip rate 14.0% (`results/noise.md`). Harness h2 (`docs/harness.md`). |
| M2 layered graders | Done. Code, trajectory (9 policy rules), judge. |
| M3 hallucination detection | Code checks done on all runs. Judge done on the **holdout** for v0-a and v2 only (quota). |
| M4 judge validation | **Not done.** Needs your hand labels. Queue ready (150 trials, claims pre-extracted). |
| M5 failure taxonomy | Done. `docs/failure-taxonomy.md` (137 trials, written by Claude, not a human). |
| M6 learning loop | v1 rejected, v2 PROMOTED, v3 rejected (`CHANGELOG.md`). v4 is built but not run. |
| M7 online evals | Done (`docs/online-evals.md`, `online/dashboard.html`). |

Headline so far: holdout success 34.7% to 50.0% (v0 to v2, gate passed). Judged hallucination on the holdout went up (44.4% to 52.8%). That is why v4 exists.

## To do next (in this order)

1. **v4 (answer validator).** Run `PYTHONPATH=. .venv/bin/python -m evals.runner --version v4 --trials 4 --salt a --run-id v4 --workers 2` (about 45 minutes). Then `python -m evals.grade v4 --no-judge`, `python -m evals.report v4`, `python -m evals.diff v2 v4`, `python -m evals.gate v2 v4`. Add a `CHANGELOG.md` entry whatever the result.
2. **Judge the holdout** of v1, v3 and v4 (`grade_run(run, True, workers=2, judge_split="holdout")`, see "Judge quota" below). The chart needs the judged hallucination rate for every version.
3. **Chart and README.** `python -m evals.chart v0=v0-a v1=v1 v2=v2 v3=v3 v4=v4 --out docs/img/improvement.png`. Then write `README.md` with the chart on top, and the one-sentence claim from the brief with real numbers.
4. **M4 (you).** `python -m evals.label annotate` (resume at any time). Then `python -m evals.judge_validation` for `judge-dev`, then `judge-test`. Then write `docs/judge-validation.md` (agreement table, confusion matrix, bias checks). The README must state TPR, TNR, kappa and n.
5. **Video.** You record it. The script is `docs/video-script.md`.
6. Optional: ask a human to review a sample of `labels/failure_notes.jsonl`. Judge the online traces on a sample. Stretch goals in the brief.

## Judge quota and keys

- The judge is `gemini/gemini-3.5-flash-lite` (fixed). The free tier allows about 500 requests per day for each model. Quota is per Google project, so a second key from the same project does not help.
- Judge calls are cached on disk (`.cache/llm/`). A repeated call costs nothing. Judging the holdout of one run costs about 150 requests.
- Keys are **not stored** in any file. Pass the key inline: `GEMINI_API_KEY=... PYTHONPATH=. .venv/bin/python ...`. You must give it again tomorrow.
- Both keys that were pasted in the chat are in the chat history. Rotate them when the project is done.

## Rules to keep

- Never read holdout traces to make a fix. Never edit holdout tasks.
- The agent model is `ollama_chat/llama3.2:3b`. Keep the Mac awake for long runs (`caffeinate -i ...`). A run takes about 45 minutes.
- Do not compare h1 results (`results/_archive_harness_h1/`) with h2 results.
- Write documents in short, plain sentences (`docs/STYLE.md`).
