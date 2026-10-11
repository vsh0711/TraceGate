# Gate: when a candidate version becomes the new version

A candidate version passes the gate only if all 4 checks pass. The command is `python -m evals.gate <baseline_run> <candidate_run>`.

| Check | Rule |
|---|---|
| Dev gain above noise | Dev success rises by more than the flip rate (the noise floor from M1). |
| Dev gain significant | The 95% paired-bootstrap interval of the dev gain has a lower bound above 0. Tasks are resampled, not trials. |
| Holdout gain above noise | Holdout success rises by more than the flip rate. |
| No category regresses | No category loses more than 10 points on dev or on holdout (`CATEGORY_REGRESSION_LIMIT` in `config.py`). |

The report also shows the McNemar test and the pass^k change.

## Gate for a fix that targets hallucination

Some fixes aim at the hallucination rate, not at success. Success does not include hallucination, so the success gate cannot see their effect. For such a fix we declare the target **before** the run, and we use this gate: `python -m evals.gate <baseline_run> <candidate_run> --target-hallucination`. The candidate passes only if all 4 checks pass.

| Check | Rule |
|---|---|
| Hallucination falls | The judged hallucination rate on the **holdout** falls, and the 95% paired-bootstrap interval of the change has an upper bound below 0. Tasks are resampled. |
| Dev success holds | Dev success does not fall by more than the flip rate. |
| Holdout success holds | Holdout success does not fall by more than the flip rate. |
| No category regresses | No category loses more than 10 points on dev or on holdout. |

The judge is independent from the code checks that the fix may use. For this reason the test uses the judge. The judge is not yet validated against human labels (M4), so a pass here is provisional until `docs/judge-validation.md` states the agreement.

## Why the checks differ for dev and holdout

The holdout has few tasks (18). A significance test on 18 tasks has little power. For this reason the significance check uses dev, and the holdout must show a gain above noise. The report always shows the holdout interval, so you can see how wide it is.

## Leakage rule

Nothing that comes from the holdout may be used to make a fix. This covers prompts, exemplars, optimizer data and judge prompts. The code enforces the rule:

- `evals/tasks.py` stores a hash of the holdout tasks. The loader stops if the holdout changes.
- `require_dev()` stops error analysis, labeling and exemplar memory when they receive holdout data.
- Failure traces are read for dev trials only.
- The gate reads the holdout as numbers only. If a candidate fails on the holdout, do not read holdout traces. Go back to the dev data to make a new fix.
