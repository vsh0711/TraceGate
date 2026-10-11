# Run diff: v2 -> v5

Noise floor (flip rate of identical runs): 14.0%

## dev

- Success: 67.2% -> 77.3%; change +10.2 pts (paired bootstrap 95% CI +1.6 to +20.3)
- pass^4 change: +9.4 pts (CI +0.0 to +21.9)
- McNemar (per-task majority): only A passes 2, only B passes 4, p = 0.688
- Change is NOT above the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0088 -> $0.0078

| Category | A | B | Change |
|---|---|---|---|
| address | 83.3% | 75.0% | -8.3 |
| adversarial | 87.5% | 82.5% | -5.0 |
| cancel | 50.0% | 85.0% | +35.0 |
| lookup | 41.7% | 41.7% | +0.0 |
| multi | 25.0% | 56.2% | +31.2 |
| refund | 78.6% | 92.9% | +14.3 |

## holdout

- Success: 50.0% -> 63.9%; change +13.9 pts (paired bootstrap 95% CI +2.8 to +27.8)
- pass^4 change: +11.1 pts (CI +0.0 to +27.8)
- McNemar (per-task majority): only A passes 0, only B passes 3, p = 0.250
- Change is NOT above the noise floor
- Hallucination rate (judge): 51.4% -> 36.1%
- Cost per success (notional): $0.0127 -> $0.0104

| Category | A | B | Change |
|---|---|---|---|
| address | 75.0% | 100.0% | +25.0 |
| adversarial | 50.0% | 55.0% | +5.0 |
| cancel | 50.0% | 100.0% | +50.0 |
| lookup | 25.0% | 25.0% | +0.0 |
| multi | 0.0% | 25.0% | +25.0 |
| refund | 87.5% | 87.5% | +0.0 |

## all

- Success: 61.0% -> 72.5%; change +11.5 pts (paired bootstrap 95% CI +4.5 to +19.5)
- pass^4 change: +10.0 pts (CI +2.0 to +18.0)
- McNemar (per-task majority): only A passes 2, only B passes 7, p = 0.180
- Change is NOT above the noise floor
- Hallucination rate (judge): 51.4% -> 36.1%
- Cost per success (notional): $0.0099 -> $0.0086

| Category | A | B | Change |
|---|---|---|---|
| address | 80.0% | 85.0% | +5.0 |
| adversarial | 75.0% | 73.3% | -1.7 |
| cancel | 50.0% | 89.3% | +39.3 |
| lookup | 35.0% | 35.0% | +0.0 |
| multi | 14.3% | 42.9% | +28.6 |
| refund | 81.8% | 90.9% | +9.1 |

