# Run report: v2

Version **v2** (guardrail). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 61.0% (49.0% to 72.0%) |
| pass^1 / pass@1 | 61.0% / 61.0% |
| pass^2 / pass@2 | 52.3% / 69.7% |
| pass^3 / pass@3 | 47.0% / 73.0% |
| pass^4 / pass@4 | 44.0% / 74.0% |
| Outcome graders passing: state / answer / policy | 67.5% / 93.5% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 91.0% / 83.5% |
| Args: schema-valid / real entities / correct | 85.8% / 80.7% / 85.7% |
| Efficiency: steps / reference steps; loop rate | 1.06; 0.0% |
| Guardrail blocks per trial | 0.70 |
| Fabricated entity rate | 13.0% |
| Fabricated action rate | 2.0% |
| Hallucination rate (response level, judge) | 52.8% |
| Claim-level unsupported / contradicted rate (150 claims) | 20.0% / 14.0% |
| Refusal explained (judge, refusal tasks) | 37.5% |
| Notional cost per successful task | $0.0099 |
| p95 latency per trial (model time) | 79.0 s |

| Category | Success |
|---|---|
| lookup | 35.0% |
| cancel | 50.0% |
| refund | 81.8% |
| address | 80.0% |
| multi | 14.3% |
| adversarial | 75.0% |

| Difficulty | Success |
|---|---|
| easy | 45.0% |
| medium | 82.5% |
| hard | 48.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 87.5% | 70.0% |
| get_customer | 98.0% | 100.0% |
| get_order | 99.3% | 73.9% |
| issue_refund | 61.6% | 86.5% |
| list_orders | 100.0% | 18.8% |
| transfer_to_human | 0.0% | n/a |
| update_address | 90.0% | 90.0% |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 67.2% (53.1% to 79.7%) |
| pass^1 / pass@1 | 67.2% / 67.2% |
| pass^2 / pass@2 | 58.3% / 76.0% |
| pass^3 / pass@3 | 53.1% / 79.7% |
| pass^4 / pass@4 | 50.0% / 81.2% |
| Outcome graders passing: state / answer / policy | 72.7% / 94.5% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 92.7% / 84.9% |
| Args: schema-valid / real entities / correct | 85.4% / 82.3% / 88.2% |
| Efficiency: steps / reference steps; loop rate | 1.08; 0.0% |
| Guardrail blocks per trial | 0.63 |
| Fabricated entity rate | 8.6% |
| Fabricated action rate | 1.6% |
| Notional cost per successful task | $0.0088 |
| p95 latency per trial (model time) | 75.8 s |

| Category | Success |
|---|---|
| lookup | 41.7% |
| cancel | 50.0% |
| refund | 78.6% |
| address | 83.3% |
| multi | 25.0% |
| adversarial | 87.5% |

| Difficulty | Success |
|---|---|
| easy | 47.2% |
| medium | 82.1% |
| hard | 63.9% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 78.9% | 75.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 98.9% | 75.0% |
| issue_refund | 60.5% | 92.9% |
| list_orders | 100.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 93.3% | 87.5% |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 50.0% (30.6% to 69.4%) |
| pass^1 / pass@1 | 50.0% / 50.0% |
| pass^2 / pass@2 | 41.7% / 58.3% |
| pass^3 / pass@3 | 36.1% / 61.1% |
| pass^4 / pass@4 | 33.3% / 61.1% |
| Outcome graders passing: state / answer / policy | 58.3% / 91.7% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 88.1% / 81.1% |
| Args: schema-valid / real entities / correct | 86.7% / 78.1% / 81.2% |
| Efficiency: steps / reference steps; loop rate | 1.04; 0.0% |
| Guardrail blocks per trial | 0.82 |
| Fabricated entity rate | 20.8% |
| Fabricated action rate | 2.8% |
| Hallucination rate (response level, judge) | 52.8% |
| Claim-level unsupported / contradicted rate (150 claims) | 20.0% / 14.0% |
| Refusal explained (judge, refusal tasks) | 37.5% |
| Notional cost per successful task | $0.0127 |
| p95 latency per trial (model time) | 86.9 s |

| Category | Success |
|---|---|
| lookup | 25.0% |
| cancel | 50.0% |
| refund | 87.5% |
| address | 75.0% |
| multi | 0.0% |
| adversarial | 50.0% |

| Difficulty | Success |
|---|---|
| easy | 41.7% |
| medium | 83.3% |
| hard | 25.0% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 65.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 72.1% |
| issue_refund | 63.3% | 79.2% |
| list_orders | n/a | 0.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 80.0% | 100.0% |

## Examples to click through

- Failed trials: [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md), [T002/t2](traces/T002_t2.md)
- Policy violations: none
- Fabricated entities: [T016/t3](traces/T016_t3.md), [T017/t0](traces/T017_t0.md), [T017/t3](traces/T017_t3.md)
- Fabricated actions: [T017/t3](traces/T017_t3.md), [T029/t1](traces/T029_t1.md), [T031/t0](traces/T031_t0.md)
- Hallucinated (judge): [T003/t0](traces/T003_t0.md), [T003/t1](traces/T003_t1.md), [T003/t2](traces/T003_t2.md)
- Looped: none
