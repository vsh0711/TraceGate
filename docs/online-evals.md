# Online evals (M7)

Online evals score live traffic without an expected answer. We have no live users, so a simulated user makes the traffic.

## How it works

1. `online/simulate.py` plays a customer. An LLM gets a persona (polite, impatient, confused or pushy) and a goal (cancel, refund, change an address, or ask a status). It talks to the deployed agent (version v2). Each conversation is saved as a trace in `online/traces.jsonl`. The batch number stands for time.
2. `online/score.py` scores traces with **reference-free graders**. These graders need no expected result: fabricated entities, fabricated actions, the policy rules, tool errors, loops and (when the judge quota allows) the claim-level judge.
3. A trace with any problem goes to the review queue (`labels/review_queue.jsonl`). `python -m evals.triage online` labels it with a failure category.
4. `online/dashboard.py` builds `online/dashboard.html` (metrics for each batch) and raises an alert when a metric passes its threshold.

## Setup of this run

- 90 conversations in 9 batches of 10. The deployed agent is v2, with the guardrail.
- Batches 1 to 4: healthy.
- Batches 5 to 7: **degraded tool descriptions** (the agent is told that `get_customer` and `get_order` are usually not needed).
- Batches 8 and 9: **guardrail switched off** (the v0 configuration is served, as after a bad deploy).
- Alert rules, set from the healthy batches: the code-check hallucination rate (a fabricated entity or a fabricated action) above 25%. The healthy batches reach at most 20%. A policy violation rate above 10%. The healthy batches all have 0%.
- The judge was not used online in this run. The free API quota was kept for the offline holdout runs.

## Results

| Batch | Change | Hallucination (code) | Policy violations | Tool errors | Loops | Traces flagged |
|---|---|---|---|---|---|---|
| 1 to 4 | none | 0%, 10%, 0%, 20% | 0% | 50% to 70% | 10% to 50% | 10% to 60% |
| 5 to 7 | degraded descriptions | 10%, 10%, 0% | 0% | 40% to 80% | 0% to 30% | 10% to 30% |
| 8 | guardrail off | 20% | **90%** | 70% | 10% | 100% |
| 9 | guardrail off | **40%** | **70%** | 100% | 20% | 70% |

- Hallucination alert: fires in batch 9 only. Batch 8 is at 20%, the same as the healthy maximum.
- Policy alert: fires in batches 8 and 9.
- Review queue: 35 traces. 17 come from batches 8 and 9. All 10 traces of batch 8 are in it.

## What we learned

1. **The degraded tool description was not detectable.** It changed nothing: the metrics and the guardrail block rate (1.1 to 1.8 blocks per trace) are the same as in the healthy batches. The 3B agent hardly reads tool descriptions. Offline, version v1 (richer descriptions) showed the same. This is a true negative result, not a failure of the monitor.
2. **The guardrail hides some damage.** With the guardrail on, the agent cannot break the policy, so policy metrics stay at 0% even when the agent behaves worse. A monitor must also watch the guardrail itself (blocks per trace) and the tool error rate.
3. **Removing the guardrail is detected.** The policy violation rate goes from 0% to 70% to 90% at once. This signal is much stronger than the hallucination rate. The hallucination alert is late: it fires one batch after the policy alert.
4. **Healthy traffic is noisy.** The tool error rate is 50% to 70% and loops reach 50% in healthy batches. These two metrics need a longer history before they can carry an alert.

## Limits

- Batches have 10 traces. One trace changes a rate by 10 points. The alert thresholds are therefore rough.
- The simulated user is a 3B model. It sometimes withholds identity details on purpose or by accident. This adds tool errors that real customers might not cause.
- The regression was made by us, so the test shows that the monitor can see a large regression. It does not show that it can see a small one.
- Hallucination here means the code checks only. The claim-level judge on online traces was not run (quota).
