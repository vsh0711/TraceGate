# Run report: v2-b

Version **v2** (guardrail). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 66.0% (54.0% to 76.5%) |
| pass^1 / pass@1 | 66.0% / 66.0% |
| pass^2 / pass@2 | 58.0% / 74.0% |
| pass^3 / pass@3 | 54.0% / 78.0% |
| pass^4 / pass@4 | 52.0% / 80.0% |
| Outcome graders passing: state / answer / policy | 72.5% / 93.5% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 88.6% / 83.3% |
| Args: schema-valid / real entities / correct | 87.1% / 81.6% / 87.0% |
| Efficiency: steps / reference steps; loop rate | 1.09; 0.0% |
| Guardrail blocks per trial | 0.72 |
| Fabricated entity rate | 12.0% |
| Fabricated action rate | 4.0% |
| Notional cost per successful task | $0.0094 |
| p95 latency per trial (model time) | 85.1 s |

| Category | Success |
|---|---|
| lookup | 35.0% |
| cancel | 53.6% |
| refund | 84.1% |
| address | 85.0% |
| multi | 28.6% |
| adversarial | 80.0% |

| Difficulty | Success |
|---|---|
| easy | 46.7% |
| medium | 85.0% |
| hard | 60.0% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 80.0% | 70.0% |
| get_customer | 98.0% | 100.0% |
| get_order | 100.0% | 73.4% |
| issue_refund | 57.9% | 84.6% |
| list_orders | 100.0% | 18.8% |
| transfer_to_human | 0.0% | n/a |
| update_address | 83.3% | 100.0% |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 71.9% (58.6% to 83.6%) |
| pass^1 / pass@1 | 71.9% / 71.9% |
| pass^2 / pass@2 | 63.5% / 80.2% |
| pass^3 / pass@3 | 58.6% / 83.6% |
| pass^4 / pass@4 | 56.2% / 84.4% |
| Outcome graders passing: state / answer / policy | 77.3% / 94.5% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 88.4% / 82.3% |
| Args: schema-valid / real entities / correct | 86.8% / 83.0% / 90.0% |
| Efficiency: steps / reference steps; loop rate | 1.10; 0.0% |
| Guardrail blocks per trial | 0.74 |
| Fabricated entity rate | 9.4% |
| Fabricated action rate | 4.7% |
| Notional cost per successful task | $0.0085 |
| p95 latency per trial (model time) | 90.4 s |

| Category | Success |
|---|---|
| lookup | 41.7% |
| cancel | 55.0% |
| refund | 85.7% |
| address | 83.3% |
| multi | 37.5% |
| adversarial | 90.0% |

| Difficulty | Success |
|---|---|
| easy | 50.0% |
| medium | 85.7% |
| hard | 72.2% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 68.2% | 75.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 100.0% | 69.2% |
| issue_refund | 51.0% | 89.3% |
| list_orders | 100.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 88.9% | 100.0% |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 55.6% (36.1% to 75.0%) |
| pass^1 / pass@1 | 55.6% / 55.6% |
| pass^2 / pass@2 | 48.1% / 63.0% |
| pass^3 / pass@3 | 45.8% / 68.1% |
| pass^4 / pass@4 | 44.4% / 72.2% |
| Outcome graders passing: state / answer / policy | 63.9% / 91.7% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 88.9% / 85.2% |
| Args: schema-valid / real entities / correct | 87.4% / 79.1% / 81.9% |
| Efficiency: steps / reference steps; loop rate | 1.07; 0.0% |
| Guardrail blocks per trial | 0.69 |
| Fabricated entity rate | 16.7% |
| Fabricated action rate | 2.8% |
| Notional cost per successful task | $0.0116 |
| p95 latency per trial (model time) | 84.5 s |

| Category | Success |
|---|---|
| lookup | 25.0% |
| cancel | 50.0% |
| refund | 81.2% |
| address | 87.5% |
| multi | 16.7% |
| adversarial | 60.0% |

| Difficulty | Success |
|---|---|
| easy | 41.7% |
| medium | 83.3% |
| hard | 41.7% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 100.0% | 65.0% |
| get_customer | 94.4% | 100.0% |
| get_order | 100.0% | 80.9% |
| issue_refund | 70.4% | 79.2% |
| list_orders | n/a | 0.0% |
| update_address | 66.7% | 100.0% |

## Examples to click through

- Failed trials: [T001/t2](traces/T001_t2.md), [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md)
- Policy violations: none
- Fabricated entities: [T013/t2](traces/T013_t2.md), [T013/t3](traces/T013_t3.md), [T017/t1](traces/T017_t1.md)
- Fabricated actions: [T008/t0](traces/T008_t0.md), [T009/t2](traces/T009_t2.md), [T014/t1](traces/T014_t1.md)
- Hallucinated (judge): none
- Looped: none
