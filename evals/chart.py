"""M6 chart: holdout success (95% CI), pass^k, hallucination rate and cost per success for each iteration (left),
and a stacked bar of failure categories on the dev split (right).
Usage: python -m evals.chart v0=v0-a v1=v1 v2=v2 v3=v3 --out docs/img/improvement.png"""
import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from evals.grade import load_grades
from evals.taxonomy import PRIMARY, count
from stats import metrics as M

COLORS = {"skipped_order_lookup": "#2b6fd8", "skipped_identity_check": "#e0494d", "gave_up_early": "#8b8d99",
          "malformed_tool_call": "#f3a424", "policy_violation": "#7a3ff2", "repeated_calls": "#555555",
          "misread_request": "#2aa198", "other": "#cccccc"}


def main(pairs, out):
    labels, hold, hat, hall, cps, cats = [], [], [], [], [], []
    notes = {}
    cfgp = Path("results/versions.json")
    if cfgp.exists():
        notes = json.loads(cfgp.read_text())
    for p in pairs:
        name, run = p.split("=")
        g = load_grades(run)
        h = [x for x in g if x["split"] == "holdout"]
        pt = M.per_task(h)
        k = max(len(v) for v in pt.values())
        hold.append(M.bootstrap_ci(pt))
        hat.append(M.pass_hat(pt, k))
        judged = [x for x in h if "claims" in x]
        if judged:
            hall.append(sum(x["claims"]["hallucinated"] for x in judged) / len(judged))
        else:
            hall.append(sum(x["fab_entity"]["fabricated"] or x["fab_action"]["fabricated"] for x in h) / len(h))
        cps.append(sum(x["totals"]["cost_usd"] for x in h) / max(sum(x["success"] for x in h), 1))
        cats.append(count(run)[0])   # primary failure categories of the failed dev trials
        labels.append(f"{name}\n{notes.get(name, '')}")
    xs = range(len(labels))
    fig, (a, b) = plt.subplots(1, 2, figsize=(17, 6.4))
    a.errorbar(xs, [100 * h[0] for h in hold], yerr=[[100 * (h[0] - h[1]) for h in hold], [100 * (h[2] - h[0]) for h in hold]],
               marker="o", color="#2b6fd8", capsize=4, lw=2, label="Holdout success (pass^1) ± 95% CI")
    a.plot(xs, [100 * v for v in hat], marker="s", color="#7a3ff2", lw=2, label=f"pass^{k} (all {k} trials succeed)")
    a.plot(xs, [100 * v for v in hall], marker="^", color="#e0494d", lw=2, label="Hallucination rate (holdout)")
    for x, c in zip(xs, cps):
        a.annotate(f"${c:.4f}/success", (x, 2), ha="center", fontsize=8, color="#555")
    a.set_xticks(list(xs)); a.set_xticklabels(labels, fontsize=8); a.set_ylim(0, 100); a.set_ylabel("%"); a.grid(alpha=.3)
    a.set_title("Frozen holdout (18 tasks x 4 trials) across gated iterations"); a.legend(fontsize=8, loc="upper left")
    bottom = [0] * len(labels)
    for cat in PRIMARY:
        vals = [c.get(cat, 0) for c in cats]
        if any(vals):
            b.bar(xs, vals, bottom=bottom, label=cat, color=COLORS.get(cat))
            bottom = [x + v for x, v in zip(bottom, vals)]
    b.set_xticks(list(xs)); b.set_xticklabels(labels); b.set_ylabel("failed trials (dev split, 32 tasks x 4 trials)"); b.set_ylim(0, max(bottom) * 1.08)
    b.set_title("Failure taxonomy: counts per category"); b.legend(fontsize=8)
    b.tick_params(axis='x', labelsize=8)
    fig.tight_layout()
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=120)
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs", nargs="+")
    ap.add_argument("--out", default="docs/img/improvement.png")
    a = ap.parse_args()
    main(a.pairs, a.out)
