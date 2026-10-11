# Project status and how to resume

Last updated: 2026-10-11 (end of day 2). Read this file first when you resume.

## Done

| Milestone | State |
|---|---|
| M0 agent and 50 tasks (32 dev, 18 frozen holdout) | Done. Hash lock in `evals/holdout.lock`. `make eval` runs all tasks once (34.5% success). |
| M1 runner, logs, noise floor | Done. Flip rate 14.0% (`results/noise.md`). Harness h2 (`docs/harness.md`). |
| M2 layered graders | Done. Code, trajectory (9 policy rules), judge. |
| M3 hallucination detection | Done. Code checks on all runs. Judge `j4` on the holdout of v0, v1, v2, v3, v4 and v5. |
| M4 judge validation | Done, with a caveat. `docs/judge-validation.md`. The final labels are Claude's re-review of the owner's hand labels. |
| M5 failure taxonomy | Done. 137 offline and 35 online trials. Notes were written by Claude. |
| M6 learning loop | Done: v1, v3, v4, v5 rejected, **v2 promoted**. Dataset v2 (5 dev regression tasks, embedding dedup). Improvement chart. |
| M7 online evals | Done (`docs/online-evals.md`, `online/dashboard.html`). |
| README (TraceGate) with the chart, summary, sample scores, tests and validation | Done. |
| Evidence pack for presentation | Done: `docs/EVIDENCE.md`, rebuilt by `python -m evals.evidence`. |
| 2-minute video | **Pending. The owner records it.** Script: `docs/video-script.md`. |

## To do

1. **Record the video** (`docs/video-script.md`).
2. Recommended: a **second human labeler** for the judge validation. The owner's first-pass labels and the re-review disagree strongly (`docs/judge-validation.md`). A human decision on the rubric would settle which reading is right.
3. Optional: a human review of a sample of `labels/failure_notes.jsonl`. The stretch goals in the brief.

## Judge quota and keys

- The judge is `gemini/gemini-3.5-flash-lite`, prompt version `j4` (fixed). The free tier allows about 500 requests per day for each model **for each Google project**. A key from a new project has its own quota.
- Judge calls are cached on disk (`.cache/llm/`). Judging the holdout of one run costs about 100 requests.
- Keys are **not stored** in any file. Pass the key inline: `GEMINI_API_KEY=... PYTHONPATH=. .venv/bin/python ...`.
- Several keys were pasted in the chat. They are in the chat history. **Rotate them.**

## Rules to keep

- Never read holdout traces to make a fix. Never edit holdout tasks.
- The agent model is `ollama_chat/llama3.2:3b`. Keep the Mac awake for long runs (`caffeinate -i ...`). A 200-trial run takes about 45 to 60 minutes.
- Do not compare h1 results (`results/_archive_harness_h1/`) with h2 results.
- Gates use dataset v1 only (the 50 original tasks). The 5 dataset v2 tasks are a separate regression suite (`results/<version>-reg`).
- Write documents in short, plain sentences (`docs/STYLE.md`).
