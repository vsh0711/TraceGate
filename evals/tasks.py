"""Task loading. The holdout split is frozen: a hash lock detects any change."""
import hashlib
import json
from pathlib import Path

TASKS_PATH = Path("evals/tasks.jsonl")
LOCK_PATH = Path("evals/holdout.lock")


def load_tasks(split: str = "all") -> list[dict]:
    tasks = [json.loads(l) for l in TASKS_PATH.read_text().splitlines() if l.strip()]
    verify_holdout(tasks)
    return tasks if split == "all" else [t for t in tasks if t["split"] == split]


def _holdout_hash(tasks) -> str:
    hold = sorted((t for t in tasks if t["split"] == "holdout"), key=lambda t: t["id"])
    return hashlib.sha256(json.dumps(hold, sort_keys=True).encode()).hexdigest()


def freeze_holdout() -> str:
    tasks = [json.loads(l) for l in TASKS_PATH.read_text().splitlines() if l.strip()]
    if LOCK_PATH.exists():
        raise SystemExit("The holdout is already frozen.")
    LOCK_PATH.write_text(_holdout_hash(tasks) + "\n")
    return LOCK_PATH.read_text().strip()


def verify_holdout(tasks) -> None:
    if LOCK_PATH.exists() and LOCK_PATH.read_text().strip() != _holdout_hash(tasks):
        raise SystemExit("LEAK GUARD: the frozen holdout tasks changed. Restore them. Never edit holdout tasks.")


def require_dev(split: str, what: str) -> None:
    """Leakage rule: error analysis, exemplars, judge tuning and optimizers may use dev data only."""
    if split != "dev":
        raise SystemExit(f"LEAK GUARD: {what} may use the dev split only, not '{split}'.")


if __name__ == "__main__":
    print("frozen holdout hash:", freeze_holdout())
