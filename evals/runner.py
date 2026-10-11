"""Runner: n trials per task, in parallel, with cached model calls and a fixed config.
Example: python -m evals.runner --version v0 --trials 4 --run-id v0-a
A resumed run skips trials that are already logged."""
import argparse
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import config
from agent.loop import run_trial
from agent.user import HARNESS_VERSION
from agent.versions import VERSIONS
from evals.tasks import load_tasks


def run_dir(run_id: str) -> Path:
    return Path("results") / run_id


def load_trajectories(run_id: str) -> list[dict]:
    p = run_dir(run_id) / "trajectories.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v0", choices=list(VERSIONS))
    ap.add_argument("--trials", type=int, default=config.N_TRIALS)
    ap.add_argument("--split", default="all", choices=["all", "dev", "holdout"])
    ap.add_argument("--run-id")
    ap.add_argument("--salt", default="", help="Changes the sampling seed. Use it for the noise-floor re-run.")
    ap.add_argument("--workers", type=int, default=config.WORKERS)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--limit", type=int, help="Only the first N tasks (smoke test).")
    ap.add_argument("--only-dataset-version", help="Only tasks added in this dataset version, for example v2 (the regression tasks).")
    a = ap.parse_args(argv)

    run_id = a.run_id or f"{a.version}-{a.split}"
    d = run_dir(run_id)
    d.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks(a.split)
    if a.only_dataset_version:
        tasks = [t for t in tasks if t["dataset_version"] == a.only_dataset_version]
    tasks = tasks[: a.limit]
    cfg = {"run_id": run_id, "version": a.version, "version_note": VERSIONS[a.version]["note"], "split": a.split,
           "trials": a.trials, "salt": a.salt, "model": config.AGENT_MODEL, "temperature": config.TEMPERATURE,
           "harness": HARNESS_VERSION, "max_steps": config.MAX_STEPS, "max_tokens": config.MAX_TOKENS, "n_tasks": len(tasks)}
    (d / "config.json").write_text(json.dumps(cfg, indent=2))

    path = d / "trajectories.jsonl"
    done = {(t["task_id"], t["trial"]) for t in load_trajectories(run_id)}
    jobs = [(t, k) for t in tasks for k in range(a.trials) if (t["id"], k) not in done]
    print(f"[{run_id}] {len(tasks)} tasks x {a.trials} trials; {len(done)} done, {len(jobs)} to run", flush=True)

    exemplars = None
    if VERSIONS[a.version]["memory"]:
        from agent.memory import ExemplarMemory
        exemplars = ExemplarMemory.load()

    lock = threading.Lock()

    def one(task, k):
        ex = exemplars.retrieve(task, exclude_task=task["id"]) if exemplars else ""
        return run_trial(task, a.version, k, a.salt, exemplars=ex, use_cache=not a.no_cache)

    n_ok = n_done = 0
    with ThreadPoolExecutor(max_workers=a.workers) as pool, path.open("a") as f:
        futs = {pool.submit(one, t, k): (t["id"], k) for t, k in jobs}
        for fut in as_completed(futs):
            traj = fut.result()
            with lock:
                f.write(json.dumps(traj) + "\n")
                f.flush()
                n_done += 1
            if n_done % 10 == 0 or n_done == len(jobs):
                print(f"  {n_done}/{len(jobs)} trials", flush=True)
    return run_id


if __name__ == "__main__":
    main()
