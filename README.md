# Agent evals: measure an agent's accuracy and hallucinations, and make it improve

![Holdout success, hallucination rate, cost and failure categories for each version](docs/img/improvement.png)

> I built a tool-using agent and the system that grades it: 50 tasks (plus 5 regression tasks), deterministic graders plus an LLM judge, trajectory-level scoring, and pass^k reliability. A failure → dataset → fix loop raised success on a frozen holdout from **34.7% to 50.0%** over **5 gated iterations** (1 promoted, 4 rejected), with no category regressing. **Judge agreement (prompt `j4`, held-out split, n = 73 trials): TPR 0.97, TNR 0.98, kappa = 0.94 against hand labels that were re-reviewed by Claude under the written rubric. Against my own first-pass hand labels the same judge agrees much less (kappa = 0.35). See [`docs/judge-validation.md`](docs/judge-validation.md).**

This repository follows the brief `BRIEF.md` (project 02, option A). The agent is not the point. The eval system is the project.

## The agent

A customer support agent for a small online store. It handles orders, refunds and address changes over a SQLite database, and it follows a written policy (`agent/policy.md`). It has 7 tools. It is a plain loop: model call, tool calls, tool results, repeat, with a limit of 15 model calls. The model is a small local model (`llama3.2:3b` through Ollama). We chose a weak model on purpose: it fails often enough to give failures to study.

## Results

Frozen holdout: 18 tasks, 4 trials for each task (72 trials). The noise floor is **14.0%**: two identical runs disagree on 14.0% of (task, trial) outcomes. A gain smaller than that is called noise.

| Version | What changed | Holdout success (95% CI) | pass^4 | Hallucination rate (judge `j4`) | Notional cost per success | Gate |
|---|---|---|---|---|---|---|
| v0 | Baseline | 34.7% (15.3 to 56.9) | 27.8% | 47.2% | $0.0163 | n/a |
| v1 | Richer tool descriptions | 34.7% (16.7 to 55.6) | 27.8% | 45.8% | $0.0194 | rejected |
| **v2** | **Guardrail: a validator blocks policy-breaking tool calls** | **50.0%** (30.6 to 69.4) | 33.3% | 51.4% | $0.0127 | **promoted** |
| v3 | Exemplar memory | 52.8% (31.9 to 73.6) | 44.4% | 68.1% | $0.0174 | rejected |
| v4 | Answer validator | 51.4% (30.6 to 72.2) | 38.9% | 45.8% | $0.0130 | rejected |
| v5 | Guardrail that reads the order for the agent | 63.9% (44.4 to 81.9) | 44.4% | 36.1% | $0.0104 | rejected (gain below the noise floor) |

- **The promoted change is v2.** On the holdout, success rose by 15.3 points (paired bootstrap 95% CI +4.2 to +27.8). On dev, it rose by 20.3 points (CI +10.9 to +31.2). The policy violation rate on the holdout fell from 43.1% to 0.0%. No category regressed by more than 10 points.
- **v5 is a real but modest gain.** Two independent runs of both versions (8 trials for each task) give +9.5 points (CI +4.3 to +15.7). That is below the 14.0-point noise floor, so the gate rejects it. It is also a scaffold: the system reads the order for the agent.
- **Hallucination did not fall with success.** After v2, the judged hallucination rate on the holdout went from 47.2% to 51.4% (not a significant change). The guardrail makes the agent safe. It does not make the agent more truthful. v5 has the lowest rate (36.1%, a significant fall against v2, but hallucination was not its declared target, so this is a hint). v3 is the worst (68.1%).
- **Four of five iterations failed the gate.** Every one is logged with its numbers and what we learned in [`CHANGELOG.md`](CHANGELOG.md).

## Failure analysis

We read 137 failed dev trajectories and grouped them by their **first wrong step** ([`docs/failure-taxonomy.md`](docs/failure-taxonomy.md)). The biggest category in the baseline is `skipped_order_lookup` (77%): the agent changes an order that it has not read. That is the failure that v2 removes. The taxonomy also covers 35 flagged online traces.

## Online evals

A simulated user made 90 conversations in 9 batches. A guardrail-off deploy raised the policy violation rate from 0% to 70% to 90% and fired the alerts. A degraded tool description changed nothing, because the agent hardly reads tool descriptions. See [`docs/online-evals.md`](docs/online-evals.md).

