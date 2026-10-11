# Changelog

One entry for each change to the harness or the agent. Each entry states what changed, the metric changes, the dataset version and the gate decision.

Dataset version for all entries below: **v1** (50 tasks: 32 dev, 18 holdout). Metrics use 4 trials per task. The baseline is run `v0-a`. The noise floor (flip rate of `v0-a` against `v0-b`) is 14.0%. Success is the share of trials where the state, answer and policy graders all pass. "Notional cost" uses the fixed prices in `config.py`.

## harness h2 (before any iteration)

- **What changed:** the scripted user now reacts to the agent (`agent/user.py`). It answers a question with the next scripted reply, and it does not repeat "yes" after the agent states that the job is done. See `docs/harness.md`.
- **Why:** the first baseline (harness h1) sent "Yes, please go ahead." twice in single-write tasks. About one third of the failed trials contained a repeated write that the extra "yes" provoked.
- **Metric change:** none to compare. The baseline was measured again. h1: 43.5% and 44.0% success. h2: 42.5% (`v0-a`) and 44.5% (`v0-b`).
- **Tasks, split, holdout hash, graders, model, temperature:** unchanged.
- **Gate:** not applicable. This change fixes the instrument. It was made before any version was compared.

## grader fix g2 (after v3, before the final numbers)

- **What changed:** two fixes in the graders. (1) Rule `P1_verify_first` counted a tool call that the guardrail **blocked**. A blocked call did not run, so it is not a violation. This is what `docs/policy-rules.md` already said. The code now matches the document. (2) The fabricated-entity check treated an empty argument (`email: ""`) as an invented value. An empty value is a missing value, so the check now skips it.
- **How it was found:** the online traces (M7). The healthy online batches showed 30% to 40% policy violations, which made no sense for a guarded agent.
- **Effect:** only guarded runs change (v2, v3). The unguarded runs (v0, v1) are unchanged. All five runs were graded again, and the reports, diffs and gates were made again. Tests: `tests/test_graders.py`.
- **Honest note:** the fix raises the success of the guarded versions, which favors the guardrail. It was found after the results were known. The gate decisions did not change (v1 reject, v2 promote, v3 reject). The numbers in the v2 and v3 entries below are the corrected ones. The holdout success values did not change.
- **Noise floor:** unchanged at 14.0%.

## grader fix g3 (found by the new regression tasks)

- **What changed:** the email pattern of the fabricated-entity check kept a trailing full stop ("name@example.com."), so a correctly used email looked invented. The check now removes the trailing full stop.
- **Effect:** only fabricated-entity rates change. They fall by 2 to 5 trials per run (for example v0-a 27 to 23 trials). Success, the gates and the noise floor do not change. Test: `tests/test_tasks.py` (reference solution of task T053).
- **Note:** this fix can only remove false alarms. It was found by the reference-solution test, not by looking at a result.

## dataset v2 (M6 step 3: grow the dataset)

- **What changed:** 5 regression tasks (T051 to T055) were added to the **dev** split. Each one covers a failure mode that the 50 first tasks did not test: the customer gives no identity at first, a mistyped email followed by a correction, an invented refund timeline, a policy question, and a false premise ("thank you for cancelling"). The failure modes come from the dev failures and from the triage of the online review queue (`evals/new_tasks_v2.json`, field `source_failure`). Code: `evals/grow.py`.
- **Deduplication by embedding similarity:** each candidate was compared with all existing tasks. The text compared is the whole scripted conversation (the first message and all replies), because the new failure mode is often in the later turns. Embedding model: `gemini-embedding-001`. Threshold: cosine similarity 0.95. **1 of 6 candidates was dropped**: "I want to cancel my order O1002" with the identity given later is 0.976 similar to task T006. The failure mode "no identity at first" stays covered by T051. The closest remaining task is at 0.874 to 0.945. Check: `python -m evals.grow --check`.
- **A first attempt compared only the first message.** That flagged 2 tasks that differ in later turns, so the check was changed to use the whole script before the final dataset was built. This is a change of the check, made after seeing its result. The threshold (0.95) was fixed before the first check.
- **Dataset size:** 55 tasks: 37 dev and 18 holdout. The holdout is unchanged: the hash lock still verifies.
- **Why a separate run:** versions v0 to v3 were measured on dataset v1. To keep every comparison paired and fair, the new tasks are run as a separate regression suite for each version (`--only-dataset-version v2`). Gate decisions use dataset v1 only.

## v1: richer tool descriptions (REJECTED)

- **Target:** `skipped_order_lookup`, the largest failure category (105 of 137 failed dev trials, 77%, in the baseline).
- **What changed:** each tool description now states when to use it and what to call first (for example "ALWAYS call get_order before cancel_order"). Code: `agent/tool_specs.py`, set `RICH`.
- **Leakage check:** the change came from reading failed dev trials only.
- **Results (run `v1`, all trials):**

