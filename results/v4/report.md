# Run report: v4

Version **v4** (answer validator). Model `ollama_chat/llama3.2:3b`, temperature 0.5, 4 trials per task, 50 tasks. Dataset v1. Cost is a notional price (see config.py), not a real invoice.

## Split: all (50 tasks, 200 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 61.5% (49.0% to 72.5%) |
| pass^1 / pass@1 | 61.5% / 61.5% |
| pass^2 / pass@2 | 54.0% / 69.0% |
| pass^3 / pass@3 | 49.0% / 71.5% |
| pass^4 / pass@4 | 46.0% / 72.0% |
| Outcome graders passing: state / answer / policy | 68.5% / 93.0% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 90.7% / 83.5% |
| Args: schema-valid / real entities / correct | 83.4% / 78.5% / 86.2% |
| Efficiency: steps / reference steps; loop rate | 1.11; 2.5% |
| Guardrail blocks per trial | 0.81 |
| Fabricated entity rate | 11.0% |
| Fabricated action rate | 1.0% |
| Hallucination rate (response level, judge) | 45.8% |
| Claim-level unsupported / contradicted rate (152 claims) | 15.8% / 17.1% |
| Refusal explained (judge, refusal tasks) | 16.7% |
| Notional cost per successful task | $0.0105 |
| p95 latency per trial (model time) | 96.6 s |

| Category | Success |
|---|---|
| lookup | 30.0% |
| cancel | 50.0% |
| refund | 86.4% |
| address | 80.0% |
| multi | 14.3% |
| adversarial | 75.0% |

| Difficulty | Success |
|---|---|
| easy | 45.0% |
| medium | 83.8% |
| hard | 48.3% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 87.5% | 70.0% |
| get_customer | 98.0% | 100.0% |
| get_order | 99.3% | 73.9% |
| issue_refund | 60.0% | 86.5% |
| list_orders | 100.0% | 18.8% |
| transfer_to_human | 0.0% | n/a |
| update_address | 90.0% | 90.0% |

## Split: dev (32 tasks, 128 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 67.2% (52.3% to 80.5%) |
| pass^1 / pass@1 | 67.2% / 67.2% |
| pass^2 / pass@2 | 59.4% / 75.0% |
| pass^3 / pass@3 | 53.9% / 77.3% |
| pass^4 / pass@4 | 50.0% / 78.1% |
| Outcome graders passing: state / answer / policy | 73.4% / 93.8% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 92.2% / 84.9% |
| Args: schema-valid / real entities / correct | 82.6% / 79.7% / 88.7% |
| Efficiency: steps / reference steps; loop rate | 1.13; 3.9% |
| Guardrail blocks per trial | 0.76 |
| Fabricated entity rate | 8.6% |
| Fabricated action rate | 0.8% |
| Notional cost per successful task | $0.0094 |
| p95 latency per trial (model time) | 95.7 s |

| Category | Success |
|---|---|
| lookup | 33.3% |
| cancel | 50.0% |
| refund | 82.1% |
| address | 83.3% |
| multi | 25.0% |
| adversarial | 87.5% |

| Difficulty | Success |
|---|---|
| easy | 44.4% |
| medium | 83.9% |
| hard | 63.9% |

| Tool | Precision | Recall |
|---|---|---|
| cancel_order | 78.9% | 75.0% |
| get_customer | 100.0% | 100.0% |
| get_order | 98.9% | 75.0% |
| issue_refund | 57.8% | 92.9% |
| list_orders | 100.0% | 25.0% |
| transfer_to_human | 0.0% | n/a |
| update_address | 93.3% | 87.5% |

## Split: holdout (18 tasks, 72 trials)

| Metric | Value |
|---|---|
| Success rate (95% CI, bootstrap over tasks) | 51.4% (30.6% to 72.2%) |
| pass^1 / pass@1 | 51.4% / 51.4% |
| pass^2 / pass@2 | 44.4% / 58.3% |
| pass^3 / pass@3 | 40.3% / 61.1% |
| pass^4 / pass@4 | 38.9% / 61.1% |
| Outcome graders passing: state / answer / policy | 59.7% / 91.7% / 100.0% |
| Policy violation rate | 0.0% |
| Tool selection precision / recall | 88.1% / 81.1% |
| Args: schema-valid / real entities / correct | 84.8% / 76.5% / 81.7% |
| Efficiency: steps / reference steps; loop rate | 1.07; 0.0% |
| Guardrail blocks per trial | 0.89 |
| Fabricated entity rate | 15.3% |
| Fabricated action rate | 1.4% |
| Hallucination rate (response level, judge) | 45.8% |
| Claim-level unsupported / contradicted rate (152 claims) | 15.8% / 17.1% |
| Refusal explained (judge, refusal tasks) | 16.7% |
| Notional cost per successful task | $0.0130 |
| p95 latency per trial (model time) | 99.7 s |

| Category | Success |
|---|---|
| lookup | 25.0% |
| cancel | 50.0% |
| refund | 93.8% |
| address | 75.0% |
| multi | 0.0% |
| adversarial | 50.0% |

| Difficulty | Success |
|---|---|
| easy | 45.8% |
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

- Failed trials: [T001/t3](traces/T001_t3.md), [T002/t0](traces/T002_t0.md), [T002/t1](traces/T002_t1.md)
- Policy violations: none
- Fabricated entities: [T016/t3](traces/T016_t3.md), [T017/t0](traces/T017_t0.md), [T017/t3](traces/T017_t3.md)
- Fabricated actions: [T008/t1](traces/T008_t1.md), [T009/t3](traces/T009_t3.md)
- Hallucinated (judge): [T003/t0](traces/T003_t0.md), [T008/t2](traces/T008_t2.md), [T008/t3](traces/T008_t3.md)
- Looped: [T014/t1](traces/T014_t1.md), [T014/t3](traces/T014_t3.md), [T015/t3](traces/T015_t3.md)
