# Policy rules and their code graders

The agent reads the policy in `agent/policy.md`. The grader file `evals/graders/policy.py` checks the rules below on every trajectory. A violation counts only when a write tool ran. A call that the guardrail blocked did not run, so it is not a violation.

| Rule | Check |
|---|---|
| P1 verify first | No order tool runs before a successful `get_customer`. |
| P2 own orders | A write changes only an order of the verified customer. |
| P3 read before write | `get_order` ran for that order before the write. |
| P4 confirm before write | The agent asked, and the customer replied, before the write. |
| P5 cancel status | `cancel_order` runs only on a `processing` order. |
| P6 address status | `update_address` runs only on a `processing` order. |
| P7 refund eligibility | `issue_refund` runs only on a `delivered` order, delivered 30 days ago or less, with no final-sale item. |
| P8 refund amount | The refund is more than 0 and not more than the order total. |
| P9 no double refund | The order has no earlier refund. |

The tools do not enforce policy. They check data integrity only. For this reason, a wrong agent can break a rule, and the graders can see it.

The store clock is fixed. Today is 2026-10-01 (`config.TODAY`).