| Metric | v0-a | v1 | Change |
|---|---|---|---|
| Success, dev | 46.9% | 45.3% | -1.6 pts (95% CI -9.4 to +7.0) |
| Success, holdout | 34.7% | 34.7% | 0.0 pts (95% CI -4.2 to +4.2) |
| Failed dev trials in `skipped_order_lookup` | 49 | 53 | +4 |
| Failed dev trials in `skipped_identity_check` | 7 | 0 | -7 |
| Dev success in `address` | 33.3% | 16.7% | -16.7 pts |

- **Gate: FAIL** (`results/gate_v0-a_vs_v1.json`). The dev gain is not above the noise floor (14.0%). The dev gain is not significant. The holdout gain is not above the noise floor. The `address` category lost more than 10 points on dev.
- **What we learned:** the descriptions removed the identity-check failures, but the model still writes before it reads the order. A 3B model does not follow "call get_order first" in a tool description. The next fix must not depend on the model's compliance.
- **Decision:** v1 is not promoted. Its changes are not part of v2.

## v2: guardrail (validator before each tool call) (PROMOTED)

- **Target:** `skipped_order_lookup` (77% of baseline failures) and `skipped_identity_check` (11%). v1 showed that the model does not follow instructions in tool descriptions. This fix does not depend on the model's compliance.
- **What changed:** `agent/guard.py` checks every tool call before it runs. It blocks an order tool before identity is verified, a write before `get_order` for that order, a write on another customer's order, a cancel or address change on an order that is not `processing`, and a refund that the policy forbids. A blocked call does not run. The agent gets an error that says what to do first (`BLOCKED_BY_POLICY: ...`) and can try again. Tool descriptions stay as in v0.
- **Leakage check:** the design came from reading failed dev trials only. No holdout trace was read.
- **Results (run `v2` against `v0-a`):**

| Metric | v0-a | v2 | Change |
|---|---|---|---|
| Success, dev | 46.9% | 67.2% | +20.3 pts (paired bootstrap 95% CI +10.9 to +31.2) |
| Success, holdout | 34.7% | 50.0% | +15.3 pts (95% CI +4.2 to +27.8) |
| pass^4, all tasks | 32.0% | 44.0% | +12.0 pts |
| Policy violation rate, holdout | 43.1% | 0.0% | -43.1 pts |
| Dev success, `refund` | 46.4% | 78.6% | +32.1 pts |
| Dev success, `address` | 33.3% | 83.3% | +50.0 pts |
| Dev success, `lookup`, `multi` | 41.7%, 25.0% | 41.7%, 25.0% | 0.0 pts |
| Failed dev trials | 68 | 42 | -26 |
| Notional cost per success, holdout | $0.0163 | $0.0127 | -22% |

- **Gate: PASS** (`results/gate_v0-a_vs_v2.json`). Dev gain 20.3 pts is above the 14.0-point noise floor and significant. Holdout gain 15.3 pts is above the noise floor. No category regresses by more than 10 points.
- **Limits:** the guard blocks 0.82 calls per trial. The guard makes the system safe, but the model still guesses. `fabricated_entity_rate` did not fall (15.3% on holdout, against 13.9% for v0; both after grader fix g3). The `lookup` and `multi` categories did not improve, because their failures are stalls, not policy errors.
- **Dataset version:** v1.

## v3: exemplar memory (REJECTED)

- **Target:** the stalls and skipped steps that remained after v2 (`gave_up_early`, `skipped_identity_check`).
- **What changed:** the system prompt gets the 2 most similar clean successful dev trajectories as few-shot examples (`agent/memory.py`, `agent/exemplars.json`). The memory holds 9 trajectories from dev tasks of runs `v0-a`, `v0-b`, `v1` and `v2`. A clean trajectory has the reference tool sequence, no guard block, no tool error, no fabrication, and no order facts stated before the order was read. A dev task never retrieves its own trajectory.
- **Leakage check:** the leak guard (`require_dev`) stops the build if a holdout task is present. The memory has no holdout task.
- **Results (run `v3` against `v2`):**

| Metric | v2 | v3 | Change |
|---|---|---|---|
| Success, dev | 67.2% | 64.8% | -2.3 pts (95% CI -14.1 to +8.6) |
| Success, holdout | 50.0% | 52.8% | +2.8 pts (95% CI -9.7 to +15.3) |
| pass^4, holdout | 33.3% | 44.4% | +11.1 pts |
| Dev success, `lookup` | 41.7% | 8.3% | -33.3 pts |
| Dev success, `address` | 83.3% | 58.3% | -25.0 pts |
| Failed dev trials, `skipped_identity_check` | 2 | 8 | +6 |
| Failed dev trials, `gave_up_early` | 5 | 9 | +4 |
| Failed dev trials, `policy_violation` (a blocked attempt counts) | 0 | 3 | +3 |
| Notional cost per success, holdout | $0.0127 | $0.0174 | +37% |

