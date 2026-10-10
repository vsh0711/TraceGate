import json
from collections import Counter

from evals.grade import grade_trial
from evals.reference import reference_trajectory
from evals.tasks import load_tasks


def test_task_counts_and_split():
    tasks = load_tasks()
    assert len(tasks) == 50
    hold = [t for t in tasks if t["split"] == "holdout"]
    assert len(hold) / len(tasks) >= 0.30
    assert {"id", "input", "expected", "tags", "split"} <= set(tasks[0])
    assert len({t["id"] for t in tasks}) == 50


def test_mix_has_adversarial_and_difficulties():
    tasks = load_tasks()
    assert {t["tags"]["difficulty"] for t in tasks} == {"easy", "medium", "hard"}
    assert sum(t["tags"]["category"] == "adversarial" for t in tasks) >= 10
    subs = Counter(t["tags"]["sub"] for t in tasks)
    assert subs["ambiguous"] and subs["tool_error"] and subs["pressure"] and subs["auth"]


def test_every_reference_solution_passes_every_grader():
    for t in load_tasks():
        g = grade_trial(t, reference_trajectory(t), use_judge=False)
        assert g["state"]["pass"], (t["id"], g["state"])
        assert g["answer"]["pass"], (t["id"], g["answer"])
        assert g["policy"]["pass"], (t["id"], g["policy"])
        assert not g["fab_entity"]["fabricated"], (t["id"], g["fab_entity"])
        assert not g["fab_action"]["fabricated"], (t["id"], g["fab_action"])
        assert g["tools"]["precision"] == 1 and g["tools"]["recall"] == 1
        assert g["args"]["correct_rate"] == 1 and g["args"]["schema_valid_rate"] == 1
