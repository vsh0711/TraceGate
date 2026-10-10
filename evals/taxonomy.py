"""Failure taxonomy (M5). A rule-based tagger gives each failed trial ONE category from grader signals.
The tagger is checked against manual open-coding notes in labels/failure_notes.jsonl (see docs/failure-taxonomy.md).
Usage: python -m evals.taxonomy <run_id>   (dev split only: leakage rule)"""
import json
import sys
from collections import Counter
from pathlib import Path

from evals.grade import load_grades
from evals.tasks import require_dev

CATEGORIES = {
    "looped": "Repeated the same call 3 or more times, hit the step limit, or the model call failed.",
    "fabricated_action": "Said that it did a cancel, refund or address change, but no matching tool call ran.",
    "policy_violation": "Changed an order that the policy does not allow (wrong status, too old, final sale, double refund, over total, not the customer's order).",
    "skipped_verification": "Used an order tool before verifying identity, or changed an order without reading it first.",
    "skipped_confirmation": "Made a change without asking the customer and getting a reply.",
    "wrong_tool_args": "Called a tool with invalid, unreal or wrong arguments, or changed the wrong order or amount.",
    "hallucinated_fact": "Stated an id, amount or date that is not in the evidence, or the judge found an unsupported claim.",
    "gave_up_early": "Did not finish: ended the turn without the needed change or answer.",
    "other": "A failure that matches no rule above.",
}


def tag(g: dict) -> str:
    """Return the first category (in priority order) that matches this failed trial."""
    rules = {v["rule"] for v in g["policy"]["violations"]}
    if g["efficiency"]["loop"] or g["status"] != "completed":
        return "looped"
    if g["fab_action"]["fabricated"]:
        return "fabricated_action"
    if rules & {"P2_own_orders", "P5_cancel_status", "P6_address_status", "P7_refund_eligibility", "P8_refund_amount", "P9_no_double_refund"}:
        return "policy_violation"
    if rules & {"P1_verify_first", "P3_read_before_write"}:
        return "skipped_verification"
    if "P4_confirm_before_write" in rules:
        return "skipped_confirmation"
    a = g["args"]
    if a["schema_valid"] < a["calls"] or a["entities_real"] < a["calls"] or a["correct"] < a["scored_calls"]:
        return "wrong_tool_args"
    if g["fab_entity"]["fabricated"] or g.get("claims", {}).get("hallucinated"):
        return "hallucinated_fact"
    if not g["state"]["pass"] or not g["answer"]["pass"]:
        return "gave_up_early"
    return "other"


def count(grades: list[dict]) -> Counter:
    return Counter(tag(g) for g in grades if not g["success"])


def main(run_id: str):
    grades = load_grades(run_id)
    dev = [g for g in grades if g["split"] == "dev"]
    require_dev(dev[0]["split"] if dev else "dev", "failure taxonomy")
    c = count(dev)
    print(f"{run_id}: {sum(c.values())} failed dev trials")
    for k, v in c.most_common():
        print(f"  {v:3d}  {k}")
    Path(f"results/{run_id}/taxonomy.json").write_text(json.dumps(dict(c), indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
