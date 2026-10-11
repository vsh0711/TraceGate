# Run report: v5-b

Version **v5** (guardrail with remediation). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 73.5% (62.5% to 82.5%) |
| pass^1 / pass@1 | 73.5% / 73.5% |
| pass^2 / pass@2 | 64.3% / 82.7% |
| pass^3 / pass@3 | 57.5% / 85.0% |
| pass^4 / pass@4 | 52.0% / 86.0% |
| Outcome graders passing: state / answer / policy | 80.5% / 93.0% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 90.4% / 89.9% |
| Args: schema-valid / real entities / correct | 85.6% / 80.7% / 87.9% |
| Efficiency: steps / reference steps; loop rate | 1.21; 2.0% |
| Guardrail blocks per trial | 0.75 |
| Fabricated entity rate | 11.5% |
| Fabricated action rate | 4.5% |
| Notional cost per successful task | $0.0085 |
| p95 latency per trial (model time) | 87.7 s |

| Category | Success |
|---|---|
| lookup | 35.0% |
| cancel | 85.7% |
| refund | 88.6% |
| address | 95.0% |
| multi | 39.3% |
| adversarial | 78.3% |

| Difficulty | Success |
|---|---|
| easy | 65.0% |
| medium | 87.5% |
| hard | 63.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 81.1% | 75.0% |
| get_customer | 98.0% | 100.0% |
| get_order | 100.0% | 86.2% |
| issue_refund | 58.8% | 90.4% |
| list_orders | 100.0% | 18.8% |
| transfer_to_human | 0.0% | n/a |
| update_address | 83.3% | 100.0% |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 81.2% (70.3% to 90.6%) |
| pass^1 / pass@1 | 81.2% / 81.2% |
| pass^2 / pass@2 | 72.9% / 89.6% |
| pass^3 / pass@3 | 65.6% / 90.6% |
| pass^4 / pass@4 | 59.4% / 90.6% |
| Outcome graders passing: state / answer / policy | 87.5% / 93.8% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 90.6% / 90.0% |
| Args: schema-valid / real entities / correct | 85.2% / 81.8% / 90.8% |
| Efficiency: steps / reference steps; loop rate | 1.24; 2.3% |
| Guardrail blocks per trial | 0.77 |
| Fabricated entity rate | 9.4% |
| Fabricated action rate | 5.5% |
| Notional cost per successful task | $0.0076 |
| p95 latency per trial (model time) | 87.8 s |

| Category | Success |
|---|---|
| lookup | 41.7% |
| cancel | 85.0% |
| refund | 92.9% |
| address | 100.0% |
| multi | 56.2% |
| adversarial | 87.5% |

| Difficulty | Success |
|---|---|
| easy | 72.2% |
| medium | 89.3% |
| hard | 77.8% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 69.6% | 80.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 100.0% | 85.0% |
| issue_refund | 51.0% | 92.9% |
| list_orders | 100.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 88.9% | 100.0% |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 59.7% (40.3% to 76.4%) |
| pass^1 / pass@1 | 59.7% / 59.7% |
| pass^2 / pass@2 | 49.1% / 70.4% |
| pass^3 / pass@3 | 43.1% / 75.0% |
| pass^4 / pass@4 | 38.9% / 77.8% |
| Outcome graders passing: state / answer / policy | 68.1% / 91.7% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 90.2% / 89.8% |
| Args: schema-valid / real entities / correct | 86.4% / 78.7% / 82.7% |
| Efficiency: steps / reference steps; loop rate | 1.15; 1.4% |
| Guardrail blocks per trial | 0.72 |
| Fabricated entity rate | 15.3% |
| Fabricated action rate | 2.8% |
| Notional cost per successful task | $0.0105 |
| p95 latency per trial (model time) | 86.5 s |

| Category | Success |
|---|---|
| lookup | 25.0% |
| cancel | 87.5% |
| refund | 81.2% |
| address | 87.5% |
| multi | 16.7% |
| adversarial | 60.0% |

| Difficulty | Success |
|---|---|
| easy | 54.2% |
| medium | 83.3% |
| hard | 41.7% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 70.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 88.2% |
| issue_refund | 72.4% | 87.5% |
| list_orders | n/a | 0.0% |
| update_address | 66.7% | 100.0% |

## Examples to click through

- Failed trials: [T001/t2](traces/T001_t2.md), [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md)
- Policy violations: none
- Fabricated entities: [T013/t2](traces/T013_t2.md), [T017/t1](traces/T017_t1.md), [T017/t2](traces/T017_t2.md)
- Fabricated actions: [T006/t0](traces/T006_t0.md), [T006/t3](traces/T006_t3.md), [T009/t0](traces/T009_t0.md)
- Hallucinated (judge): none
- Looped: [T014/t0](traces/T014_t0.md), [T014/t2](traces/T014_t2.md), [T033/t2](traces/T033_t2.md)
