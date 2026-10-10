# Noise floor (M1)

Runs `v0-a` and `v0-b` use the same version, the same config and the same tasks. Only the sampling seed differs.

| Split | Flip rate | Success A | Success B |
|---|---|---|---|
| all | 14.0% | 42.5% | 44.5% |
| dev | 14.8% | 46.9% | 46.1% |
| holdout | 12.5% | 34.7% | 41.7% |

**Result:** identical runs disagree on 14.0% of (task, trial) outcomes, so a change smaller than 14.0 points is not real.
