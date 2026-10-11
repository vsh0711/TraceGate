# Judge validation (M4)

The judge is an LLM that labels each claim of a final answer as `supported`, `contradicted` or `unsupported`, and that grades how a refusal was handled (`docs/judge-rubric.md`). This document compares the judge with hand labels.

## Result in one paragraph

**Hallucination judge (prompt `j4`, model `gemini/gemini-3.5-flash-lite`): TPR 0.97, TNR 0.98, kappa = 0.94 on n = 73 held-out labeled trials (judge-test, trial level).** At claim level: TPR 0.91, TNR 0.98, kappa = 0.90 on n = 168 claims. For refusal handling: TPR 1.00, TNR 0.85, kappa = 0.88 on n = 38.

**Read this first: who made the labels.** The 150 trials were first labeled by hand by the project owner (the first pass). The project owner's labels disagreed with the written rubric in many places, for example on invented details such as "3-5 business days", and on refusal tasks where the agent did the forbidden action. At the owner's request, **Claude re-reviewed all 150 trials** under the same written rubric. The **final labels are Claude's re-review**. The owner's first-pass labels are kept (`labels/human_labels.jsonl`). So this validation compares the judge with Claude's labels. It is **not** a validation against the owner's own first-pass labels. Against those, the judge agrees much less (see the table below). The brief asks for labels that you make yourself. This is a known deviation, and it is the main limit of this document.

## Method

1. 150 trials were sampled from the **dev split** only (`python -m evals.label sample`). The holdout was never labeled and never used to tune the judge.
2. The trials are split by task into `judge-dev` (77 trials, 18 tasks, for tuning the judge prompt) and `judge-test` (73 trials, 14 tasks, for reporting). No task is in both.
3. The labels cover every claim of the final answer and, for tasks that the policy does not allow, the handling of the refusal. The judge gets the same claims and the same evidence.
4. We report the true positive rate (TPR: the judge flags a real failure), the true negative rate (TNR: the judge does not flag a good output) and Cohen's kappa. The positive class is a failure.
5. judge-test was run with the final prompt only after tuning on judge-dev was finished. The first judge-test run was stopped by the free API quota and was resumed with the same prompt and the same labels. No prompt change was made between the two parts.

## Label sets

| Set | Made by | Used for |
|---|---|---|
| First-pass labels | The project owner (hand) | Kept as the record. Reported next to the final result. |
| Final labels | Claude re-reviewed all 150 trials under the written rubric (`labels/human_labels_review_claude.jsonl`, merged in `labels/human_labels_final.jsonl`) | The validation result above |