- **Gate: FAIL** (`results/gate_v2_vs_v3.json`). The dev result fell. The holdout gain is below the noise floor (14.0%). `lookup` lost more than 10 points on both splits and `address` lost 25 points on dev.
- **What we learned:** the examples are the weak model's own successes, and they still contain its bad habits. They show the agent narrating and asking for confirmation before a read-only step. The model copied this, and the h2 user ends the conversation after a statement. Memory built from a weak model's own trajectories spreads its mistakes. Better memory needs curated or reference-based demonstrations.
- **Decision:** v3 is not promoted. v2 stays the live version.

## v4: answer validator (REJECTED)

- **Target (declared before the run):** the judged hallucination rate on the holdout. After v2, success rose, but the judged hallucination rate on the holdout did not fall (47.2% to 51.4%, +4.2 pts, 95% CI -5.6 to +15.3, so not a significant rise either). The guardrail makes the agent safe. It does not make the agent more truthful. The agent still says that an action is done when it is not, and it invents details such as refund timelines.
- **What changed:** `agent/answer_check.py` checks each draft final answer before the customer sees it. It flags a claimed action without a successful tool call, an id or amount that no tool result or customer message contains, and invented details (refund timelines, payment methods, emails). If the draft has a problem, the model gets **one** chance to rewrite it. The first two checks use the same detectors as the code graders, so they improve by design. For this reason the test uses the independent LLM judge on the holdout. Starting point: v2.
- **Leakage check:** the invented-detail patterns came from reading failed dev trajectories. No holdout trace was read.
- **Results (run `v4` against `v2`):**

| Metric | v2 | v4 | Change |
|---|---|---|---|
| Hallucination rate, holdout (judge `j4`, 72 trials) | 51.4% | 45.8% | -5.6 pts (95% CI -12.5 to +0.0) |
| Unsupported / contradicted claims, holdout | 18.0% / 16.0% | 15.8% / 17.1% | small |
| Fabricated entity rate, holdout (code) | 15.3% | 15.3% | 0.0 pts |
| Fabricated action rate, holdout (code) | 2.8% | 1.4% | -1.4 pts |
| Success, dev | 67.2% | 67.2% | 0.0 pts (CI -2.3 to +2.3) |
| Success, holdout | 50.0% | 51.4% | +1.4 pts (CI +0.0 to +4.2) |
| Validator rewrites | n/a | 29 rewrites in 28 of 200 trials | |
| Notional cost per success, holdout | $0.0127 | $0.0130 | +2% |

- **Gate: FAIL**, on the success gate and on the hallucination gate (`results/gate_v2_vs_v4.json`, `results/gate_v2_vs_v4_hallucination.json`). The fall in hallucination is small and its interval touches 0 (-12.5 to +0.0), so it is not significant. Success did not change. No category regressed.
- **What we learned:** the validator rarely fires (28 of 200 trials), so it cannot move the rate much. Most hallucinated claims are not an id, an amount or a known pattern, so the code checks cannot see them. A catch-all validator needs the judge itself at run time, which costs one model call for each answer. The judge is not yet validated (M4), so the 4-point fall is only a hint.
- **Decision:** v4 is not promoted. v2 stays the live version.

## v5: guardrail with remediation (REJECTED by the gate; a real but modest gain)

- **Target:** `skipped_order_lookup`, still the largest category after v2 (28 of 42 failed dev trials). After v2 the guard blocked the bad write, but the agent did not know the real order data, so it kept guessing amounts or ids.
- **Hypothesis (declared before the run):** success rises by more than the 14.0-point noise floor on both dev and holdout.
- **What changed:** when the guard blocks a write because the order was not read, the **system** reads the order for the agent (`get_order`), logs that read as a tool event (marked `auto`), and returns the real order data inside the error message. The agent still decides what to do next. Starting point: v2. Code: `agent/loop.py` (flag `remediate`). Tests: `tests/test_loop.py`.
- **This is a scaffold, not a model improvement.** The system performed 94 reads for the agent, in 89 of 200 trials. The graders count the logged read as the lookup that rule P3 asks for.
- **Results, first run (run `v5` against `v2`):** all tasks 61.0% to 72.5% (+11.5 pts, 95% CI +4.5 to +19.5). Dev 67.2% to 77.3% (+10.2 pts, CI +1.6 to +20.3). Holdout 50.0% to 63.9% (+13.9 pts, CI +2.8 to +27.8). **Gate: FAIL** (`results/gate_v2_vs_v5.json`): dev gain 10.2 and holdout gain 13.9 are below the 14.0-point noise floor. No category regresses.
- **Replication (declared before it was run):** the brief says "run more trials" for a gain that is close to the noise. Both v2 and v5 were run a second time with another seed (`v2-b`, `v5-b`). Pooled over 8 trials for each task (`python -m evals.pool`):

