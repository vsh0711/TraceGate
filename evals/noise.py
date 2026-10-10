"""M1 noise floor: compare two runs of the SAME version with nothing changed.
Usage: python -m evals.noise v0-a v0-b   (writes results/noise.json and results/noise.md)"""
import json
import sys
from pathlib import Path

from evals.grade import load_grades
from stats import metrics as M


def main(run_a: str, run_b: str):
    ga, gb = load_grades(run_a), load_grades(run_b)
    out = {"run_a": run_a, "run_b": run_b, "n_outcomes": len({(g["task_id"], g["trial"]) for g in ga}),
           "flip_rate": {}, "success_a": {}, "success_b": {}}
    for split in ("all", "dev", "holdout"):
        sa = [g for g in ga if split == "all" or g["split"] == split]
        sb = [g for g in gb if split == "all" or g["split"] == split]
        out["flip_rate"][split] = M.flip_rate(sa, sb)
        out["success_a"][split] = M.success_rate(M.per_task(sa))
        out["success_b"][split] = M.success_rate(M.per_task(sb))
    f = out["flip_rate"]["all"]
    out["minimum_detectable_effect"] = f
    Path("results/noise.json").write_text(json.dumps(out, indent=2))
    text = (f"# Noise floor (M1)\n\nRuns `{run_a}` and `{run_b}` use the same version, the same config and the same tasks. "
            f"Only the sampling seed differs.\n\n| Split | Flip rate | Success A | Success B |\n|---|---|---|---|\n" +
            "".join(f"| {s} | {100 * out['flip_rate'][s]:.1f}% | {100 * out['success_a'][s]:.1f}% | {100 * out['success_b'][s]:.1f}% |\n"
                    for s in out["flip_rate"]) +
            f"\n**Result:** identical runs disagree on {100 * f:.1f}% of (task, trial) outcomes, "
            f"so a change smaller than {100 * f:.1f} points is not real.\n")
    Path("results/noise.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main(*sys.argv[1:3])
