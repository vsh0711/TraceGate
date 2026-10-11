# Run report: v5

Version **v5** (guardrail with remediation). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 55 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 72.5% (62.0% to 81.5%) |
| pass^1 / pass@1 | 72.5% / 72.5% |
| pass^2 / pass@2 | 62.3% / 82.7% |
| pass^3 / pass@3 | 57.0% / 87.5% |
| pass^4 / pass@4 | 54.0% / 90.0% |
| Outcome graders passing: state / answer / policy | 79.0% / 93.5% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 92.3% / 86.8% |
| Args: schema-valid / real entities / correct | 85.8% / 81.2% / 86.8% |
| Efficiency: steps / reference steps; loop rate | 1.17; 0.0% |
| Guardrail blocks per trial | 0.70 |
| Fabricated entity rate | 10.5% |
| Fabricated action rate | 3.0% |
| Hallucination rate (response level, judge) | 36.1% |
| Claim-level unsupported / contradicted rate (167 claims) | 6.6% / 14.4% |
| Refusal explained (judge, refusal tasks) | 16.7% |
| Notional cost per successful task | $0.0086 |
| p95 latency per trial (model time) | 89.5 s |

| Category | Success |
|---|---|
| lookup | 35.0% |
| cancel | 89.3% |
| refund | 90.9% |
| address | 85.0% |
| multi | 42.9% |
| adversarial | 73.3% |

| Difficulty | Success |
|---|---|
| easy | 65.0% |
| medium | 87.5% |
| hard | 60.0% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 88.6% | 77.5% |
| get_customer | 98.0% | 100.0% |
| get_order | 99.3% | 80.9% |
| issue_refund | 65.7% | 84.6% |
| list_orders | 100.0% | 18.8% |
| transfer_to_human | 0.0% | n/a |
| update_address | 90.0% | 90.0% |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 77.3% (66.4% to 87.5%) |
| pass^1 / pass@1 | 77.3% / 77.3% |
| pass^2 / pass@2 | 66.7% / 88.0% |
| pass^3 / pass@3 | 61.7% / 93.8% |
| pass^4 / pass@4 | 59.4% / 96.9% |
| Outcome graders passing: state / answer / policy | 82.8% / 94.5% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 93.6% / 87.5% |
| Args: schema-valid / real entities / correct | 85.6% / 82.9% / 88.7% |
| Efficiency: steps / reference steps; loop rate | 1.17; 0.0% |
| Guardrail blocks per trial | 0.65 |
| Fabricated entity rate | 8.6% |
| Fabricated action rate | 1.6% |
| Notional cost per successful task | $0.0078 |
| p95 latency per trial (model time) | 84.7 s |

| Category | Success |
|---|---|
| lookup | 41.7% |
| cancel | 85.0% |
| refund | 92.9% |
| address | 75.0% |
| multi | 56.2% |
| adversarial | 82.5% |

| Difficulty | Success |
|---|---|
| easy | 63.9% |
| medium | 89.3% |
| hard | 72.2% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 81.0% | 85.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 99.0% | 80.8% |
| issue_refund | 63.2% | 85.7% |
| list_orders | 100.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 93.3% | 87.5% |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 63.9% (44.4% to 81.9%) |
| pass^1 / pass@1 | 63.9% / 63.9% |
| pass^2 / pass@2 | 54.6% / 73.1% |
| pass^3 / pass@3 | 48.6% / 76.4% |
| pass^4 / pass@4 | 44.4% / 77.8% |
| Outcome graders passing: state / answer / policy | 72.2% / 91.7% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 89.9% / 85.6% |
| Args: schema-valid / real entities / correct | 86.0% / 78.5% / 83.6% |
| Efficiency: steps / reference steps; loop rate | 1.18; 0.0% |
| Guardrail blocks per trial | 0.81 |
| Fabricated entity rate | 13.9% |
| Fabricated action rate | 5.6% |
| Hallucination rate (response level, judge) | 36.1% |
| Claim-level unsupported / contradicted rate (167 claims) | 6.6% / 14.4% |
| Refusal explained (judge, refusal tasks) | 16.7% |
| Notional cost per successful task | $0.0104 |
| p95 latency per trial (model time) | 96.1 s |

| Category | Success |
|---|---|
| lookup | 25.0% |
| cancel | 100.0% |
| refund | 87.5% |
| address | 100.0% |
| multi | 25.0% |
| adversarial | 55.0% |

| Difficulty | Success |
|---|---|
| easy | 66.7% |
| medium | 83.3% |
| hard | 41.7% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 70.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 80.9% |
| issue_refund | 69.0% | 83.3% |
| list_orders | n/a | 0.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 80.0% | 100.0% |

## Examples to click through

- Failed trials: [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md), [T002/t2](traces/T002_t2.md)
- Policy violations: none
- Fabricated entities: [T009/t3](traces/T009_t3.md), [T017/t0](traces/T017_t0.md), [T017/t3](traces/T017_t3.md)
- Fabricated actions: [T029/t3](traces/T029_t3.md), [T031/t1](traces/T031_t1.md), [T031/t3](traces/T031_t3.md)
- Hallucinated (judge): [T003/t0](traces/T003_t0.md), [T016/t0](traces/T016_t0.md), [T019/t0](traces/T019_t0.md)
- Looped: none
