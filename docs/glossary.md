# Glossary

| Term | Meaning |
|---|---|
| Agent | The support agent. It is a loop: model call, tool calls, tool results, repeat. |
| Task | One test case in `evals/tasks.jsonl`. It has an `id`, `input`, `expected` result, `tags` and `split`. |
| Trial | One run of one task. Each task has 4 trials in a normal run. |
| Trajectory | The full log of one trial: messages, tool calls with arguments, tool outputs, tokens, latency and cost. |
| Run | All trials of one agent version on a set of tasks. A run is saved in `results/<run_id>/`. |
| Version | One state of the agent: prompt, tool descriptions, guardrail and memory. Names: v0, v1, v2, v3. |
| Dataset version | One state of the task file. Names: v1, v2. A new dataset version adds dev tasks only. |
| Split | `dev` or `holdout`. |
| Dev split | Tasks that you may read and use to make fixes. |
| Holdout split | Tasks that are frozen. You must not use them to write prompts, pick exemplars, or tune the judge. |
| Outcome grader | A code grader that decides success: final database state, answer checks, policy rules. |
| Success | A trial where all outcome graders pass. |
| pass^k | The chance that all k sampled trials of a task succeed. It measures reliability. |
| pass@k | The chance that at least one of k sampled trials of a task succeeds. It measures potential. |
| Flip rate | The share of (task, trial) outcomes that change between two identical runs. It is the noise floor. |
| Judge | An LLM that grades what code cannot check. It gives a binary result and a short reason. |
| Claim | One atomic factual statement in the final answer of the agent. |
| Hallucination | A claim with the label `unsupported` or `contradicted`, a fabricated entity, or a fabricated action. See `docs/hallucination.md`. |
| Gate | The check that a candidate version must pass before it becomes the new version. See `docs/gate.md`. |
| Notional cost | A cost computed with a fixed price per token. The local model has no real cost. |
