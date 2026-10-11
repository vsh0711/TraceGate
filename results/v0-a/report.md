# Run report: v0-a

Version **v0** (baseline). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 42.5% (30.0% to 55.0%) |
| pass^1 / pass@1 | 42.5% / 42.5% |
| pass^2 / pass@2 | 37.3% / 47.7% |
| pass^3 / pass@3 | 34.5% / 50.0% |
| pass^4 / pass@4 | 32.0% / 52.0% |
| Outcome graders passing: state / answer / policy | 66.5% / 94.0% / 59.0% |
| Policy violation rate | 41.0% |
| Tool selection precision / recall | 90.0% / 75.4% |
| Args: schema-valid / real entities / correct | 82.0% / 77.0% / 80.7% |
| Efficiency: steps / reference steps; loop rate | 0.99; 2.5% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 11.5% |
| Fabricated action rate | 3.5% |
| Hallucination rate (response level, judge) | 47.2% |
| Claim-level unsupported / contradicted rate (135 claims) | 15.6% / 19.3% |
| Refusal explained (judge, refusal tasks) | 16.7% |
| Notional cost per successful task | $0.0127 |
| p95 latency per trial (model time) | 73.2 s |

| Category | Success |
|---|---|
| lookup | 35.0% |
| cancel | 42.9% |
| refund | 47.7% |
| address | 35.0% |
| multi | 14.3% |
| adversarial | 56.7% |

| Difficulty | Success |
|---|---|
| easy | 15.0% |
| medium | 66.2% |
| hard | 38.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 88.6% | 77.5% |
| get_customer | 98.0% | 99.5% |
| get_order | 98.8% | 44.7% |
| issue_refund | 63.5% | 90.4% |
| list_orders | 80.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 85.7% | 90.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 11 |
| P2_own_orders | 4 |
| P3_read_before_write | 73 |
| P6_address_status | 4 |
| P7_refund_eligibility | 7 |
| P8_refund_amount | 12 |
| P9_no_double_refund | 17 |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 46.9% (32.0% to 61.7%) |
| pass^1 / pass@1 | 46.9% / 46.9% |
| pass^2 / pass@2 | 40.6% / 53.1% |
| pass^3 / pass@3 | 37.5% / 56.2% |
| pass^4 / pass@4 | 34.4% / 59.4% |
| Outcome graders passing: state / answer / policy | 71.1% / 95.3% / 60.2% |
| Policy violation rate | 39.8% |
| Tool selection precision / recall | 90.5% / 76.0% |
| Args: schema-valid / real entities / correct | 81.1% / 77.7% / 83.9% |
| Efficiency: steps / reference steps; loop rate | 0.99; 2.3% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 10.2% |
| Fabricated action rate | 2.3% |
| Notional cost per successful task | $0.0111 |
| p95 latency per trial (model time) | 69.0 s |

| Category | Success |
|---|---|
| lookup | 41.7% |
| cancel | 40.0% |
| refund | 46.4% |
| address | 33.3% |
| multi | 25.0% |
| adversarial | 65.0% |

| Difficulty | Success |
|---|---|
| easy | 19.4% |
| medium | 60.7% |
| hard | 52.8% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 80.0% | 80.0% |
| get_customer | 100.0% | 99.2% |
| get_order | 98.2% | 45.8% |
| issue_refund | 55.6% | 89.3% |
| list_orders | 80.0% | 33.3% |
| transfer_to_human | 0.0% | n/a |
| update_address | 93.3% | 87.5% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 7 |
| P2_own_orders | 3 |
| P3_read_before_write | 46 |
| P6_address_status | 2 |
| P7_refund_eligibility | 4 |
| P8_refund_amount | 3 |
| P9_no_double_refund | 9 |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 34.7% (15.3% to 56.9%) |
| pass^1 / pass@1 | 34.7% / 34.7% |
| pass^2 / pass@2 | 31.5% / 38.0% |
| pass^3 / pass@3 | 29.2% / 38.9% |
| pass^4 / pass@4 | 27.8% / 38.9% |
| Outcome graders passing: state / answer / policy | 58.3% / 91.7% / 56.9% |
| Policy violation rate | 43.1% |
| Tool selection precision / recall | 89.3% / 74.3% |
| Args: schema-valid / real entities / correct | 83.3% / 75.8% / 75.4% |
| Efficiency: steps / reference steps; loop rate | 0.99; 2.8% |
| Guardrail blocks per trial | 0.00 |
| Fabricated entity rate | 13.9% |
| Fabricated action rate | 5.6% |
| Hallucination rate (response level, judge) | 47.2% |
| Claim-level unsupported / contradicted rate (135 claims) | 15.6% / 19.3% |
| Refusal explained (judge, refusal tasks) | 16.7% |
| Notional cost per successful task | $0.0163 |
| p95 latency per trial (model time) | 75.2 s |

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
| easy | 8.3% |
| medium | 79.2% |
| hard | 16.7% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 75.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 42.6% |
| issue_refund | 75.9% | 91.7% |
| list_orders | n/a | 0.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 66.7% | 100.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 4 |
| P2_own_orders | 1 |
| P3_read_before_write | 27 |
| P6_address_status | 2 |
| P7_refund_eligibility | 3 |
| P8_refund_amount | 9 |
| P9_no_double_refund | 8 |

## Examples to click through

- Failed trials: [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md), [T002/t2](traces/T002_t2.md)
- Policy violations: [T002/t0](traces/T002_t0.md), [T002/t3](traces/T002_t3.md), [T005/t0](traces/T005_t0.md)
- Fabricated entities: [T009/t3](traces/T009_t3.md), [T017/t0](traces/T017_t0.md), [T017/t1](traces/T017_t1.md)
- Fabricated actions: [T008/t1](traces/T008_t1.md), [T009/t3](traces/T009_t3.md), [T013/t2](traces/T013_t2.md)
- Hallucinated (judge): [T003/t0](traces/T003_t0.md), [T008/t0](traces/T008_t0.md), [T008/t1](traces/T008_t1.md)
- Looped: [T018/t0](traces/T018_t0.md), [T018/t3](traces/T018_t3.md), [T024/t3](traces/T024_t3.md)