How much the two label sets differ (the owner's first pass against the re-review):

| Split | Level | n | Agreement kappa | Raw agreement |
|---|---|---|---|---|
| judge-dev | claim | 159 | 0.12 | 67% |
| judge-dev | trial | 77 | 0.10 | 57% |
| judge-dev | refusal | 40 | 0.06 | 35% |
| judge-test | claim | 168 | 0.26 | 75% |
| judge-test | trial | 73 | 0.29 | 68% |
| judge-test | refusal | 38 | 0.03 | 39% |

In the final labels, judge-test has 168 claims (47 unsupported or contradicted), 30 hallucination trials out of 73, and 25 failed refusals out of 38. Judge-dev has 159 claims (53 bad), 36 hallucination trials out of 77, and 29 failed refusals out of 40.

## Result on judge-test (the reporting split)

| Compared with | Level | n | TPR | TNR | Cohen's kappa |
|---|---|---|---|---|---|
| Final labels (re-review) | claim | 168 | 0.91 | 0.98 | 0.90 |
| Final labels (re-review) | trial (hallucination) | 73 | 0.97 | 0.98 | 0.94 |
| Final labels (re-review) | refusal handling | 38 | 1.00 | 0.85 | 0.88 |
| First-pass labels (owner) | claim | 168 | 0.61 | 0.78 | 0.27 |
| First-pass labels (owner) | trial (hallucination) | 73 | 0.85 | 0.68 | 0.35 |
| First-pass labels (owner) | refusal handling | 38 | 0.75 | 0.29 | 0.01 |

**Claim level, final labels** (positive = a failure)

| | Judge: failure | Judge: ok |
|---|---|---|
| **Label: failure** | 43 | 4 |
| **Label: ok** | 3 | 118 |

**Trial level, final labels** (positive = a failure)

| | Judge: failure | Judge: ok |
|---|---|---|
| **Label: failure** | 29 | 1 |
| **Label: ok** | 1 | 42 |

**Refusal handling, final labels** (positive = a failure)

| | Judge: failure | Judge: ok |
|---|---|---|
| **Label: failure** | 25 | 0 |
| **Label: ok** | 2 | 11 |

## Result on judge-dev (the tuning split, optimistic)

| Compared with | Level | n | TPR | TNR | Cohen's kappa |
|---|---|---|---|---|---|
| Final labels (re-review) | claim | 159 | 0.89 | 0.93 | 0.82 |
| Final labels (re-review) | trial (hallucination) | 77 | 0.89 | 0.85 | 0.74 |
| Final labels (re-review) | refusal handling | 40 | 0.93 | 0.82 | 0.75 |
| First-pass labels (owner) | claim | 159 | 0.58 | 0.69 | 0.15 |
| First-pass labels (owner) | trial (hallucination) | 77 | 0.73 | 0.55 | 0.13 |
| First-pass labels (owner) | refusal handling | 40 | 0.67 | 0.27 | -0.01 |

The dev numbers are higher than a fair estimate: the prompt was tuned on this split, and Claude had seen the judge's answers on many dev trials when it re-reviewed them. Use the judge-test numbers.

## How the judge prompt was tuned (judge-dev only)

Kappa values on judge-dev. The label set changed during the work, so each row says which labels it used.

| Prompt | Labels used | Claim kappa | Trial kappa | Refusal kappa | What changed |
|---|---|---|---|---|---|
| j1 | First-pass | 0.07 | 0.13 | 0.07 | First version |
| j2 | First-pass | 0.16 | 0.17 | 0.07 | Rules for placed_at against delivered_at, day counts, "not found" errors, blocked calls, matching order ids |
| j2 | 65 of 150 trials re-reviewed (selected), the rest first-pass | 0.75 | 0.82 | 0.57 | Same prompt. Shows how much the labels, not the judge, limited agreement |
| j2 | All 150 re-reviewed | 0.68 | 0.71 | 0.21 | Same prompt, final labels |
| j3 | Final | 0.82 | 0.74 | 0.41 | Rules for "full refund", for errors that the agent caused with its own arguments, for allowed and forbidden actions, for claims about the final message, and a computed days-since-delivery helper in the evidence. A sharper refusal rubric |
| **j4 (final)** | Final | 0.82 | 0.74 | 0.75 | The refusal judge is told that the task cannot be carried out as asked, and that not doing the action is not enough |

j1 and j2 numbers on the first-pass labels were recorded when they ran (the result files of those runs were later overwritten by runs with the final labels).

## Bias checks

Both checks use the final prompt.

- **Position bias.** We reversed the order of the claims and labeled them again. On judge-test the verdict stayed the same for 30 of 32 claims (94%). On judge-dev it stayed the same for 30 of 31 (97%).
- **Verbosity bias.** We added a long, polite and fact-free sentence to the end of the answer and judged again. On judge-test the trial verdict stayed the same for 17 of 20 answers (85%). On judge-dev it stayed the same for 17 of 20 (85%).
- **Self-preference.** The agent is a Llama model, the judge is a Gemini model, and the final labels were made by Claude. No two of them are the same model.

## What "acceptable" means

We accept the judge when kappa is 0.60 or more and TPR is 0.80 or more on `judge-test`. Kappa of 0.60 is the usual lower limit for substantial agreement. TPR of 0.80 means that the judge catches at least 8 of 10 real failures. We prefer a judge that flags too much to a judge that misses failures, because hallucination is a safety metric.

**Verdict.** Against the final labels, the judge meets both limits at all three levels on judge-test. Against the owner's first-pass labels, it does not (kappa 0.27, 0.35 and 0.01). The two label sets disagree with each other, so the judge cannot agree with both. The honest statement is: the judge applies the written rubric consistently and agrees with a strict reading of that rubric. It does not agree with the owner's more lenient first-pass reading.

## Limits

- **The final labels are not purely human.** They are Claude's re-review. The brief asks for labels that you make yourself. A second human labeler is the fix.
- **The judge and the final labels both apply the same strict rubric.** Their agreement is partly agreement on a shared reading, not proof that the reading is the right one.
- **The owner's labels and the re-review disagree** (kappa 0.10 to 0.29 on claims and trials, 0.03 to 0.06 on refusals). We could not measure a stable human standard. This is itself a finding: the rubric needed worked examples (they were added to `docs/judge-rubric.md` after the first pass).
- **Dev labels are not blind to the judge.** For many judge-dev trials, Claude saw the judge's answers before it re-reviewed them. Judge-test labels were made without any judge output.
- **Small samples.** Judge-test has 73 trials, 168 claims and 38 refusal items. Read every rate with its sample size. One trial moves a rate by one or two points.
- **One judge model.** `gemini/gemini-3.5-flash-lite`. We did not compare judges or run a panel.
- **Earlier hallucination numbers.** The hallucination rates that were reported before this validation used prompt `j1`, which was not validated. The reports and the chart were made again with `j4` (see `CHANGELOG.md`).
