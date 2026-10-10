# Noise floor (M1)

Runs `v0-a` and `v0-b` use the same version, the same config and the same tasks. Only the sampling seed differs.

| Split | Flip rate | Success A | Success B |
|---|---|---|---|
| all | 10.5% | 43.5% | 44.0% |
| dev | 13.3% | 46.9% | 46.1% |
| holdout | 5.6% | 37.5% | 40.3% |

**Result:** identical runs disagree on 10.5% of (task, trial) outcomes, so a change smaller than 10.5 points is not real.
