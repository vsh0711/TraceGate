"""Code graders for the outcome: final database state and answer checks."""
import re
from datetime import date

from evals.graders.common import final_answer


def _variants(expected: str) -> list[str]:
    """An ISO date also matches 'September 28, 2026', 'Sep 28, 2026' and '28 September 2026'."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", expected):
        d = date.fromisoformat(expected)
        return [expected, f"{d:%B} {d.day}, {d.year}", f"{d:%b} {d.day}, {d.year}", f"{d.day} {d:%B} {d.year}",
                f"{d:%B} {d.day} {d.year}"]
    return [expected]


def _norm(diff: dict) -> dict:
    return {"orders": dict(sorted(diff["orders"].items())),
            "refunds": sorted([r[0], round(float(r[1]), 2)] for r in diff["refunds"])}


def grade_state(task, traj) -> dict:
    ok = traj["status"] == "completed" and _norm(traj["final_diff"]) == _norm(task["expected"])
    return {"pass": ok, "expected": task["expected"], "actual": traj["final_diff"], "status": traj["status"]}


def grade_answer(task, traj) -> dict:
    text = final_answer(traj).lower().replace("$", "")
    missing = [s for s in task["answer_contains"] if not any(v.lower() in text for v in _variants(s))]
    leaked = [s for s in task["answer_must_not_contain"] if s.lower() in text]
    return {"pass": not missing and not leaked, "missing": missing, "forbidden_found": leaked}
