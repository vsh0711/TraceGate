"""M6 step 3: grow the dataset. Turn each NEW failure mode into at least one regression task.
New tasks go to the DEV split only. Near-duplicates (by embedding similarity) are dropped.
The dataset version goes up (v1 -> v2). The frozen holdout does not change.
Usage: python -m evals.grow evals/new_tasks_v2.json
The spec file is a list of objects with: category, difficulty, sub, refusal, first_message, script_tail,
reference_calls, answer_contains, answer_must_not_contain, source_failure (a task id and category)."""
import json
import sys
from pathlib import Path

from env.tools import Env
from evals import similarity
from evals.tasks import LOCK_PATH, TASKS_PATH, load_tasks


def grow(spec_path: str, threshold: float = 0.95) -> str:
    specs = json.loads(Path(spec_path).read_text())
    tasks = load_tasks()
    version = f"v{max(int(t['dataset_version'][1:]) for t in tasks) + 1}"
    texts = [" || ".join(t["input"]) for t in tasks]   # the whole scripted conversation, not only the first message
    added, dropped = [], []
    for s in specs:
        full = " || ".join([s["first_message"]] + s["script_tail"])
        if similarity.is_duplicate(full, texts, threshold):
            dropped.append(s["first_message"])
            continue
        env = Env()
        for c in s["reference_calls"]:
            env.call(c["name"], c["args"])
        tid = f"T{len(tasks) + len(added) + 1:03d}"
        added.append({"id": tid, "input": [s["first_message"]] + s["script_tail"], "expected": env.final_state_diff(),
                      "reference_calls": s["reference_calls"], "answer_contains": s.get("answer_contains", []),
                      "answer_must_not_contain": s.get("answer_must_not_contain", []),
                      "tags": {"category": s["category"], "difficulty": s["difficulty"], "sub": s.get("sub"),
                               "expect_refusal": s["refusal"], "source_failure": s.get("source_failure")},
                      "split": "dev", "dataset_version": version})
        texts.append(full)
    if added:
        all_tasks = tasks + added
        TASKS_PATH.write_text("".join(json.dumps(t) + "\n" for t in all_tasks))
        Path(f"evals/datasets/tasks.{version}.jsonl").write_text(TASKS_PATH.read_text())
        load_tasks()   # the leak guard re-checks the holdout hash
    print(f"dataset {version}: added {len(added)} dev tasks, dropped {len(dropped)} near-duplicates "
          f"(similarity backend: {similarity.backend()})")
    for d in dropped:
        print("  dropped:", d)
    return version


def check_duplicates(version: str = "v2", threshold: float = 0.95) -> list[dict]:
    """Compare every task of `version` with all tasks of earlier versions. Needs the embedding API for a real check."""
    import numpy as np
    tasks = load_tasks()
    new = [t for t in tasks if t["dataset_version"] == version]
    old = [t for t in tasks if t["dataset_version"] != version]
    X = similarity.embed([" || ".join(t["input"]) for t in old + new])   # the whole scripted conversation
    rows = []
    for i, t in enumerate(new):
        sims = X[len(old):][i] @ X[: len(old)].T
        j = int(np.argmax(sims))
        rows.append({"task": t["id"], "closest": old[j]["id"], "similarity": round(float(sims[j]), 3), "duplicate": bool(sims[j] >= threshold)})
    print(f"similarity backend: {similarity.backend()}; threshold {threshold}")
    for r in rows:
        print(f"  {r['task']} closest to {r['closest']}: {r['similarity']}  {'DUPLICATE' if r['duplicate'] else 'ok'}")
    return rows


if __name__ == "__main__":
    check_duplicates() if sys.argv[1] == "--check" else grow(sys.argv[1])
