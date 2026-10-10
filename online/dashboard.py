"""M7: build online/dashboard.html: metrics over time (batches) and an alert when the hallucination rate is too high.
Usage: python -m online.dashboard --threshold 0.25"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCORES = Path("online/scores.jsonl")
METRICS = [("hallucinated", "Hallucination rate (judge)"), ("fab_entity", "Fabricated entity rate"),
           ("fab_action", "Fabricated action rate"), ("policy_violation", "Policy violation rate"),
           ("tool_error", "Tool error rate"), ("loop", "Loop rate")]


def main(threshold: float):
    rows = [json.loads(l) for l in SCORES.read_text().splitlines()]
    by = defaultdict(list)
    for r in rows:
        by[r["batch"]].append(r)
    batches = sorted(by)
    series = {k: [sum(bool(r.get(k)) for r in by[b]) / len(by[b]) for b in batches] for k, _ in METRICS}
    degraded = [any(r["degraded"] for r in by[b]) for b in batches]
    alerts = [b for b, v in zip(batches, series["hallucinated"]) if v > threshold]

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.2))
    for k, label in METRICS:
        ax[0].plot(batches, [100 * v for v in series[k]], marker="o", label=label)
    ax[0].axhline(100 * threshold, color="red", ls="--", lw=1, label=f"Alert threshold {100 * threshold:.0f}%")
    for b, d in zip(batches, degraded):
        if d:
            ax[0].axvspan(b - 0.5, b + 0.5, color="orange", alpha=0.12)
    ax[0].set_xlabel("batch (time)"); ax[0].set_ylabel("% of sampled traces"); ax[0].set_title("Online metrics (orange = degraded tool descriptions)")
    ax[0].legend(fontsize=7)
    ax[1].bar(batches, [len(by[b]) for b in batches], color="#888")
    ax[1].set_xlabel("batch"); ax[1].set_ylabel("sampled traces"); ax[1].set_title("Traffic sampled")
    fig.tight_layout(); fig.savefig("online/dashboard.png", dpi=110)

    queue = Path("labels/review_queue.jsonl")
    q = [json.loads(l) for l in queue.read_text().splitlines()] if queue.exists() else []
    html = ["<html><body style='font-family:sans-serif;max-width:1000px;margin:20px auto'><h1>Online eval dashboard</h1>"]
    html.append(f"<h2 style='color:{'#c00' if alerts else '#080'}'>{'ALERT: hallucination rate above ' + format(threshold, '.0%') + ' in batch(es) ' + ', '.join(map(str, alerts)) if alerts else 'No alert'}</h2>")
    html.append("<img src='dashboard.png' style='width:100%'>")
    html.append("<h3>Per-batch table</h3><table border=1 cellpadding=4><tr><th>batch</th><th>degraded</th><th>traces</th>" +
                "".join(f"<th>{l}</th>" for _, l in METRICS) + "</tr>")
    for i, b in enumerate(batches):
        html.append(f"<tr><td>{b}</td><td>{degraded[i]}</td><td>{len(by[b])}</td>" +
                    "".join(f"<td>{100 * series[k][i]:.0f}%</td>" for k, _ in METRICS) + "</tr>")
    html.append(f"</table><h3>Review queue ({len(q)} traces)</h3><ul>" +
                "".join(f"<li>{x['trace_id']} (batch {x['batch']}): {', '.join(x['reasons'])}</li>" for x in q[:40]) + "</ul></body></html>")
    Path("online/dashboard.html").write_text("\n".join(html))
    print("alerts in batches:", alerts or "none", "| wrote online/dashboard.html")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.25)
    main(ap.parse_args().threshold)
