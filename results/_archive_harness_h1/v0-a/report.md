# Run report: v0-a

Version **v0** (baseline). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 43.5% (31.5% to 55.5%) |
| pass^1 / pass@1 | 43.5% / 43.5% |
| pass^2 / pass@2 | 38.3% / 48.7% |
| pass^3 / pass@3 | 35.0% / 50.5% |
| pass^4 / pass@4 | 32.0% / 52.0% |
| Outcome graders passing: state / answer / policy | 65.0% / 95.0% / 56.5% |
| Policy violation rate | 43.5% |
| Tool selection precision / recall | 89.6% / 78.7% |
| Args: schema-valid / real entities / correct | 80.7% / 76.1% / 81.7% |
| Efficiency: steps / reference steps; loop rate | 1.11; 6.5% |
| Fabricated entity rate | 13.0% |
| Fabricated action rate | 3.0% |
| Hallucination rate (response level, judge) | 42.0% |
| Claim-level unsupported / contradicted rate (432 claims) | 14.6% / 12.5% |
| Refusal explained (judge, refusal tasks) | 35.7% |
| Notional cost per successful task | $0.0139 |
| p95 latency per trial (model time) | 67.5 s |

| Category | Success |
|---|---|
| lookup | 50.0% |
| cancel | 39.3% |
| refund | 47.7% |
| address | 35.0% |
| multi | 14.3% |
| adversarial | 56.7% |

| Difficulty | Success |
|---|---|
| easy | 20.0% |
| medium | 65.0% |
| hard | 38.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 86.1% | 77.5% |
| get_customer | 98.0% | 100.0% |
| get_order | 99.0% | 50.5% |
| issue_refund | 62.5% | 96.2% |
| list_orders | 100.0% | 31.2% |
| transfer_to_human | 0.0% | n/a |
| update_address | 86.4% | 95.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 11 |
| P2_own_orders | 4 |
| P3_read_before_write | 77 |
| P5_cancel_status | 1 |
| P6_address_status | 4 |
| P7_refund_eligibility | 7 |
| P8_refund_amount | 13 |
| P9_no_double_refund | 23 |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 46.9% (32.8% to 61.7%) |
| pass^1 / pass@1 | 46.9% / 46.9% |
| pass^2 / pass@2 | 39.6% / 54.2% |
| pass^3 / pass@3 | 35.2% / 57.0% |
| pass^4 / pass@4 | 31.2% / 59.4% |
| Outcome graders passing: state / answer / policy | 66.4% / 95.3% / 57.0% |
| Policy violation rate | 43.0% |
| Tool selection precision / recall | 90.5% / 79.7% |
| Args: schema-valid / real entities / correct | 78.5% / 75.1% / 85.0% |
| Efficiency: steps / reference steps; loop rate | 1.10; 6.2% |
| Fabricated entity rate | 9.4% |
| Fabricated action rate | 1.6% |
| Hallucination rate (response level, judge) | 45.3% |
| Claim-level unsupported / contradicted rate (297 claims) | 14.1% / 12.8% |
| Refusal explained (judge, refusal tasks) | 36.7% |
| Notional cost per successful task | $0.0126 |
| p95 latency per trial (model time) | 66.3 s |

| Category | Success |
|---|---|
| lookup | 50.0% |
| cancel | 35.0% |
| refund | 46.4% |
| address | 33.3% |
| multi | 25.0% |
| adversarial | 65.0% |

| Difficulty | Success |
|---|---|
| easy | 22.2% |
| medium | 58.9% |
| hard | 52.8% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 76.2% | 80.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 98.4% | 52.5% |
| issue_refund | 55.1% | 96.4% |
| list_orders | 100.0% | 41.7% |
| transfer_to_human | 0.0% | n/a |
| update_address | 93.8% | 93.8% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 7 |
| P2_own_orders | 3 |
| P3_read_before_write | 49 |
| P5_cancel_status | 1 |
| P6_address_status | 2 |
| P7_refund_eligibility | 4 |
| P8_refund_amount | 3 |
| P9_no_double_refund | 18 |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 37.5% (16.7% to 59.7%) |
| pass^1 / pass@1 | 37.5% / 37.5% |
| pass^2 / pass@2 | 36.1% / 38.9% |
| pass^3 / pass@3 | 34.7% / 38.9% |
| pass^4 / pass@4 | 33.3% / 38.9% |
| Outcome graders passing: state / answer / policy | 62.5% / 94.4% / 55.6% |
| Policy violation rate | 44.4% |
| Tool selection precision / recall | 88.1% / 76.9% |
| Args: schema-valid / real entities / correct | 84.5% / 77.6% / 76.0% |
| Efficiency: steps / reference steps; loop rate | 1.11; 6.9% |
| Fabricated entity rate | 19.4% |
| Fabricated action rate | 5.6% |
| Hallucination rate (response level, judge) | 36.1% |
| Claim-level unsupported / contradicted rate (135 claims) | 15.6% / 11.9% |
| Refusal explained (judge, refusal tasks) | 33.3% |
| Notional cost per successful task | $0.0169 |
| p95 latency per trial (model time) | 68.5 s |

| Category | Success |
|---|---|
| lookup | 50.0% |
| cancel | 50.0% |
| refund | 50.0% |
| address | 37.5% |
| multi | 0.0% |
| adversarial | 40.0% |

| Difficulty | Success |
|---|---|
| easy | 16.7% |
| medium | 79.2% |
| hard | 16.7% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 75.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 47.1% |
| issue_refund | 74.2% | 95.8% |
| list_orders | n/a | 0.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 66.7% | 100.0% |

| Policy rule broken | Trials |
|---|---|
| P1_verify_first | 4 |
| P2_own_orders | 1 |
| P3_read_before_write | 28 |
| P6_address_status | 2 |
| P7_refund_eligibility | 3 |
| P8_refund_amount | 10 |
| P9_no_double_refund | 5 |

## Examples to click through

- Failed trials: [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md), [T002/t2](traces/T002_t2.md)
- Policy violations: [T002/t0](traces/T002_t0.md), [T002/t3](traces/T002_t3.md), [T005/t0](traces/T005_t0.md)
- Fabricated entities: [T017/t0](traces/T017_t0.md), [T017/t1](traces/T017_t1.md), [T017/t3](traces/T017_t3.md)
- Fabricated actions: [T008/t1](traces/T008_t1.md), [T009/t3](traces/T009_t3.md), [T013/t2](traces/T013_t2.md)
- Hallucinated (judge): [T002/t0](traces/T002_t0.md), [T002/t1](traces/T002_t1.md), [T004/t2](traces/T004_t2.md)
- Looped: [T015/t0](traces/T015_t0.md), [T015/t2](traces/T015_t2.md), [T015/t3](traces/T015_t3.md)
