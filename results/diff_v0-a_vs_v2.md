# Run diff: v0-a -> v2

Noise floor (flip rate of identical runs): 14.0%

## dev

- Success: 46.9% -> 67.2%; change +20.3 pts (paired bootstrap 95% CI +10.9 to +31.2)
- pass^4 change: +15.6 pts (CI +6.2 to +28.1)
- McNemar (per-task majority): only A passes 0, only B passes 5, p = 0.062
- Change is ABOVE the noise floor
- Hallucination rate (judge): nan% -> nan%
- Cost per success (notional): $0.0111 -> $0.0088

| Category | A | B | Change |
|---|---|---|---|
| address | 33.3% | 83.3% | +50.0 |
| adversarial | 65.0% | 87.5% | +22.5 |
| cancel | 40.0% | 50.0% | +10.0 |
| lookup | 41.7% | 41.7% | +0.0 |
| multi | 25.0% | 25.0% | +0.0 |
| refund | 46.4% | 78.6% | +32.1 |

## holdout

- Success: 34.7% -> 50.0%; change +15.3 pts (paired bootstrap 95% CI +4.2 to +27.8)
- pass^4 change: +5.6 pts (CI +0.0 to +16.7)
- McNemar (per-task majority): only A passes 0, only B passes 2, p = 0.500
- Change is ABOVE the noise floor
- Hallucination rate (judge): 47.2% -> 51.4%
- Cost per success (notional): $0.0163 -> $0.0127

| Category | A | B | Change |
|---|---|---|---|
| address | 37.5% | 75.0% | +37.5 |
| adversarial | 40.0% | 50.0% | +10.0 |
| cancel | 50.0% | 50.0% | +0.0 |
| lookup | 25.0% | 25.0% | +0.0 |
| multi | 0.0% | 0.0% | +0.0 |
| refund | 50.0% | 87.5% | +37.5 |

## all

- Success: 42.5% -> 61.0%; change +18.5 pts (paired bootstrap 95% CI +11.0 to +26.5)
- pass^4 change: +12.0 pts (CI +4.0 to +22.0)
- McNemar (per-task majority): only A passes 0, only B passes 7, p = 0.016
- Change is ABOVE the noise floor
- Hallucination rate (judge): 47.2% -> 51.4%
- Cost per success (notional): $0.0127 -> $0.0099

| Category | A | B | Change |
|---|---|---|---|
| address | 35.0% | 80.0% | +45.0 |
| adversarial | 56.7% | 75.0% | +18.3 |
| cancel | 42.9% | 50.0% | +7.1 |
| lookup | 35.0% | 35.0% | +0.0 |
| multi | 14.3% | 14.3% | +0.0 |
| refund | 47.7% | 81.8% | +34.1 |

