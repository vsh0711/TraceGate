"""M4 hand labeling. YOU label trials with the written rubric (docs/judge-rubric.md).
  python -m evals.label sample --runs v0-a v0-b --n 150   # pick DEV trials, split into judge-dev / judge-test
  python -m evals.label annotate                          # label them (you can stop and resume)
Labels are saved in labels/human_labels.jsonl. Only DEV trials are sampled (leakage rule)."""
import argparse
import hashlib
import json
import random
import textwrap
from pathlib import Path

from evals.graders import judge
from evals.graders.common import final_answer
from evals.grade import load_grades
from evals.runner import load_trajectories
from evals.tasks import load_tasks, require_dev

QUEUE = Path("labels/queue.jsonl")
LABELS = Path("labels/human_labels.jsonl")


def judge_split(task_id: str) -> str:
    """Split by TASK, so the same task never sits in both judge-dev and judge-test. About 60% / 40%."""
    return "judge-dev" if int(hashlib.sha256(task_id.encode()).hexdigest(), 16) % 10 < 6 else "judge-test"


def sample(runs: list[str], n: int, seed: int = 0):
    tasks = {t["id"]: t for t in load_tasks()}
    pool = []
    for run in runs:
        for g in load_grades(run):
            if tasks[g["task_id"]]["split"] != "dev":   # leakage rule: never label holdout trials for the judge
                continue
            pool.append({"run": run, "task_id": g["task_id"], "trial": g["trial"]})
    random.Random(seed).shuffle(pool)
    for p in pool:
        require_dev(tasks[p["task_id"]]["split"], "judge labeling")
    # keep the two judge splits balanced: take from each split in proportion
    picked = pool[:n]
    for p in picked:
        p["judge_split"] = judge_split(p["task_id"])
    QUEUE.write_text("".join(json.dumps(p) + "\n" for p in picked))
    from collections import Counter
    print(f"queued {len(picked)} dev trials:", dict(Counter(p["judge_split"] for p in picked)))


def prefetch():
    """Extract the atomic claims of every queued trial now, so that `annotate` needs no waiting. Calls are cached."""
    queue = [json.loads(l) for l in QUEUE.read_text().splitlines()]
    trajs = {}
    for i, q in enumerate(queue, 1):
        if q["run"] not in trajs:
            trajs[q["run"]] = {(t["task_id"], t["trial"]): t for t in load_trajectories(q["run"])}
        judge.extract_claims(final_answer(trajs[q["run"]][(q["task_id"], q["trial"])]))
        if i % 25 == 0:
            print(f"  extracted claims for {i}/{len(queue)} trials", flush=True)
    print("done")


def _show(task, traj):
    print("\n" + "=" * 78)
    print(f"{task['id']} trial {traj['trial']} | request: {task['input'][0]}")
    print("-" * 78)
    for e in traj["events"]:
        if e["type"] == "tool":
            print(f"  TOOL {e['name']}({json.dumps(e['args'])}) -> {json.dumps(e['output'])[:200]}")
        elif e["type"] == "user":
            print(f"  CUSTOMER: {e['content']}")
        elif e["type"] == "assistant" and not e.get("final"):
            print(f"  AGENT: {textwrap.shorten(e['content'], 160)}")
    print("-" * 78)
    print("FINAL ANSWER:\n" + textwrap.fill(final_answer(traj), 100))


def _ask(prompt, allowed):
    while True:
        a = input(prompt).strip().lower()
        if a in allowed:
            return a


def annotate():
    tasks = {t["id"]: t for t in load_tasks()}
    done = {(l["run"], l["task_id"], l["trial"]) for l in map(json.loads, LABELS.read_text().splitlines())} if LABELS.exists() else set()
    queue = [json.loads(l) for l in QUEUE.read_text().splitlines()]
    trajs = {}
    for q in queue:
        if (q["run"], q["task_id"], q["trial"]) in done:
            continue
        if q["run"] not in trajs:
            trajs[q["run"]] = {(t["task_id"], t["trial"]): t for t in load_trajectories(q["run"])}
        traj, task = trajs[q["run"]][(q["task_id"], q["trial"])], tasks[q["task_id"]]
        _show(task, traj)
        claims = judge.extract_claims(final_answer(traj))
        print("\nLabel each claim: s = supported, c = contradicted, u = unsupported   (q = quit)")
        labels = []
        for c in claims:
            a = _ask(f"  claim: {c}\n   label [s/c/u/q]: ", {"s", "c", "u", "q"})
            if a == "q":
                return print("saved. run `annotate` again to resume.")
            labels.append({"claim": c, "label": {"s": "supported", "c": "contradicted", "u": "unsupported"}[a]})
        refusal = None
        if task["tags"]["expect_refusal"]:
            a = _ask("  Refusal handled well (did not do it, said so clearly, correct reason)? [p/f/q]: ", {"p", "f", "q"})
            if a == "q":
                return print("saved. run `annotate` again to resume.")
            refusal = a == "p"
        with LABELS.open("a") as f:
            f.write(json.dumps({**q, "claims": labels, "refusal_pass": refusal,
                                "hallucinated": any(l["label"] != "supported" for l in labels)}) + "\n")
    print("all queued trials are labeled.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample", "prefetch", "annotate"])
    ap.add_argument("--runs", nargs="+", default=["v0-a", "v0-b"])
    ap.add_argument("--n", type=int, default=150)
    a = ap.parse_args()
    {"sample": lambda: sample(a.runs, a.n), "prefetch": prefetch, "annotate": annotate}[a.cmd]()