## How the project meets the brief

| Milestone | Where |
|---|---|
| M0 agent and 50 tasks, frozen holdout | `agent/`, `env/`, `evals/tasks.jsonl`, `evals/holdout.lock`; `make eval` |
| M1 runner, trajectory logs, flip rate | `evals/runner.py`, `results/<run>/trajectories.jsonl`, `results/noise.md` |
| M2 layered graders | `evals/graders/` ([`docs/policy-rules.md`](docs/policy-rules.md)) |
| M3 hallucination detection | [`docs/hallucination.md`](docs/hallucination.md), `evals/graders/hallucination.py`, `evals/graders/judge.py` |
| M4 judge validation | [`docs/judge-validation.md`](docs/judge-validation.md), `evals/label.py`, `evals/label_review.py`, `evals/judge_validation.py` |
| M5 failure taxonomy | [`docs/failure-taxonomy.md`](docs/failure-taxonomy.md) |
| M6 learning loop | [`CHANGELOG.md`](CHANGELOG.md), [`docs/gate.md`](docs/gate.md), `evals/gate.py`, `evals/grow.py` |
| M7 online evals | [`docs/online-evals.md`](docs/online-evals.md), `online/` |
| Run reports and diffs | `results/<run>/report.md`, `results/diff_*.md` |
| Statistics | `stats/metrics.py` (pass^k, bootstrap over tasks, McNemar, flip rate) |

## Run it

```bash
uv venv --python 3.12 .venv
uv pip install -p .venv/bin/python litellm numpy scipy statsmodels pyyaml matplotlib pytest
ollama pull llama3.2:3b
export GEMINI_API_KEY=...         # the LLM judge. Do not write the key in a file.
make test                         # unit tests
make eval                         # run all tasks once and print the success rate
PYTHONPATH=. .venv/bin/python -m evals.runner --version v2 --trials 4 --run-id v2
PYTHONPATH=. .venv/bin/python -m evals.grade v2 && PYTHONPATH=. .venv/bin/python -m evals.report v2
PYTHONPATH=. .venv/bin/python -m evals.diff v0-a v2 && PYTHONPATH=. .venv/bin/python -m evals.gate v0-a v2
```

More commands are in [`docs/runbook.md`](docs/runbook.md).

## Rules that keep the numbers honest

- **Leakage.** Nothing from the holdout is used to make a fix. The code enforces it: a hash lock on the holdout tasks, and `require_dev()` in error analysis, labeling and exemplar memory.
- **Noise.** A change smaller than the flip rate (14.0%) is called noise. Gates use paired tests.
- **Fixed set.** The task set and the number of trials were fixed before results were read. Dataset v2 added 5 dev tasks after the loop found new failure modes. Gates use dataset v1 only.
- **The harness is part of the measurement.** The first baseline had an unrealistic scripted user. We found it in the error analysis, fixed it, and measured again (`docs/harness.md`).

## Limits and known issues

- The holdout has 18 tasks. Its confidence intervals are wide (about ±20 points).
- The agent model is small. Results may differ for a stronger model.
- **The judge labels are not purely human.** The final labels in the judge validation are a re-review by Claude of my first-pass hand labels. My first-pass labels disagreed with the written rubric (for example on invented refund timelines). The judge agrees well with the re-review and poorly with my first pass. A second human labeler would settle which reading is right. See [`docs/judge-validation.md`](docs/judge-validation.md).
- The failure notes were written by Claude, not by a human reviewer. A human should review a sample.
- Two graders had bugs that were found after results were known (`CHANGELOG.md`, g2 and g3). All runs were graded again. The gate decisions did not change.
- The scripted user stops when the agent ends a turn with a statement. An agent that narrates and stops fails the task. We count this as a real failure.
- Costs are notional. The local model has no real cost.

## Status

Done: M0 to M7, the report files, the changelog and the improvement chart. **Pending: the 2-minute video** (script in [`docs/video-script.md`](docs/video-script.md)), which the project owner records. Recommended: a second human labeler for the judge validation. See [`docs/STATUS.md`](docs/STATUS.md).

## Style of the documents

Documents use short, plain sentences, inspired by ASD-STE100 ([`docs/STYLE.md`](docs/STYLE.md), [`docs/glossary.md`](docs/glossary.md)).
