"""M7: score a SAMPLE of online traces with reference-free graders. No expected answer is needed.
Graders: fabricated entities, fabricated actions, policy rules, tool errors, loops, and the claim-level judge.
Usage: python -m online.score --sample 1.0 --judge   Writes online/scores.jsonl and online/review_queue.jsonl."""
import argparse
import json
import random
from pathlib import Path

from evals.graders import hallucination, judge, policy, trajectory
from evals.graders.common import tool_events

TRACES, SCORES, QUEUE = Path("online/traces.jsonl"), Path("online/scores.jsonl"), Path("labels/review_queue.jsonl")


def score(traj: dict, use_judge: bool) -> dict:
    task = {"reference_calls": [], "tags": {"expect_refusal": False}}
    tools = tool_events(traj)
    s = {"trace_id": traj["task_id"], "batch": traj["batch"], "degraded": traj.get("degraded", False),
         "version": traj["version"]}
    s["fab_entity"] = hallucination.grade_fabricated_entities(task, traj)["fabricated"]
    s["fab_action"] = hallucination.grade_fabricated_actions(task, traj)["fabricated"]
    pol = policy.grade_policy(task, traj)
    s["policy_violation"], s["policy_rules"] = (not pol["pass"]), sorted({v["rule"] for v in pol["violations"]})
    s["tool_error"] = any((not e["ok"]) and not e.get("blocked") for e in tools)
    s["loop"] = trajectory.grade_efficiency(task, traj)["loop"]
    if use_judge:
        try:
            c = judge.grade_claims(task, traj)
            s["hallucinated"], s["unsupported_claims"] = c["hallucinated"], [x["claim"] for x in c["claims"] if x["label"] != "supported"]
        except Exception as e:
            s["judge_error"] = str(e)[:120]
    s["flagged"] = s["fab_entity"] or s["fab_action"] or s["policy_violation"] or s["loop"] or bool(s.get("hallucinated"))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=float, default=1.0, help="Share of traces to score (X%).")
    ap.add_argument("--judge", action="store_true")
    a = ap.parse_args()
    traces = [json.loads(l) for l in TRACES.read_text().splitlines()]
    rng = random.Random(7)
    picked = [t for t in traces if rng.random() < a.sample]
    scores = [score(t, a.judge) for t in picked]
    SCORES.write_text("".join(json.dumps(s) + "\n" for s in scores))
    # Flagged traces land in the review queue (triage happens with evals.triage)
    QUEUE.parent.mkdir(exist_ok=True)
    old = {json.loads(l)["trace_id"] for l in QUEUE.read_text().splitlines()} if QUEUE.exists() else set()
    with QUEUE.open("a") as f:
        for s in scores:
            if s["flagged"] and s["trace_id"] not in old:
                reasons = [k for k in ("fab_entity", "fab_action", "policy_violation", "loop", "hallucinated") if s.get(k)]
                f.write(json.dumps({"trace_id": s["trace_id"], "source": "online", "batch": s["batch"], "reasons": reasons,
                                    "status": "open", "category": None, "note": None}) + "\n")
    print(f"scored {len(scores)} of {len(traces)} traces; flagged {sum(s['flagged'] for s in scores)}")


if __name__ == "__main__":
    main()
