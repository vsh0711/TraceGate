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


def decide_hallucination(base: str, cand: str) -> dict:
    """Gate for a fix that targets hallucination. The test is the judged hallucination rate on the HOLDOUT
    (the judge is independent from the code checks that the fix may use). Pass only if (1) the rate falls and the
    paired-bootstrap 95% interval of the change (resampling tasks) excludes 0, and (2) success on dev and on holdout does
    not fall by more than the noise floor, and (3) no category regresses."""
    from evals.grade import load_grades
    from stats import metrics as M
    ga = [g for g in load_grades(base) if g["split"] == "holdout" and "claims" in g]
    gb = [g for g in load_grades(cand) if g["split"] == "holdout" and "claims" in g]
    hall = lambda g: g["claims"]["hallucinated"]
    pa, pb = M.per_task(ga, hall), M.per_task(gb, hall)
    delta, lo, hi = M.paired_bootstrap_diff(pa, pb)
    out = compare(base, cand)
    noise = out["noise_floor"] if out["noise_floor"] is not None else 0.0
    regress = {f"{sp}/{c}": round(v["b"] - v["a"], 3) for sp in ("dev", "holdout") for c, v in out["splits"][sp]["categories"].items()
               if v["b"] - v["a"] < -config.CATEGORY_REGRESSION_LIMIT}
    checks = {"hallucination_falls_significantly": hi < 0,
              "dev_success_not_worse_than_noise": out["splits"]["dev"]["delta"] > -noise,
              "holdout_success_not_worse_than_noise": out["splits"]["holdout"]["delta"] > -noise,
              "no_category_regression": not regress}
    return {"promote": all(checks.values()), "target": "hallucination", "checks": checks, "regressions": regress,
            "hallucination_a": M.success_rate(pa), "hallucination_b": M.success_rate(pb), "hallucination_delta": delta,
            "hallucination_ci": [lo, hi], "n_tasks": len(set(pa) & set(pb)), "noise_floor": noise}


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[3] == "--target-hallucination":
        res = decide_hallucination(sys.argv[1], sys.argv[2])
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["promote"] else 1)
    res = decide(compare(sys.argv[1], sys.argv[2]))
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["promote"] else 1)
