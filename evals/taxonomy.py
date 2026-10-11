"""Failure taxonomy (M5). Every failed trial gets ONE primary category and any number of secondary tags.

Coding rule: the primary category is the FIRST step where the agent went wrong (root cause), not the last symptom.
A rule-based tagger applies this rule to the logged trajectory. It was written after open coding of failed dev
trials (labels/failure_notes.jsonl) and is checked against those notes (see docs/failure-taxonomy.md).
Usage: python -m evals.taxonomy <run_id>   (dev split only: leakage rule)"""
import json
import sys
from collections import Counter
from pathlib import Path

from evals.grade import load_grades
from evals.runner import load_trajectories
from evals.tasks import require_dev

WRITES = {"cancel_order", "issue_refund", "update_address"}

PRIMARY = {
    "skipped_order_lookup": "Acted on an order without reading it first: a write before get_order, or a guessed or placeholder order id or amount.",
    "skipped_identity_check": "Used an order tool before identity was verified, or continued after verification failed.",
    "gave_up_early": "Stopped before the job was done: narrated or asked instead of acting, or gave no answer.",
    "malformed_tool_call": "Wrote the tool call as plain text, so no tool ran, and the job was never done.",
    "repeated_calls": "Made no wrong step first, but repeated the same call 3 or more times without progress.",
    "policy_violation": "Read the order, then still did something that the policy does not allow.",
    "misread_request": "Did a different action from the one the customer asked for.",
    "other": "A failure that matches no rule above.",
}
SECONDARY = {
    "repeated_action": "Repeated a write that already succeeded, or called the same tool with the same arguments 3 or more times.",
    "fabricated_action": "Said it did an action that no tool call did.",
    "hallucinated_fact": "Stated an id, amount or date that is not in the evidence (code check), or the judge found an unsupported claim.",
    "wrong_tool_args": "At least one call had invalid, unreal or placeholder arguments.",
}
CATEGORIES = {**PRIMARY, **SECONDARY}   # 8 primary + 4 secondary tags (12 labels in all)


def _placeholder(args: dict) -> bool:
    for k, v in args.items():
        if k == "amount" and str(v).strip().lower() in {"0", "0.0", "null", "none", "", "get_order", "full", "full amount", "full refund"}:
            return True
        if k in ("order_id", "customer_id") and not (isinstance(v, str) and v[:1] in "OC" and v[1:].isdigit()):
            return True
        if k == "amount":
            try:
                float(v)
            except (TypeError, ValueError):
                return True
    return False


def primary(g: dict, traj: dict) -> str:
    """The first wrong step in time order."""
    ev = traj["events"]
    verified, read = False, set()
    for i, e in enumerate(ev):
        if e["type"] != "tool":
            continue
        name, args, ok = e["name"], e["args"], e["ok"] and not e.get("blocked")
        if name == "get_customer":
            verified = verified or ok
            continue
        if name == "transfer_to_human":
            continue
        if not verified:
            return "skipped_identity_check"
        if name in ("get_order", "list_orders"):
            if ok:
                read.add(args.get("order_id") or "list")
            continue
        if name in WRITES and e.get("blocked"):
            reason = str(e["output"].get("error", ""))
            if args.get("order_id") in read and not any(k in reason for k in ("Read the order first", "Identity is not verified")):
                return "policy_violation"          # it read the order and still tried something that the policy forbids
        if name in WRITES:
            oid = args.get("order_id")
            if oid not in read and not (e.get("pre") is None and "list" in read and oid):
                return "skipped_order_lookup"
            pre = e.get("pre")
            if ok and pre and any(v["event"] == i for v in g["policy"]["violations"]):   # THIS write broke a rule
                return "policy_violation"
    texts = [x for x in ev if x["type"] == "assistant" and x["content"].lstrip().startswith('{"name"')]
    if texts and not g["state"]["pass"]:
        return "malformed_tool_call"
    if g["policy"]["violations"]:
        rules = {v["rule"] for v in g["policy"]["violations"]}
        if rules & {"P1_verify_first"}:
            return "skipped_identity_check"
        return "policy_violation"
    if g["efficiency"]["loop"]:
        return "repeated_calls"
    if not g["state"]["pass"]:
        changed = traj["final_diff"]["orders"] or traj["final_diff"]["refunds"]
        return "misread_request" if changed else "gave_up_early"
    if not g["answer"]["pass"]:
        return "gave_up_early"
    return "other"


def secondary(g: dict, traj: dict) -> list[str]:
    tags = []
    calls = [e for e in traj["events"] if e["type"] == "tool"]
    seen, rep = set(), g["efficiency"]["loop"]
    for e in calls:
        if e["name"] in WRITES:
            k = (e["name"], e["args"].get("order_id"))
            rep = rep or k in seen
            if e["ok"]:
                seen.add(k)
    if rep or "P9_no_double_refund" in {v["rule"] for v in g["policy"]["violations"]}:
        tags.append("repeated_action")
    if g["fab_action"]["fabricated"]:
        tags.append("fabricated_action")
    if g["fab_entity"]["fabricated"] or g.get("claims", {}).get("hallucinated"):
        tags.append("hallucinated_fact")
    if any(_placeholder(e["args"]) for e in calls if isinstance(e["args"], dict)):
        tags.append("wrong_tool_args")
    return tags


def load_failed_dev(run_id: str):
    trajs = {(t["task_id"], t["trial"]): t for t in load_trajectories(run_id)}
    for g in load_grades(run_id):
        if g["split"] == "dev" and not g["success"]:
            require_dev(g["split"], "failure taxonomy")
            yield g, trajs[(g["task_id"], g["trial"])]


def count(run_id: str) -> tuple[Counter, Counter]:
    p, s = Counter(), Counter()
    for g, t in load_failed_dev(run_id):
        p[primary(g, t)] += 1
        s.update(secondary(g, t))
    return p, s


def main(run_id: str):
    p, s = count(run_id)
    print(f"{run_id}: {sum(p.values())} failed dev trials")
    for k, v in p.most_common():
        print(f"  {v:3d}  {k}")
    print("secondary tags:", dict(s))
    Path(f"results/{run_id}/taxonomy.json").write_text(json.dumps({"primary": dict(p), "secondary": dict(s)}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
