"""M7: build online/dashboard.html: metrics over time (batches) and an alert when the hallucination rate is too high.
The alert metric is the code-check hallucination rate (a fabricated entity or a fabricated action), which covers every
scored trace. The judge rate is shown too, over the judged (sampled) traces only.
Usage: python -m online.dashboard --threshold 0.25   (the threshold was set from the healthy batches 1 to 4)"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCORES = Path("online/scores.jsonl")
METRICS = [("hallucination_code", "Hallucination rate (code checks)"), ("hallucinated", "Hallucination rate (judge, sampled)"),
           ("policy_violation", "Policy violation rate"), ("tool_error", "Tool error rate"), ("loop", "Loop rate")]


def rate(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return (sum(bool(v) for v in vals) / len(vals)) if vals else None


POLICY_THRESHOLD = 0.10   # the healthy batches 1 to 7 all have 0%, so any value above 0 is a clear change


def main(threshold: float):
    rows = [json.loads(l) for l in SCORES.read_text().splitlines()]
    by = defaultdict(list)
    for r in rows:
        by[r["batch"]].append(r)
    batches = sorted(by)
    series = {k: [rate(by[b], k) for b in batches] for k, _ in METRICS}
    blocks = [sum(r.get("blocked_calls", 0) for r in by[b]) / len(by[b]) for b in batches]
    regress = {b: next((r["regression"] for r in by[b] if r.get("regression")), None) for b in batches}
    alerts = [b for b, v in zip(batches, series["hallucination_code"]) if v is not None and v > threshold]
    policy_alerts = [b for b, v in zip(batches, series["policy_violation"]) if v is not None and v > POLICY_THRESHOLD]

    fig, ax = plt.subplots(1, 2, figsize=(14, 4.4))
    for k, label in METRICS:
        pts = [(b, 100 * v) for b, v in zip(batches, series[k]) if v is not None]
        if pts:
            ax[0].plot(*zip(*pts), marker="o", label=label)
    ax[0].axhline(100 * threshold, color="red", ls="--", lw=1, label=f"Hallucination alert {100 * threshold:.0f}%")
    ax[0].axhline(100 * POLICY_THRESHOLD, color="purple", ls=":", lw=1, label=f"Policy alert {100 * POLICY_THRESHOLD:.0f}%")
    for b in batches:
        if regress[b]:
            ax[0].axvspan(b - 0.5, b + 0.5, color="orange", alpha=0.15)
    ax[0].set_xlabel("batch (time); orange = deliberate regression"); ax[0].set_ylabel("% of traces"); ax[0].set_title("Online metrics")
    ax[0].legend(fontsize=7)
    ax[1].bar(batches, blocks, color="#888")
    ax[1].set_xlabel("batch"); ax[1].set_ylabel("guardrail blocks per trace"); ax[1].set_title("Guardrail interventions")
    fig.tight_layout(); fig.savefig("online/dashboard.png", dpi=110)

    queue = Path("labels/review_queue.jsonl")
    q = [json.loads(l) for l in queue.read_text().splitlines()] if queue.exists() else []
    fmt = lambda v: "n/a" if v is None else f"{100 * v:.0f}%"
    html = ["<html><body style='font-family:sans-serif;max-width:1000px;margin:20px auto'><h1>Online eval dashboard</h1>"]
    msgs = ([f"ALERT: code-check hallucination rate above {threshold:.0%} in batch(es) {', '.join(map(str, alerts))}"] if alerts else []) + \
           ([f"ALERT: policy violation rate above {POLICY_THRESHOLD:.0%} in batch(es) {', '.join(map(str, policy_alerts))}"] if policy_alerts else [])
    html.append(f"<h2 style='color:{'#c00' if msgs else '#080'}'>" + ("<br>".join(msgs) if msgs else "No alert") + "</h2>")
    html.append("<img src='dashboard.png' style='width:100%'>")
    html.append("<h3>Per-batch table</h3><table border=1 cellpadding=4><tr><th>batch</th><th>regression</th><th>traces</th>" +
                "".join(f"<th>{l}</th>" for _, l in METRICS) + "<th>blocks/trace</th></tr>")
    for i, b in enumerate(batches):
        html.append(f"<tr><td>{b}</td><td>{regress[b] or ''}</td><td>{len(by[b])}</td>" +
                    "".join(f"<td>{fmt(series[k][i])}</td>" for k, _ in METRICS) + f"<td>{blocks[i]:.2f}</td></tr>")
    html.append(f"</table><h3>Review queue ({len(q)} traces)</h3><ul>" +
                "".join(f"<li>{x['trace_id']} (batch {x['batch']}): {', '.join(x['reasons'])}</li>" for x in q[:60]) + "</ul></body></html>")
    Path("online/dashboard.html").write_text("\n".join(html))
    print("hallucination alerts in batches:", alerts or "none", "| policy alerts in batches:", policy_alerts or "none", "| wrote online/dashboard.html")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.25)
    main(ap.parse_args().threshold)
