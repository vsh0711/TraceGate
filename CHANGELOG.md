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
- **Limits:** the guard blocks 0.82 calls per trial. The guard makes the system safe, but the model still guesses. `fabricated_entity_rate` did not fall (20.8% on holdout). The `lookup` and `multi` categories did not improve, because their failures are stalls, not policy errors.
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
| Failed dev trials, `gave_up_early` | 5 | 14 | +9 |
| Notional cost per success, holdout | $0.0127 | $0.0174 | +37% |

- **Gate: FAIL** (`results/gate_v2_vs_v3.json`). The dev result fell. The holdout gain is below the noise floor (14.0%). `lookup` lost more than 10 points on both splits and `address` lost 25 points on dev.
- **What we learned:** the examples are the weak model's own successes, and they still contain its bad habits. They show the agent narrating and asking for confirmation before a read-only step. The model copied this, and the h2 user ends the conversation after a statement. Memory built from a weak model's own trajectories spreads its mistakes. Better memory needs curated or reference-based demonstrations.
- **Decision:** v3 is not promoted. v2 stays the live version.
