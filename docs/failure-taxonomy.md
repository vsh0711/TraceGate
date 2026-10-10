# Failure taxonomy (M5)

This document groups the failures of the baseline (version v0, harness h2). It uses 137 failed trials from the **dev split** of runs `v0-a` and `v0-b`. Holdout trials were not read (leakage rule).

## How the categories were made

1. I read every one of the failed dev trajectories and wrote a free-text note for each one (open coding). The notes are in `labels/failure_notes.jsonl`.
2. I grouped the notes into categories (axial coding). The coding rule is: **code the first step where the agent went wrong**. The first wrong step is the root cause. Later steps are symptoms.
3. I wrote a rule-based tagger (`evals/taxonomy.py`) that applies the same rule to a logged trajectory. The tagger lets us count failures for every later version without reading each trace again.
4. Some problems are not a root cause but a symptom (a repeated write, an invented fact). They are **secondary tags**. A trial has 1 primary category and 0 or more secondary tags.

Important: the notes were written by Claude, not by a human. The categories and counts are a first draft. A human reviewer should read at least a sample of the notes.

## Counts: primary category (sorted)

| Rank | Category | Trials | Share | Meaning |
|---|---|---|---|---|
| 1 | `skipped_order_lookup` | 105 | 77% | Acted on an order without reading it first: a write before get_order, or a guessed or placeholder order id or amount. |
| 2 | `skipped_identity_check` | 15 | 11% | Used an order tool before identity was verified, or continued after verification failed. |
| 3 | `gave_up_early` | 9 | 7% | Stopped before the job was done: narrated or asked instead of acting, or gave no answer. |
| 4 | `malformed_tool_call` | 6 | 4% | Wrote the tool call as plain text, so no tool ran, and the job was never done. |
| 5 | `misread_request` | 1 | 1% | Did a different action from the one the customer asked for. |
| 6 | `policy_violation` | 1 | 1% | Read the order, then still did something that the policy does not allow. |

**The top category is `skipped_order_lookup`. It is the next fix.**

## Counts: secondary tags

| Tag | Trials | Meaning |
|---|---|---|
| `wrong_tool_args` | 39 | At least one call had invalid, unreal or placeholder arguments. |
| `repeated_action` | 31 | Repeated a write that already succeeded, or called the same tool with the same arguments 3 or more times. |
| `hallucinated_fact` | 14 | Stated an id, amount or date that is not in the evidence (code check), or the judge found an unsupported claim. |
| `fabricated_action` | 6 | Said it did an action that no tool call did. |

## Example traces (2 per category)

- **`skipped_order_lookup`**: [T006 trial 0 (v0-a)](../results/v0-a/traces/T006_t0.md); [T007 trial 0 (v0-a)](../results/v0-a/traces/T007_t0.md)
- **`skipped_identity_check`**: [T002 trial 0 (v0-a)](../results/v0-a/traces/T002_t0.md); [T039 trial 0 (v0-a)](../results/v0-a/traces/T039_t0.md)
- **`gave_up_early`**: [T001 trial 3 (v0-a)](../results/v0-a/traces/T001_t3.md); [T002 trial 2 (v0-a)](../results/v0-a/traces/T002_t2.md)
- **`malformed_tool_call`**: [T014 trial 0 (v0-a)](../results/v0-a/traces/T014_t0.md); [T025 trial 2 (v0-a)](../results/v0-a/traces/T025_t2.md)
- **`misread_request`**: [T036 trial 1 (v0-a)](../results/v0-a/traces/T036_t1.md)
- **`policy_violation`**: [T050 trial 1 (v0-a)](../results/v0-a/traces/T050_t1.md)

## Notes for three typical trials

- [T006 trial 0 (v0-a)](../results/v0-a/traces/T006_t0.md) (`skipped_order_lookup`): First change was cancel_order(order_id=O1002) with no earlier get_order for that order. It used a guessed or placeholder argument (for example amount 0 or 'get_order').
- [T002 trial 0 (v0-a)](../results/v0-a/traces/T002_t0.md) (`skipped_identity_check`): Called get_order before a successful get_customer.
- [T001 trial 3 (v0-a)](../results/v0-a/traces/T001_t3.md) (`gave_up_early`): Ended the turn with narration or a question, and never gave the answer or made the change.

## Check of the tagger against the manual labels

The tagger gives the same primary category as the manual label for 137 of 137 trials (100%). This check is in-sample: the tagger rules were written after the reading, so the number shows only that the rules reproduce the reading. It does not show that they work on new failures.

## Known limits

- One coder wrote the notes, and the same coder wrote the tagger. No second coder checked them.
- Most failures (about three quarters) are one category. A finer split inside it may help later, for example 'wrote before lookup' versus 'guessed an argument'.
- The coding used harness h2 (see `docs/harness.md`). Counts from the earlier h1 runs are not comparable.
- The 4 trials per task are not independent. One weak task can add 4 failures.
