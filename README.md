# TraceGate

**TraceGate measures a tool-using agent's accuracy and hallucinations, and makes the agent improve from its own failures, with a gate that keeps the numbers honest.**

![Holdout success, hallucination rate, cost and failure categories for each version](docs/img/improvement.png)

> I built a tool-using agent and the system that grades it: 50 tasks (plus 5 regression tasks), deterministic graders plus an LLM judge, trajectory-level scoring, and pass^k reliability. A failure → dataset → fix loop raised success on a frozen holdout from **34.7% to 50.0%** over **5 gated iterations** (1 promoted, 4 rejected), with no category regressing. **Judge agreement (prompt `j4`, held-out split, n = 73 trials): TPR 0.97, TNR 0.98, kappa = 0.94 against hand labels that were re-reviewed by Claude under the written rubric. Against my own first-pass hand labels the same judge agrees much less (kappa = 0.35). See [`docs/judge-validation.md`](docs/judge-validation.md).**

## Summary

TraceGate is an evaluation system for a customer-support agent that handles orders, refunds and address changes over a SQLite store, and that follows a written policy. The agent is a plain loop (model call, tool calls, tool results, repeat) on a small local model. **The agent is not the point. The eval system is the project.**

TraceGate does five things:

1. **It defines correctness with code.** Success means the final database change is right, the answer checks pass, and none of 9 policy rules is broken. The graders also score tool choice, arguments and efficiency on the whole trajectory, not only the final answer.
2. **It counts hallucinations.** It uses an operational definition: two deterministic checks (fabricated entities and fabricated actions) and one claim-level LLM judge.
3. **It does not fool itself.** It measures run-to-run noise (flip rate 14.0%), uses bootstrap intervals over tasks and paired tests, keeps a hash-locked holdout, and blocks leakage in code.
4. **It validates its judge** against labels, with TPR, TNR, kappa and bias checks, and it reports the judge's limits.
5. **It improves the agent from its own failures.** It reads failed trajectories, names the failure modes, fixes the biggest one first, adds regression tasks, and promotes a change only if it passes a gate. Four of five changes were rejected, and each is logged with its numbers.

**Evidence for every claim is in one file: [`docs/EVIDENCE.md`](docs/EVIDENCE.md)** (policy, tasks, tests, labels, judge validation, results, traces).

## What this project proves

- **It can define correctness** for a non-deterministic, multi-step system: final database state plus 9 policy rules, checked on every trajectory.
- **It builds graders that it can trust, with evidence:** reference solutions pass every grader (a test), and the judge is validated (kappa 0.94 per trial on held-out labels, with the label caveat below).
- **It does error analysis:** 137 failed trajectories read, 8 categories, and the biggest one (49 of 68 failed dev trials in one baseline run) fixed first.
- **It does not fool itself:** noise floor 14.0%, a leak guard, and judge bias checks (reordering changed 2 of 32 verdicts, padding 3 of 20).
- **It improves without breaking what worked:** the promoted change raised holdout success by +15.3 points (95% CI +4.2 to +27.8) and no category lost more than 10 points.

## Sample scores, tests and validation

**Scores (baseline against the promoted version):**

| Metric (holdout, 18 tasks x 4 trials) | v0 baseline | v2 guardrail |
|---|---|---|
| Success (95% CI, bootstrap over tasks) | 34.7% (15.3% to 56.9%) | 50.0% (30.6% to 69.4%) |
| pass^4 / pass@4 | 27.8% / 38.9% | 33.3% / 61.1% |
| Policy violation rate | 43.1% | 0.0% |
| Tool selection precision / recall | 89.3% / 74.3% | 88.1% / 81.1% |
| Fabricated entity / action rate (code checks) | 13.9% / 5.6% | 15.3% / 2.8% |
| Hallucination rate (judge `j4`) | 47.2% | 51.4% |
| Notional cost per success | $0.0163 | $0.0127 |

**Gate decisions** (rule: the gain must exceed the 14.0-point noise floor, be significant by a paired bootstrap, and no category may regress):

