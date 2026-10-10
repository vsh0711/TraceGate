"""M5/M6 triage: label failures with a free-text note (open coding) and a taxonomy category (axial coding).
  python -m evals.triage offline --run v0-a      # failed DEV trials of a run
  python -m evals.triage online                  # open items in labels/review_queue.jsonl
Press Enter to accept the suggested category. Notes are saved in labels/failure_notes.jsonl."""
import argparse
import json
from pathlib import Path

from evals.grade import load_grades
from evals.report import render_trace
from evals.runner import load_trajectories
from evals.taxonomy import CATEGORIES, tag
from evals.tasks import load_tasks, require_dev

NOTES = Path("labels/failure_notes.jsonl")
QUEUE = Path("labels/review_queue.jsonl")


def load_notes() -> list[dict]:
    return [json.loads(l) for l in NOTES.read_text().splitlines()] if NOTES.exists() else []


def save_note(entry: dict):
    NOTES.parent.mkdir(exist_ok=True)
    with NOTES.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def offline(run_id: str):
    tasks = {t["id"]: t for t in load_tasks()}
    trajs = {(t["task_id"], t["trial"]): t for t in load_trajectories(run_id)}
    done = {(n["run"], n["task_id"], n["trial"]) for n in load_notes()}
    todo = [g for g in load_grades(run_id) if not g["success"] and g["split"] == "dev" and (run_id, g["task_id"], g["trial"]) not in done]
    for g in todo:
        require_dev(g["split"], "failure triage")
        print("\n" + "=" * 80 + "\n" + render_trace(tasks[g["task_id"]], trajs[(g["task_id"], g["trial"])], g))
        sug = tag(g)
        print("categories:", ", ".join(CATEGORIES))
        cat = input(f"category [{sug}] (q to quit): ").strip() or sug
        if cat == "q":
            return
        note = input("note (one sentence: what went wrong?): ").strip()
        save_note({"run": run_id, "task_id": g["task_id"], "trial": g["trial"], "category": cat, "note": note,
                   "suggested": sug, "source": "offline", "coder": "human"})
    print("no more failed dev trials to triage.")


def online():
    items = [json.loads(l) for l in QUEUE.read_text().splitlines()]
    traces = {t["task_id"]: t for t in map(json.loads, Path("online/traces.jsonl").read_text().splitlines())}
    for it in items:
        if it["status"] != "open":
            continue
        t = traces[it["trace_id"]]
        print("\n" + "=" * 80, f"\n{it['trace_id']} flagged for {it['reasons']}")
        for e in t["events"]:
            print(" ", e["type"], e.get("name", ""), json.dumps(e.get("args") or e.get("content") or e.get("output"))[:160])
        cat = input("category (q to quit): ").strip()
        if cat == "q":
            break
        it["status"], it["category"], it["note"] = "triaged", cat, input("note: ").strip()
    QUEUE.write_text("".join(json.dumps(i) + "\n" for i in items))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["offline", "online"])
    ap.add_argument("--run")
    a = ap.parse_args()
    offline(a.run) if a.mode == "offline" else online()
