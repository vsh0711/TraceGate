# Run report: v3

Version **v3** (exemplar memory). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 60.5% (48.0% to 72.5%) |
| pass^1 / pass@1 | 60.5% / 60.5% |
| pass^2 / pass@2 | 54.3% / 66.7% |
| pass^3 / pass@3 | 51.5% / 70.0% |
| pass^4 / pass@4 | 50.0% / 72.0% |
| Outcome graders passing: state / answer / policy | 70.5% / 90.0% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 94.2% / 86.6% |
| Args: schema-valid / real entities / correct | 92.8% / 89.9% / 90.8% |
| Efficiency: steps / reference steps; loop rate | 1.14; 5.5% |
| Guardrail blocks per trial | 0.45 |
| Fabricated entity rate | 11.5% |
| Fabricated action rate | 4.5% |
| Notional cost per successful task | $0.0142 |
| p95 latency per trial (model time) | 118.3 s |

| Category | Success |
|---|---|
| lookup | 5.0% |
| cancel | 60.7% |
| refund | 77.3% |
| address | 75.0% |
| multi | 28.6% |
| adversarial | 76.7% |

| Difficulty | Success |
|---|---|
| easy | 31.7% |
| medium | 83.8% |
| hard | 58.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 85.3% | 72.5% |
| get_customer | 98.0% | 100.0% |
| get_order | 100.0% | 81.9% |
| issue_refund | 82.6% | 73.1% |
| list_orders | 100.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 100.0% | 95.0% |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 64.8% (50.0% to 78.9%) |
| pass^1 / pass@1 | 64.8% / 64.8% |
| pass^2 / pass@2 | 57.8% / 71.9% |
| pass^3 / pass@3 | 54.7% / 75.8% |
| pass^4 / pass@4 | 53.1% / 78.1% |
| Outcome graders passing: state / answer / policy | 74.2% / 90.6% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 95.1% / 85.2% |
| Args: schema-valid / real entities / correct | 92.7% / 89.7% / 91.2% |
| Efficiency: steps / reference steps; loop rate | 1.12; 1.6% |
| Guardrail blocks per trial | 0.43 |
| Fabricated entity rate | 7.0% |
| Fabricated action rate | 3.1% |
| Notional cost per successful task | $0.0127 |
| p95 latency per trial (model time) | 103.3 s |

| Category | Success |
|---|---|
| lookup | 8.3% |
| cancel | 65.0% |
| refund | 71.4% |
| address | 58.3% |
| multi | 50.0% |
| adversarial | 85.0% |

| Difficulty | Success |
|---|---|
| easy | 25.0% |
| medium | 83.9% |
| hard | 75.0% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 75.0% | 75.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 100.0% | 78.3% |
| issue_refund | 80.0% | 71.4% |
| list_orders | 100.0% | 33.3% |
| transfer_to_human | 0.0% | n/a |
| update_address | 100.0% | 93.8% |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 52.8% (31.9% to 73.6%) |
| pass^1 / pass@1 | 52.8% / 52.8% |
| pass^2 / pass@2 | 48.1% / 57.4% |
| pass^3 / pass@3 | 45.8% / 59.7% |
| pass^4 / pass@4 | 44.4% / 61.1% |
| Outcome graders passing: state / answer / policy | 63.9% / 88.9% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 92.6% / 89.1% |
| Args: schema-valid / real entities / correct | 93.0% / 90.4% / 90.1% |
| Efficiency: steps / reference steps; loop rate | 1.19; 12.5% |
| Guardrail blocks per trial | 0.49 |
| Fabricated entity rate | 19.4% |
| Fabricated action rate | 6.9% |
| Notional cost per successful task | $0.0174 |
| p95 latency per trial (model time) | 122.5 s |

| Category | Success |
|---|---|
| lookup | 0.0% |
| cancel | 50.0% |
| refund | 87.5% |
| address | 100.0% |
| multi | 0.0% |
| adversarial | 60.0% |

| Difficulty | Success |
|---|---|
| easy | 41.7% |
| medium | 83.3% |
| hard | 33.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 70.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 88.2% |
| issue_refund | 85.7% | 75.0% |
| list_orders | n/a | 0.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 100.0% | 100.0% |

## Examples to click through

- Failed trials: [T001/t0](traces/T001_t0.md), [T001/t1](traces/T001_t1.md), [T001/t2](traces/T001_t2.md)
- Policy violations: none
- Fabricated entities: [T003/t0](traces/T003_t0.md), [T003/t1](traces/T003_t1.md), [T017/t3](traces/T017_t3.md)
- Fabricated actions: [T013/t2](traces/T013_t2.md), [T029/t1](traces/T029_t1.md), [T029/t2](traces/T029_t2.md)
- Hallucinated (judge): none
- Looped: [T013/t2](traces/T013_t2.md), [T014/t1](traces/T014_t1.md), [T029/t0](traces/T029_t0.md)
