"""Pool the graded trials of several runs of the SAME version into one run (more trials for each task).
Usage: python -m evals.pool v2-pool v2 v2-b      (the second run's trials are numbered 4 to 7, and so on)
Only grades.jsonl and config.json are written. The trajectories stay in the source runs."""
import json
import sys
from pathlib import Path

from evals.grade import load_grades


def pool(out_id: str, run_ids: list[str]):
    grades, offset = [], 0
    for run in run_ids:
        g = load_grades(run)
        n = max(x["trial"] for x in g) + 1
        grades += [{**x, "trial": x["trial"] + offset, "source_run": run} for x in g]
        offset += n
    d = Path("results") / out_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "grades.jsonl").write_text("".join(json.dumps(x) + "\n" for x in sorted(grades, key=lambda x: (x["task_id"], x["trial"]))))
    (d / "config.json").write_text(json.dumps({"run_id": out_id, "pooled_from": run_ids, "trials": offset}, indent=2))
    return len(grades)


if __name__ == "__main__":
    print(out := sys.argv[1], pool(sys.argv[1], sys.argv[2:]), "trials")
