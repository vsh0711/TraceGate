"""Trajectory graders: tool selection, argument correctness, efficiency."""
import json
from collections import Counter

from env.tools import PARAMS, Env
from evals.graders.common import tool_events

_ENV = Env()
_TYPES = {"string": str, "number": (int, float)}


def grade_tools(task, traj) -> dict:
    called = {e["name"] for e in tool_events(traj)}
    ref = {c["name"] for c in task["reference_calls"]}
    tp = called & ref
    precision = len(tp) / len(called) if called else 1.0
    recall = len(tp) / len(ref) if ref else 1.0
    return {"precision": precision, "recall": recall, "called": sorted(called), "reference": sorted(ref),
            "tp": sorted(tp), "fp": sorted(called - ref), "fn": sorted(ref - called)}


def _schema_ok(name, args) -> bool:
    spec = PARAMS.get(name)
    if spec is None or set(args) != set(spec):
        return False
    return all(isinstance(args[k], _TYPES[t]) and not isinstance(args[k], bool) for k, t in spec.items())


def _entities_real(name, args) -> bool:
    if "order_id" in args and _ENV.order_context(str(args["order_id"])) is None:
        return False
    if "customer_id" in args and not _ENV.customer_exists(str(args["customer_id"])):
        return False
    return True


def grade_args(task, traj) -> dict:
    calls = tool_events(traj)
    valid = sum(_schema_ok(e["name"], e["args"]) for e in calls)
    real = sum(_schema_ok(e["name"], e["args"]) and _entities_real(e["name"], e["args"]) for e in calls)
    # "Correct" = the call equals a reference call of the same tool (only tools that the reference uses).
    def norm(a):
        return json.dumps({k: (round(float(v), 2) if k == "amount" else v) for k, v in a.items()}, sort_keys=True)
    ref_args = {(c["name"], norm(c["args"])) for c in task["reference_calls"]}
    ref_tools = {c["name"] for c in task["reference_calls"]}
    scored = [e for e in calls if e["name"] in ref_tools and isinstance(e["args"], dict)]
    correct = sum((e["name"], norm(e["args"])) in ref_args for e in scored)
    return {"calls": len(calls), "schema_valid": valid, "entities_real": real,
            "scored_calls": len(scored), "correct": correct,
            "correct_rate": correct / len(scored) if scored else 1.0,
            "schema_valid_rate": valid / len(calls) if calls else 1.0,
            "entities_real_rate": real / len(calls) if calls else 1.0}


def grade_efficiency(task, traj) -> dict:
    calls = tool_events(traj)
    ref_steps = max(len(task["reference_calls"]), 1)
    counts = Counter(json.dumps([e["name"], e["args"]], sort_keys=True) for e in calls)
    repeats = sum(c - 1 for c in counts.values() if c > 1)
    looped = any(c >= 3 for c in counts.values()) or traj["status"] == "max_steps"
    return {"steps": len(calls), "ref_steps": ref_steps, "ratio": len(calls) / ref_steps,
            "repeat_calls": repeats, "loop": looped, "llm_calls": traj["totals"]["llm_calls"]}
