"""M6 step 2 for online traces: triage the flagged traces in labels/review_queue.jsonl into taxonomy categories.
Labels were assigned by reading each trace (Claude, not a human reviewer) with the rule "first wrong step".
Usage: python -m evals.online_triage     Updates labels/review_queue.jsonl and labels/failure_notes.jsonl."""
import json
from collections import Counter
from pathlib import Path

from evals.grade import grade_trial
from evals.taxonomy import primary, secondary

I, L, P, R = "skipped_identity_check", "skipped_order_lookup", "policy_violation", "repeated_calls"
# Index in the review queue -> primary category. Read from the compact view of every flagged trace.
MANUAL = {0: I, 1: I, 2: I, 3: L, 4: L, 5: I, 6: I, 7: I, 8: I, 9: I, 10: L, 11: L, 12: I, 13: P, 14: P, 15: I, 16: R, 17: I,
          18: L, 19: L, 20: L, 21: I, 22: P, 23: P, 24: P, 25: I, 26: I, 27: L, 28: I, 29: P, 30: P, 31: I, 32: I, 33: P, 34: P}
NOTE = {
    I: "Called an order tool before the customer was verified (the customer gave no identity at first).",
    L: "Tried a change on an order that it had not read with get_order, or used a guessed argument.",
    P: "Read the order, then tried or made a change that the policy does not allow.",
    R: "Repeated the same call 3 times without progress.",
}


def main():
    qpath = Path("labels/review_queue.jsonl")
    queue = [json.loads(l) for l in qpath.read_text().splitlines()]
    assert len(queue) == len(MANUAL), f"{len(queue)} queue items but {len(MANUAL)} labels: re-read the new items first"
    traces = {t["task_id"]: t for t in map(json.loads, Path("online/traces.jsonl").read_text().splitlines())}
    notes, agree, conf = [], 0, Counter()
    for i, q in enumerate(queue):
        t = traces[q["trace_id"]]
        stub = {"id": t["task_id"], "split": "online", "tags": {"category": "online", "difficulty": "n/a", "expect_refusal": False},
                "reference_calls": [], "expected": t["final_diff"], "answer_contains": [], "answer_must_not_contain": []}
        g = grade_trial(stub, t, False)
        auto = primary(g, t)
        agree += auto == MANUAL[i]
        if auto != MANUAL[i]:
            conf[(MANUAL[i], auto)] += 1
        q.update({"status": "triaged", "category": MANUAL[i], "note": NOTE[MANUAL[i]], "tagger": auto})
        notes.append({"run": f"online-b{q['batch']}", "task_id": q["trace_id"], "trial": 0, "category": MANUAL[i], "tagger": auto,
                      "secondary": secondary(g, t), "note": NOTE[MANUAL[i]], "source": "online", "coder": "claude (manual reading)"})
    qpath.write_text("".join(json.dumps(q) + "\n" for q in queue))
    old = [l for l in Path("labels/failure_notes.jsonl").read_text().splitlines() if '"source": "online"' not in l]
    Path("labels/failure_notes.jsonl").write_text("\n".join(old + [json.dumps(n) for n in notes]) + "\n")
    healthy = Counter(q["category"] for q in queue if q["batch"] <= 7)
    regress = Counter(q["category"] for q in queue if q["batch"] >= 8)
    print(f"{len(queue)} online items triaged; tagger agrees on {agree}; disagreements: {dict(conf)}")
    print("healthy batches 1-7 (v2):", dict(healthy)); print("guard-off batches 8-9 (v0):", dict(regress))


if __name__ == "__main__":
    main()
