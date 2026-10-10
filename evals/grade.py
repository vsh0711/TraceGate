"""Grade every trajectory of a run. Writes results/<run>/grades.jsonl.
Success = all OUTCOME graders pass: final state, answer checks, and policy rules.
The hallucination and judge results are reported next to success but are not part of it."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from evals.graders import hallucination, judge, policy, state, trajectory
from evals.runner import load_trajectories, run_dir
from evals.tasks import load_tasks


def grade_trial(task, traj, use_judge: bool) -> dict:
    g = {"task_id": task["id"], "trial": traj["trial"], "version": traj["version"], "split": task["split"],
         "category": task["tags"]["category"], "difficulty": task["tags"]["difficulty"]}
    g["state"] = state.grade_state(task, traj)
    g["answer"] = state.grade_answer(task, traj)
    g["policy"] = policy.grade_policy(task, traj)
    g["tools"] = trajectory.grade_tools(task, traj)
    g["args"] = trajectory.grade_args(task, traj)
    g["efficiency"] = trajectory.grade_efficiency(task, traj)
    g["fab_entity"] = hallucination.grade_fabricated_entities(task, traj)
    g["fab_action"] = hallucination.grade_fabricated_actions(task, traj)
    g["success"] = g["state"]["pass"] and g["answer"]["pass"] and g["policy"]["pass"]
    g["totals"] = traj["totals"]
    g["status"] = traj["status"]
    if use_judge:
        try:
            g["claims"] = judge.grade_claims(task, traj)
            g["refusal"] = judge.grade_refusal(task, traj)
        except Exception as e:   # a judge outage must not lose the code-grader results
            g["judge_error"] = str(e)[:200]
    return g


def grade_run(run_id: str, use_judge: bool = True, workers: int = 4) -> list[dict]:
    tasks = {t["id"]: t for t in load_tasks()}
    trajs = load_trajectories(run_id)
    with ThreadPoolExecutor(max_workers=workers if use_judge else 1) as pool:
        grades = list(pool.map(lambda tr: grade_trial(tasks[tr["task_id"]], tr, use_judge), trajs))
    grades.sort(key=lambda g: (g["task_id"], g["trial"]))
    (run_dir(run_id) / "grades.jsonl").write_text("".join(json.dumps(g) + "\n" for g in grades))
    return grades


def load_grades(run_id: str) -> list[dict]:
    p = run_dir(run_id) / "grades.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    ap.add_argument("--no-judge", action="store_true")
    a = ap.parse_args()
    gs = grade_run(a.run_id, not a.no_judge)
    print(f"graded {len(gs)} trials; success {sum(g['success'] for g in gs) / max(len(gs), 1):.1%}")