| Metric (pooled, 8 trials for each task) | v2 | v5 | Change |
|---|---|---|---|
| Success, all tasks | 63.5% | 73.0% | +9.5 pts (95% CI +4.3 to +15.7) |
| Success, dev | 69.5% | 79.3% | +9.8 pts (CI +3.1 to +17.2) |
| Success, holdout | 52.8% | 61.8% | +9.0 pts (CI +1.4 to +20.1) |
| Dev `cancel` | 52.5% | 85.0% | +32.5 pts |
| Dev `multi` | 31.2% | 56.2% | +25.0 pts |
| Dev `refund` | 82.1% | 92.9% | +10.7 pts |
| Dev `adversarial` | 88.8% | 85.0% | -3.7 pts |
| Dev `lookup` | 41.7% | 41.7% | 0.0 pts |
| Notional cost per success, holdout | $0.0121 | $0.0105 | -13% |

  McNemar on the dev tasks (per-task majority): p = 0.062. Flip rates of the repeated pairs: v0 14.0%, v2 16.0%, v5 17.0%.
- **Gate on the pooled runs: FAIL** (`results/gate_v2-pool_vs_v5-pool.json`). The gain is significant by the paired bootstrap on both splits (the intervals exclude 0), but it is +9.8 on dev and +9.0 on holdout. Both are below the 14.0-point noise floor. By the rule in the brief, a change smaller than the run-to-run noise is called noise.
- **How to read this:** v5 very probably helps (two independent runs agree, and the gain is largest in the categories that the fix targets). The size of the gain, about 9 to 10 points, is smaller than the noise floor that this project set for itself. The gate rejects it, and v2 stays the live version. The noise floor is a flip rate from single runs of 4 trials. For pooled runs it is conservative. We keep the rule as declared, and we do not change it after the result.
- **Dataset version:** v1 (the 50 original tasks). The run also produced 20 trials of the new regression tasks (`v5-reg`).

## regression suite (dataset v2 tasks T051 to T055, 4 trials each)

Run for every version (`results/<version>-reg`). Successes out of 20 trials: v0 8, v1 8, v2 10, v3 6, **v4 14**, v5 11. Per-task results and the reading are in `docs/regression-suite.md`. These are dev tasks, so they were not used to gate any version.

## M4 judge validation, and the judge numbers in this file

- **What changed:** the LLM judge was validated against hand labels (`docs/judge-validation.md`). The first judge prompt (`j1`) agreed poorly with the owner's first-pass labels (claim kappa 0.07). Two parts of the problem were found: real judge errors (placed_at read as a delivery date, "not found" errors, day counts, "full refund" claims, a refusal rubric that was too lenient) and a large disagreement between the owner's first-pass labels and the written rubric (kappa 0.10 to 0.29 on claims and trials, 0.03 to 0.06 on refusals).
- **Labels:** at the owner's request, Claude re-reviewed all 150 labeled trials under the written rubric. The final labels are that re-review. The owner's first-pass labels are kept. This is a deviation from the brief, which asks for labels that you make yourself.
- **Final judge prompt `j4`, on judge-test (never used for tuning), against the final labels:** claim kappa 0.90 (TPR 0.91, TNR 0.98, n = 168), trial kappa 0.94 (TPR 0.97, TNR 0.98, n = 73), refusal kappa 0.88 (TPR 1.00, TNR 0.85, n = 38). Against the owner's first-pass labels the same judge answers give kappa 0.27, 0.35 and 0.01.
- **All judged hallucination rates were made again with `j4`.** Earlier entries used `j1`, which was not validated. Version rates on the holdout (72 trials each): v0 47.2%, v1 45.8%, v2 51.4%, v3 68.1%, v4 45.8%, v5 36.1%. The earlier `j1` values were 44.4%, 50.0%, 52.8%, 62.5%, 48.6% and 38.9%. No gate decision changed, because the gates for v1, v2 and v3 use success only, and v4 still fails its hallucination gate.
- **v5 and hallucination (exploratory, not a declared target):** the hallucination gate (`--target-hallucination`) passes for v5 against v2 (51.4% to 36.1%, -15.3 pts, 95% CI -30.6 to -2.8; unsupported claims 18.0% to 6.6%). The success gate still rejects v5 (gain below the noise floor), so v5 is not promoted. Because hallucination was not declared as v5's target before the run, this result is a hint and not a gate pass.
