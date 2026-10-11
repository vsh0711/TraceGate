# Regression suite (dataset v2)

Dataset v2 adds 5 dev tasks (T051 to T055). Each one tests a failure mode that the first 50 tasks did not test (`evals/new_tasks_v2.json`). We ran all six versions on them (4 trials for each task, `results/<version>-reg`). The numbers below are successes out of 4 trials.

| Task | Failure mode | v0 | v1 | v2 | v3 | v4 | v5 |
|---|---|---|---|---|---|---|---|
| T051 | The customer gives no identity at first | 0 | 0 | 3 | 3 | 3 | 3 |
| T052 | The customer mistypes the email, then corrects it | 0 | 1 | 0 | 1 | 0 | 1 |
| T053 | The customer asks for a detail that nothing gives (refund time) | 1 | 0 | 0 | 0 | **4** | 0 |
| T054 | The customer asks a policy question | 4 | 4 | 4 | 2 | 4 | 4 |
| T055 | The customer states a false premise ("thank you for cancelling") | 3 | 3 | 3 | 0 | 3 | 3 |
| **All (of 20)** | | 8 | 8 | 10 | 6 | **14** | 11 |

## What the table shows

1. **The guardrail fixes the "no identity" case.** v0 and v1 fail all 8 trials of T051. Every guarded version passes 3 of 4. This case came from the online traces, where the agent tried an order tool before the customer gave an identity.
2. **The answer validator (v4) solves the invented-detail case.** v4 passes all 4 trials of T053. The other versions pass 0 or 1. This is **in-sample**: the task and the validator's patterns come from the same failure mode ("3-5 business days"). The result shows that the validator works as designed. It does not show that it works on other kinds of invented details.
3. **Exemplar memory (v3) breaks two tasks.** v3 fails T055 (0 of 4, while the others pass 3 of 4) and loses on T054. This agrees with the main result: examples taken from the weak model's own trajectories spread its habits.
4. **The mistyped email (T052) is hard for every version.** No version passes more than 1 of 4. The agent does not recover well after a failed verification. This is an open failure mode for the next iteration.
5. **v5 gains 1 trial over v2** (11 against 10 of 20). This is inside the noise.

## Limits

- 20 trials for each version. One trial is 5 points. Read every difference of 1 or 2 trials as noise.
- These are dev tasks. They show how each version handles failure modes that we already know. They are not a clean test of generalization.
- Gate decisions use the 50 tasks of dataset v1 only (see `CHANGELOG.md`).
