"""M6 gate. Promote a candidate only if the gain is significant AND no category regresses.
Usage: python -m evals.gate <baseline_run> <candidate_run>
Rules are in docs/gate.md. Thresholds live in config.py."""
import json
import sys

import config
from evals.diff import compare


def decide(out: dict) -> dict:
    noise = out["noise_floor"] if out["noise_floor"] is not None else 0.0
    dev, hold = out["splits"]["dev"], out["splits"]["holdout"]
    checks = {
        "dev_gain_above_noise": dev["delta"] > noise,
        "dev_gain_significant": dev["ci"][0] > 0,
        "holdout_gain_above_noise": hold["delta"] > noise,
    }
    regress = {}
    for split in ("dev", "holdout"):
        for c, v in out["splits"][split]["categories"].items():
            if v["b"] - v["a"] < -config.CATEGORY_REGRESSION_LIMIT:
                regress[f"{split}/{c}"] = round(v["b"] - v["a"], 3)
    checks["no_category_regression"] = not regress
    return {"promote": all(checks.values()), "checks": checks, "regressions": regress,
            "dev_delta": dev["delta"], "dev_ci": dev["ci"], "holdout_delta": hold["delta"], "holdout_ci": hold["ci"],
            "noise_floor": noise}


if __name__ == "__main__":
    res = decide(compare(sys.argv[1], sys.argv[2]))
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["promote"] else 1)
