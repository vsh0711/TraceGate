# Run diff: v2 -> v4

Noise floor (flip rate of identical runs): 14.0%

## dev

- Success: 67.2% -> 67.2%; change +0.0 pts (paired bootstrap 95% CI -2.3 to +2.3)
- pass^4 change: +0.0 pts (CI +0.0 to +0.0)
- McNemar (per-task majority): only A passes 0, only B passes 1, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0088 -> $0.0094

| Category | A | B | Change |
|---|---|---|---|
| address | 83.3% | 83.3% | +0.0 |
| adversarial | 87.5% | 87.5% | +0.0 |
| cancel | 50.0% | 50.0% | +0.0 |
| lookup | 41.7% | 33.3% | -8.3 |
| multi | 25.0% | 25.0% | +0.0 |
| refund | 78.6% | 82.1% | +3.6 |

## holdout

- Success: 50.0% -> 51.4%; change +1.4 pts (paired bootstrap 95% CI +0.0 to +4.2)
- pass^4 change: +5.6 pts (CI +0.0 to +16.7)
- McNemar (per-task majority): only A passes 0, only B passes 0, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): 51.4% -> 45.8%
- Cost per success (notional): $0.0127 -> $0.0130

| Category | A | B | Change |
|---|---|---|---|
| address | 75.0% | 75.0% | +0.0 |
| adversarial | 50.0% | 50.0% | +0.0 |
| cancel | 50.0% | 50.0% | +0.0 |
| lookup | 25.0% | 25.0% | +0.0 |
| multi | 0.0% | 0.0% | +0.0 |
| refund | 87.5% | 93.8% | +6.2 |

## all

- Success: 61.0% -> 61.5%; change +0.5 pts (paired bootstrap 95% CI -1.0 to +2.5)
- pass^4 change: +2.0 pts (CI +0.0 to +6.0)
- McNemar (per-task majority): only A passes 0, only B passes 1, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): 51.4% -> 45.8%
- Cost per success (notional): $0.0099 -> $0.0105

| Category | A | B | Change |
|---|---|---|---|
| address | 80.0% | 80.0% | +0.0 |
| adversarial | 75.0% | 75.0% | +0.0 |
| cancel | 50.0% | 50.0% | +0.0 |
| lookup | 35.0% | 30.0% | -5.0 |
| multi | 14.3% | 14.3% | +0.0 |
| refund | 81.8% | 86.4% | +4.5 |

