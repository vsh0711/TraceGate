"""Exemplar memory (fix type 3 in M6): store successful DEV trajectories, retrieve the most similar
ones as few-shot examples at run time.
LEAK GUARD: only dev tasks may enter the memory. At run time a task never retrieves itself."""
import json
import sys
from pathlib import Path

from evals.grade import load_grades
from evals.runner import load_trajectories
from evals.similarity import most_similar
from evals.tasks import load_tasks, require_dev

PATH = Path("agent/exemplars.json")


def _render(task_input: str, traj: dict) -> str:
    steps, n = [], 1
    for e in traj["events"][1:]:
        if e["type"] == "tool":
            args = ", ".join(f"{k}={json.dumps(v)}" for k, v in e["args"].items())
            steps.append(f"{n}. call {e['name']}({args})")
        elif e["type"] == "assistant" and e["content"]:
            steps.append(f"{n}. say: \"{e['content'][:220].strip()}\"")
        elif e["type"] == "user":
            steps.append(f"{n}. customer: \"{e['content'][:120]}\"")
        else:
            continue
        n += 1
    return f"Customer: \"{task_input}\"\nCorrect handling:\n" + "\n".join(steps)


class ExemplarMemory:
    def __init__(self, items: list[dict]):
        self.items = items

    @classmethod
    def load(cls):
        return cls(json.loads(PATH.read_text()))

    def retrieve(self, task: dict, exclude_task: str | None = None, k: int = 2) -> str:
        cands = [it for it in self.items if it["task_id"] != exclude_task]
        if not cands:
            return ""
        hits = most_similar(task["input"][0], [c["request"] for c in cands], k)
        return "\n\n".join(f"Example {i + 1}\n{cands[j]['text']}" for i, (j, _) in enumerate(hits))


def build(run_id: str):
    """Keep the shortest successful trajectory of each DEV task from a graded run."""
    tasks = {t["id"]: t for t in load_tasks()}
    trajs = {(t["task_id"], t["trial"]): t for t in load_trajectories(run_id)}
    best = {}
    for g in load_grades(run_id):
        if tasks[g["task_id"]]["split"] != "dev":   # leakage rule: holdout trials never enter the memory
            continue
        if not g["success"] or g["fab_entity"]["fabricated"]:
            continue
        tr = trajs[(g["task_id"], g["trial"])]
        if g["task_id"] not in best or len(tr["events"]) < len(best[g["task_id"]]["events"]):
            best[g["task_id"]] = tr
    items = [{"task_id": tid, "request": tasks[tid]["input"][0], "text": _render(tasks[tid]["input"][0], tr)}
             for tid, tr in sorted(best.items())]
    for it in items:
        require_dev(tasks[it["task_id"]]["split"], "exemplar memory")   # final check
    PATH.write_text(json.dumps(items, indent=1))
    print(f"memory: {len(items)} exemplars from dev tasks of run {run_id}")


if __name__ == "__main__":
    build(sys.argv[2]) if sys.argv[1] == "build" else sys.exit("usage: python -m agent.memory build <run_id>")
