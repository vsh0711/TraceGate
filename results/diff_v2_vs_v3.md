# Run diff: v2 -> v3

Noise floor (flip rate of identical runs): 14.0%

## dev

- Success: 67.2% -> 64.8%; change -2.3 pts (paired bootstrap 95% CI -14.1 to +8.6)
- pass^4 change: +3.1 pts (CI -9.4 to +15.6)
- McNemar (per-task majority): only A passes 4, only B passes 3, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0088 -> $0.0127

| Category | A | B | Change |
|---|---|---|---|
| address | 83.3% | 58.3% | -25.0 |
| adversarial | 87.5% | 85.0% | -2.5 |
| cancel | 50.0% | 65.0% | +15.0 |
| lookup | 41.7% | 8.3% | -33.3 |
| multi | 25.0% | 50.0% | +25.0 |
| refund | 78.6% | 71.4% | -7.1 |

## holdout

- Success: 50.0% -> 52.8%; change +2.8 pts (paired bootstrap 95% CI -9.7 to +15.3)
- pass^4 change: +11.1 pts (CI +0.0 to +27.8)
- McNemar (per-task majority): only A passes 1, only B passes 2, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0127 -> $0.0174

| Category | A | B | Change |
|---|---|---|---|
| address | 75.0% | 100.0% | +25.0 |
| adversarial | 50.0% | 60.0% | +10.0 |
| cancel | 50.0% | 50.0% | +0.0 |
| lookup | 25.0% | 0.0% | -25.0 |
| multi | 0.0% | 0.0% | +0.0 |
| refund | 87.5% | 87.5% | +0.0 |

## all

- Success: 61.0% -> 60.5%; change -0.5 pts (paired bootstrap 95% CI -9.0 to +8.0)
- pass^4 change: +6.0 pts (CI -4.0 to +16.0)
- McNemar (per-task majority): only A passes 5, only B passes 5, p = 1.000
- Change is NOT above the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0099 -> $0.0142

| Category | A | B | Change |
|---|---|---|---|
| address | 80.0% | 75.0% | -5.0 |
| adversarial | 75.0% | 76.7% | +1.7 |
| cancel | 50.0% | 60.7% | +10.7 |
| lookup | 35.0% | 5.0% | -30.0 |
| multi | 14.3% | 28.6% | +14.3 |
| refund | 81.8% | 77.3% | -4.5 |

