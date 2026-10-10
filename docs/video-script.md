# Script for the 2-minute video

The brief asks for one video: a failing trace, its taxonomy label, the fix, and the gate passing. This script gives the shots and the words. Record it yourself.

| Time | On screen | Say |
|---|---|---|
| 0:00 to 0:15 | `README.md` with the improvement chart | "I built a support agent and the system that grades it. Success on a frozen holdout rose from X percent to Y percent in N gated iterations." |
| 0:15 to 0:45 | A failing trace (`results/v0-a/traces/...`) | "This trial failed. The agent refunded an order before it read the order. The code grader P3 caught it. The final database state is wrong." |
| 0:45 to 1:05 | `docs/failure-taxonomy.md`, the row for the top category | "I read the failed trials and gave each a category. This category is the largest, with N trials. I fix the largest category first." |
| 1:05 to 1:30 | The diff in `CHANGELOG.md` and the changed tool description or guardrail | "The fix is this change. It uses only dev data." |
| 1:30 to 1:50 | `python -m evals.gate` output | "The gate checks four things: gain above the noise floor, a significant dev gain, a holdout gain, and no category that regresses. All pass." |
| 1:50 to 2:00 | `docs/judge-validation.md` | "The judge agrees with my labels: kappa K on N held-out labels." |
