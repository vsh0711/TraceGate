# Run diff: v2-pool -> v5-pool

Noise floor (flip rate of identical runs): 14.0%

## dev

- Success: 69.5% -> 79.3%; change +9.8 pts (paired bootstrap 95% CI +3.1 to +17.2)
- pass^8 change: +0.0 pts (CI -9.4 to +9.4)
- McNemar (per-task majority): only A passes 0, only B passes 5, p = 0.062
- Change is NOT above the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0086 -> $0.0077

| Category | A | B | Change |
|---|---|---|---|
| address | 83.3% | 87.5% | +4.2 |
| adversarial | 88.8% | 85.0% | -3.7 |
| cancel | 52.5% | 85.0% | +32.5 |
| lookup | 41.7% | 41.7% | +0.0 |
| multi | 31.2% | 56.2% | +25.0 |
| refund | 82.1% | 92.9% | +10.7 |

## holdout

- Success: 52.8% -> 61.8%; change +9.0 pts (paired bootstrap 95% CI +1.4 to +20.1)
- pass^8 change: +0.0 pts (CI +0.0 to +0.0)
- McNemar (per-task majority): only A passes 0, only B passes 2, p = 0.500
- Change is NOT above the noise floor
- Hallucination rate (judge): 51.4% -> 36.1%
- Cost per success (notional): $0.0121 -> $0.0105

| Category | A | B | Change |
|---|---|---|---|
| address | 81.2% | 93.8% | +12.5 |
| adversarial | 55.0% | 57.5% | +2.5 |
| cancel | 50.0% | 93.8% | +43.8 |
| lookup | 25.0% | 25.0% | +0.0 |
| multi | 8.3% | 20.8% | +12.5 |
| refund | 84.4% | 84.4% | +0.0 |

## all

- Success: 63.5% -> 73.0%; change +9.5 pts (paired bootstrap 95% CI +4.3 to +15.7)
- pass^8 change: +0.0 pts (CI -6.0 to +6.0)
- McNemar (per-task majority): only A passes 0, only B passes 7, p = 0.016
- Change is NOT above the noise floor
- Hallucination rate (judge): 51.4% -> 36.1%
- Cost per success (notional): $0.0097 -> $0.0085

| Category | A | B | Change |
|---|---|---|---|
| address | 82.5% | 90.0% | +7.5 |
| adversarial | 77.5% | 75.8% | -1.7 |
| cancel | 51.8% | 87.5% | +35.7 |
| lookup | 35.0% | 35.0% | +0.0 |
| multi | 21.4% | 41.1% | +19.6 |
| refund | 83.0% | 89.8% | +6.8 |