| Candidate | Dev change (95% CI) | Holdout change (95% CI) | Decision |
|---|---|---|---|
| v2 guardrail | +20.3 (+10.9 to +31.2) | +15.3 (+4.2 to +27.8) | **promoted** |
| v5 guardrail with remediation (8 trials per task, pooled) | +9.8 (+3.1 to +17.2) | +9.0 (+1.4 to +20.1) | rejected: significant, but below the noise floor |

**Judge validation** (tuned on a dev split; run once on a held-out split; acceptance rule: kappa 0.60 or more and TPR 0.80 or more):

| Judge-test, prompt `j4` | n | TPR | TNR | Cohen's kappa (final labels) | Kappa (owner's first-pass labels) |
|---|---|---|---|---|---|
| Hallucination, per trial | 73 | 0.97 | 0.98 | **0.94** | 0.35 |
| Hallucination, per claim | 168 | 0.91 | 0.98 | **0.90** | 0.27 |
| Refusal handling | 38 | 1.00 | 0.85 | **0.88** | 0.01 |

The bias checks pass: reversing the claim order changed 2 of 32 verdicts, and padding the answer changed 3 of 20. **Caveat:** the "final labels" are a re-review by Claude of the owner's first-pass labels, because the first pass disagreed with the written rubric. The brief asks for labels that you make yourself. Both sets are kept and reported.

**Tests:** `make test` → **29 passed in 2.29s**. They cover the task set and the frozen holdout, a check that every reference solution passes every grader, the guardrail rules, the agent loop with a fake model, the reactive scripted user, the statistics (pass^k, bootstrap, paired tests, flip rate), the answer validator, and two grader regressions. `make eval` runs all tasks once and prints the success rate (34.5% for the baseline, one trial per task).

### Screenshots of the labeling and judging scripts

These four images are terminal-style renders of the **real output** of the scripts. The script text is not edited. They are not screen captures. The labeling prompts wait for input, so no typed answer is shown.

**1. Hand-labeling tool (first pass).** `python -m evals.label annotate` shows one trial: the customer request, the tool calls with their results (the evidence), and the agent's final answer. Then it asks for one label for each atomic claim: `s` supported, `c` contradicted, `u` unsupported. The first claim here is "Order O1001 was delivered 26 days ago", and the evidence shows an 11-day-old delivery.

![Hand-labeling tool](docs/img/screenshots/01-human-labeling.png)

**2. Blind re-review tool (second pass).** `python -m evals.label_review annotate` shows the same kind of screen for the 65 trials that were selected for a second look. It does not show the judge's answer or the earlier label. It prints the rubric reminders (invented details are `u`, an action claim needs a successful tool call) and the three-part refusal rule. Trial 1 has no claims because the final answer is a broken tool call, so only the refusal question is asked.

![Blind re-review tool](docs/img/screenshots/02-human-rereview.png)

**3. Judge validation run.** `python -m evals.judge_validation --split judge-test` compares the judge (prompt `j4`, model `gemini-3.5-flash-lite`) with the final labels on the 73 held-out trials. It prints the confusion counts (TP, FN, TN, FP), TPR, TNR and Cohen's kappa at claim level (kappa 0.90), trial level (0.94) and refusal level (0.88), and the bias counts: the verdict stayed the same for 30 of 32 claims when their order was reversed, and for 17 of 20 answers after padding.

![Judge validation run](docs/img/screenshots/03-judge-validation-run.png)

**4. Claim-level hallucination judge on one trial.** For one baseline holdout trial, the judge splits the final answer into 3 atomic claims, labels each one against the evidence (1 supported, 2 unsupported), and gives a short reason. The trial counts as a hallucination trial because at least one claim is unsupported.

![Claim-level hallucination judge](docs/img/screenshots/04-judge-claim-labels.png)

This repository follows the brief `BRIEF.md` (project 02, option A).

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

Done: M0 to M7, the report files, the changelog and the improvement chart. **Pending: the 2-minute video** (a failing trace, its taxonomy label, the fix, and the gate passing), which the project owner records. Recommended: a second human labeler for the judge validation.

## Style of the documents

Documents use short, plain sentences, inspired by ASD-STE100 ([`docs/STYLE.md`](docs/STYLE.md), [`docs/glossary.md`](docs/glossary.md)).
