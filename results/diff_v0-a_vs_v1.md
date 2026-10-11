# Run diff: v0-a -> v1

Noise floor (flip rate of identical runs): 14.0%

## dev

- Success: 46.9% -> 45.3%; change -1.6 pts (paired bootstrap 95% CI -9.4 to +7.0)
- pass^4 change: +0.0 pts (CI -12.5 to +12.5)
- McNemar (per-task majority): only A passes 2, only B passes 1, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0111 -> $0.0138

| Category | A | B | Change |
|---|---|---|---|
| address | 33.3% | 16.7% | -16.7 |
| adversarial | 65.0% | 67.5% | +2.5 |
| cancel | 40.0% | 35.0% | -5.0 |
| lookup | 41.7% | 41.7% | +0.0 |
| multi | 25.0% | 25.0% | +0.0 |
| refund | 46.4% | 46.4% | +0.0 |

## holdout

- Success: 34.7% -> 34.7%; change +0.0 pts (paired bootstrap 95% CI -4.2 to +4.2)
- pass^4 change: +0.0 pts (CI +0.0 to +0.0)
- McNemar (per-task majority): only A passes 1, only B passes 0, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): 47.2% -> 45.8%
- Cost per success (notional): $0.0163 -> $0.0194

| Category | A | B | Change |
|---|---|---|---|
| address | 37.5% | 37.5% | +0.0 |
| adversarial | 40.0% | 40.0% | +0.0 |
| cancel | 50.0% | 50.0% | +0.0 |
| lookup | 25.0% | 25.0% | +0.0 |
| multi | 0.0% | 0.0% | +0.0 |
| refund | 50.0% | 50.0% | +0.0 |

## all

- Success: 42.5% -> 41.5%; change -1.0 pts (paired bootstrap 95% CI -6.5 to +5.0)
- pass^4 change: +0.0 pts (CI -8.0 to +8.0)
- McNemar (per-task majority): only A passes 3, only B passes 1, p = 0.625
- Change is NOT above the noise floor
- Hallucination rate (judge): 47.2% -> 45.8%
- Cost per success (notional): $0.0127 -> $0.0155

| Category | A | B | Change |
|---|---|---|---|
| address | 35.0% | 25.0% | -10.0 |
| adversarial | 56.7% | 58.3% | +1.7 |
| cancel | 42.9% | 39.3% | -3.6 |
| lookup | 35.0% | 35.0% | +0.0 |
| multi | 14.3% | 14.3% | +0.0 |
| refund | 47.7% | 47.7% | +0.0 |

