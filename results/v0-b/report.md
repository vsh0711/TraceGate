# Run report: v0-b

Version **v0** (baseline). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 44.5% (32.5% to 56.0%) |
| pass^1 / pass@1 | 44.5% / 44.5% |
| pass^2 / pass@2 | 35.0% / 54.0% |
| pass^3 / pass@3 | 30.5% / 59.0% |
| pass^4 / pass@4 | 28.0% / 62.0% |
| Outcome graders passing: state / answer / policy | 67.0% / 95.5% / 59.0% |
| Policy violation rate | 41.0% |
| Tool selection precision / recall | 86.7% / 74.1% |
| Args: schema-valid / real entities / correct | 80.8% / 75.3% / 81.1% |
| Efficiency: steps / reference steps; loop rate | 1.00; 4.5% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 11.5% |
| Fabricated action rate | 4.0% |
| Notional cost per successful task | $0.0124 |
| p95 latency per trial (model time) | 89.9 s |

| Category | Success |
|---|---|
| lookup | 35.0% |
| cancel | 35.7% |
| refund | 56.8% |
| address | 35.0% |
| multi | 21.4% |
| adversarial | 56.7% |

| Difficulty | Success |
|---|---|
| easy | 21.7% |
| medium | 65.0% |
| hard | 40.0% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 77.8% | 70.0% |
| get_customer | 98.0% | 98.0% |
| get_order | 100.0% | 44.1% |
| issue_refund | 58.3% | 94.2% |
| list_orders | 100.0% | 18.8% |
| transfer_to_human | 0.0% | n/a |
| update_address | 83.3% | 100.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 12 |
| P2_own_orders | 5 |
| P3_read_before_write | 74 |
| P5_cancel_status | 3 |
| P6_address_status | 4 |
| P7_refund_eligibility | 7 |
| P8_refund_amount | 13 |
| P9_no_double_refund | 16 |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 46.1% (32.0% to 60.2%) |
| pass^1 / pass@1 | 46.1% / 46.1% |
| pass^2 / pass@2 | 36.5% / 55.7% |
| pass^3 / pass@3 | 31.2% / 60.2% |
| pass^4 / pass@4 | 28.1% / 62.5% |
| Outcome graders passing: state / answer / policy | 69.5% / 96.9% / 56.2% |
| Policy violation rate | 43.8% |
| Tool selection precision / recall | 86.0% / 72.5% |
| Args: schema-valid / real entities / correct | 80.2% / 75.7% / 83.3% |
| Efficiency: steps / reference steps; loop rate | 1.00; 3.1% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 9.4% |
| Fabricated action rate | 3.1% |
| Notional cost per successful task | $0.0115 |
| p95 latency per trial (model time) | 88.9 s |

| Category | Success |
|---|---|
| lookup | 41.7% |
| cancel | 30.0% |
| refund | 53.6% |
| address | 25.0% |
| multi | 25.0% |
| adversarial | 65.0% |

| Difficulty | Success |
|---|---|
| easy | 22.2% |
| medium | 58.9% |
| hard | 50.0% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 65.2% | 75.0% |
| get_customer | 100.0% | 97.7% |
| get_order | 100.0% | 39.2% |
| issue_refund | 50.9% | 96.4% |
| list_orders | 100.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 88.9% | 100.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 8 |
| P2_own_orders | 4 |
| P3_read_before_write | 52 |
| P5_cancel_status | 3 |
| P6_address_status | 3 |
| P7_refund_eligibility | 5 |
| P8_refund_amount | 4 |
| P9_no_double_refund | 10 |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 41.7% (23.6% to 61.1%) |
| pass^1 / pass@1 | 41.7% / 41.7% |
| pass^2 / pass@2 | 32.4% / 50.9% |
| pass^3 / pass@3 | 29.2% / 56.9% |
| pass^4 / pass@4 | 27.8% / 61.1% |
| Outcome graders passing: state / answer / policy | 62.5% / 93.1% / 63.9% |
| Policy violation rate | 36.1% |
| Tool selection precision / recall | 87.8% / 77.1% |
| Args: schema-valid / real entities / correct | 81.6% / 74.6% / 77.7% |
| Efficiency: steps / reference steps; loop rate | 1.00; 6.9% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 15.3% |
| Fabricated action rate | 5.6% |
| Notional cost per successful task | $0.0139 |
| p95 latency per trial (model time) | 88.7 s |

| Category | Success |
|---|---|
| lookup | 25.0% |
| cancel | 50.0% |
| refund | 62.5% |
| address | 50.0% |
| multi | 16.7% |
| adversarial | 40.0% |

| Difficulty | Success |
|---|---|
| easy | 20.8% |
| medium | 79.2% |
| hard | 25.0% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 65.0% |
| get_customer | 94.4% | 98.5% |
| get_order | 100.0% | 52.9% |
| issue_refund | 71.0% | 91.7% |
| list_orders | n/a | 0.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 66.7% | 100.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 4 |
| P2_own_orders | 1 |
| P3_read_before_write | 22 |
| P6_address_status | 1 |
| P7_refund_eligibility | 2 |
| P8_refund_amount | 9 |
| P9_no_double_refund | 6 |

## Examples to click through

- Failed trials: [T001/t2](traces/T001_t2.md), [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md)
- Policy violations: [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md), [T002/t1](traces/T002_t1.md)
- Fabricated entities: [T013/t2](traces/T013_t2.md), [T017/t1](traces/T017_t1.md), [T017/t2](traces/T017_t2.md)
- Fabricated actions: [T008/t3](traces/T008_t3.md), [T017/t1](traces/T017_t1.md), [T020/t0](traces/T020_t0.md)
- Hallucinated (judge): none
- Looped: [T013/t2](traces/T013_t2.md), [T013/t3](traces/T013_t3.md), [T015/t0](traces/T015_t0.md)
