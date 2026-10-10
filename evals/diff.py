"""Run diff with CIs and paired tests. Usage: python -m evals.diff <run_a> <run_b>
Writes results/diff_<a>_vs_<b>.md. The noise floor comes from results/noise.json."""
import json
import sys
from pathlib import Path

from evals.grade import load_grades
from stats import metrics as M


def mde() -> float | None:
    p = Path("results/noise.json")
    return json.loads(p.read_text())["minimum_detectable_effect"] if p.exists() else None


def compare(run_a: str, run_b: str) -> dict:
    ga, gb = load_grades(run_a), load_grades(run_b)
    noise = mde()
    out = {"a": run_a, "b": run_b, "noise_floor": noise, "splits": {}}
    for split in ("dev", "holdout", "all"):
        sa = [g for g in ga if split == "all" or g["split"] == split]
        sb = [g for g in gb if split == "all" or g["split"] == split]
        pa, pb = M.per_task(sa), M.per_task(sb)
        d, lo, hi = M.paired_bootstrap_diff(pa, pb)
        k = min(len(next(iter(pa.values()))), len(next(iter(pb.values()))))
        dk, dlo, dhi = M.paired_bootstrap_diff(pa, pb, stat=lambda p: M.pass_hat(p, k))
        out["splits"][split] = {
            "success_a": M.success_rate(pa), "success_b": M.success_rate(pb), "delta": d, "ci": [lo, hi],
            "pass_hat_k": k, "pass_hat_delta": dk, "pass_hat_ci": [dlo, dhi],
            "mcnemar": M.mcnemar_majority(pa, pb),
            "above_noise": noise is not None and abs(d) > noise,
            "categories": {c: {"a": M.success_rate(M.per_task([g for g in sa if g["category"] == c])),
                               "b": M.success_rate(M.per_task([g for g in sb if g["category"] == c]))}
                           for c in sorted({g["category"] for g in sa})}}
        h = lambda gs, key: (sum(key(g) for g in gs) / len(gs)) if gs else float("nan")
        out["splits"][split]["hallucination_a"] = h([g for g in sa if "claims" in g], lambda g: g["claims"]["hallucinated"])
        out["splits"][split]["hallucination_b"] = h([g for g in sb if "claims" in g], lambda g: g["claims"]["hallucinated"])
        out["splits"][split]["cost_per_success_a"] = sum(g["totals"]["cost_usd"] for g in sa) / max(sum(g["success"] for g in sa), 1)
        out["splits"][split]["cost_per_success_b"] = sum(g["totals"]["cost_usd"] for g in sb) / max(sum(g["success"] for g in sb), 1)
    return out


def render(out: dict) -> str:
    pc = lambda x: f"{100 * x:.1f}%"
    L = [f"# Run diff: {out['a']} -> {out['b']}", "",
         f"Noise floor (flip rate of identical runs): {pc(out['noise_floor']) if out['noise_floor'] is not None else 'not measured'}", ""]
    for split, s in out["splits"].items():
        L += [f"## {split}", "",
              f"- Success: {pc(s['success_a'])} -> {pc(s['success_b'])}; change {100 * s['delta']:+.1f} pts "
              f"(paired bootstrap 95% CI {100 * s['ci'][0]:+.1f} to {100 * s['ci'][1]:+.1f})",
              f"- pass^{s['pass_hat_k']} change: {100 * s['pass_hat_delta']:+.1f} pts "
              f"(CI {100 * s['pass_hat_ci'][0]:+.1f} to {100 * s['pass_hat_ci'][1]:+.1f})",
              f"- McNemar (per-task majority): only A passes {s['mcnemar']['a_only']}, only B passes {s['mcnemar']['b_only']}, "
              f"p = {s['mcnemar']['p_value']:.3f}",
              f"- Change is {'ABOVE' if s['above_noise'] else 'NOT above'} the noise floor",
              f"- Hallucination rate (judge): {pc(s['hallucination_a'])} -> {pc(s['hallucination_b'])}",
              f"- Cost per success (notional): ${s['cost_per_success_a']:.4f} -> ${s['cost_per_success_b']:.4f}", "",
              "| Category | A | B | Change |", "|---|---|---|---|"]
        L += [f"| {c} | {pc(v['a'])} | {pc(v['b'])} | {100 * (v['b'] - v['a']):+.1f} |" for c, v in s["categories"].items()]
        L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    o = compare(sys.argv[1], sys.argv[2])
    p = Path(f"results/diff_{sys.argv[1]}_vs_{sys.argv[2]}.md")
    p.write_text(render(o))
    print(render(o))
