# Run report: v1

Version **v1** (tool descriptions). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 41.5% (29.5% to 54.0%) |
| pass^1 / pass@1 | 41.5% / 41.5% |
| pass^2 / pass@2 | 36.3% / 46.7% |
| pass^3 / pass@3 | 33.5% / 49.0% |
| pass^4 / pass@4 | 32.0% / 50.0% |
| Outcome graders passing: state / answer / policy | 64.0% / 93.5% / 61.5% |
| Policy violation rate | 38.5% |
| Tool selection precision / recall | 87.1% / 73.7% |
| Args: schema-valid / real entities / correct | 78.8% / 75.2% / 79.9% |
| Efficiency: steps / reference steps; loop rate | 1.03; 7.5% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 12.5% |
| Fabricated action rate | 6.5% |
| Notional cost per successful task | $0.0155 |
| p95 latency per trial (model time) | 106.1 s |

| Category | Success |
|---|---|
| lookup | 35.0% |
| cancel | 39.3% |
| refund | 47.7% |
| address | 25.0% |
| multi | 14.3% |
| adversarial | 58.3% |

| Difficulty | Success |
|---|---|
| easy | 15.0% |
| medium | 67.5% |
| hard | 33.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 90.6% | 72.5% |
| get_customer | 98.0% | 100.0% |
| get_order | 100.0% | 45.2% |
| issue_refund | 50.0% | 82.7% |
| list_orders | 80.0% | 25.0% |
| update_address | 80.0% | 80.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 4 |
| P2_own_orders | 3 |
| P3_read_before_write | 68 |
| P5_cancel_status | 4 |
| P6_address_status | 4 |
| P7_refund_eligibility | 11 |
| P8_refund_amount | 9 |
| P9_no_double_refund | 13 |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 45.3% (30.5% to 61.7%) |
| pass^1 / pass@1 | 45.3% / 45.3% |
| pass^2 / pass@2 | 40.1% / 50.5% |
| pass^3 / pass@3 | 36.7% / 52.3% |
| pass^4 / pass@4 | 34.4% / 53.1% |
| Outcome graders passing: state / answer / policy | 68.0% / 94.5% / 62.5% |
| Policy violation rate | 37.5% |
| Tool selection precision / recall | 88.4% / 72.5% |
| Args: schema-valid / real entities / correct | 79.1% / 75.6% / 81.4% |
| Efficiency: steps / reference steps; loop rate | 1.03; 7.8% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 9.4% |
| Fabricated action rate | 5.5% |
| Notional cost per successful task | $0.0138 |
| p95 latency per trial (model time) | 113.5 s |

| Category | Success |
|---|---|
| lookup | 41.7% |
| cancel | 35.0% |
| refund | 46.4% |
| address | 16.7% |
| multi | 25.0% |
| adversarial | 67.5% |

| Difficulty | Success |
|---|---|
| easy | 16.7% |
| medium | 64.3% |
| hard | 44.4% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 84.2% | 80.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 100.0% | 40.8% |
| issue_refund | 44.6% | 89.3% |
| list_orders | 100.0% | 33.3% |
| update_address | 85.7% | 75.0% |

| Policy rule broken | Trials |
|---|---|
| P3_read_before_write | 43 |
| P5_cancel_status | 4 |
| P6_address_status | 2 |
| P7_refund_eligibility | 9 |
| P8_refund_amount | 2 |
| P9_no_double_refund | 9 |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 34.7% (16.7% to 55.6%) |
| pass^1 / pass@1 | 34.7% / 34.7% |
| pass^2 / pass@2 | 29.6% / 39.8% |
| pass^3 / pass@3 | 27.8% / 43.1% |
| pass^4 / pass@4 | 27.8% / 44.4% |
| Outcome graders passing: state / answer / policy | 56.9% / 91.7% / 59.7% |
| Policy violation rate | 40.3% |
| Tool selection precision / recall | 84.8% / 75.8% |
| Args: schema-valid / real entities / correct | 78.5% / 74.6% / 77.3% |
| Efficiency: steps / reference steps; loop rate | 1.04; 6.9% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 18.1% |
| Fabricated action rate | 8.3% |
| Notional cost per successful task | $0.0194 |
| p95 latency per trial (model time) | 101.6 s |

| Category | Success |
|---|---|
| lookup | 25.0% |
| cancel | 50.0% |
| refund | 50.0% |
| address | 37.5% |
| multi | 0.0% |
| adversarial | 40.0% |

| Difficulty | Success |
|---|---|
| easy | 12.5% |
| medium | 75.0% |
| hard | 16.7% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 65.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 52.9% |
| issue_refund | 60.0% | 75.0% |
| list_orders | 0.0% | 0.0% |
| update_address | 66.7% | 100.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 4 |
| P2_own_orders | 3 |
| P3_read_before_write | 25 |
| P6_address_status | 2 |
| P7_refund_eligibility | 2 |
| P8_refund_amount | 7 |
| P9_no_double_refund | 4 |

## Examples to click through

- Failed trials: [T001/t3](traces/T001_t3.md), [T002/t2](traces/T002_t2.md), [T002/t3](traces/T002_t3.md)
- Policy violations: [T005/t0](traces/T005_t0.md), [T005/t1](traces/T005_t1.md), [T005/t2](traces/T005_t2.md)
- Fabricated entities: [T009/t3](traces/T009_t3.md), [T018/t0](traces/T018_t0.md), [T018/t1](traces/T018_t1.md)
- Fabricated actions: [T008/t1](traces/T008_t1.md), [T009/t1](traces/T009_t1.md), [T009/t3](traces/T009_t3.md)
- Hallucinated (judge): none
- Looped: [T013/t1](traces/T013_t1.md), [T014/t3](traces/T014_t3.md), [T015/t1](traces/T015_t1.md)
