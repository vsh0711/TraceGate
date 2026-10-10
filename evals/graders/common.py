"""Helpers shared by all graders."""
import json
import re

WRITE_TOOLS = {"cancel_order", "issue_refund", "update_address"}


def tool_events(traj):
    return [e for e in traj["events"] if e["type"] == "tool"]


def executed(e) -> bool:
    """A tool call that ran and did not return an error (a blocked call did not run)."""
    return e["type"] == "tool" and e["ok"] and not e.get("blocked")


def final_answer(traj) -> str:
    for e in reversed(traj["events"]):
        if e["type"] == "assistant" and e.get("final"):
            return e["content"]
    return ""


def assistant_texts(traj) -> list[str]:
    return [e["content"] for e in traj["events"] if e["type"] == "assistant" and e["content"]]


def evidence_text(traj, upto: int | None = None) -> str:
    """Everything the agent legitimately knows: user messages and tool outputs (before index `upto`)."""
    parts = []
    for i, e in enumerate(traj["events"][:upto]):
        if e["type"] == "user":
            parts.append(e["content"])
        elif e["type"] == "tool":
            parts.append(json.dumps(e["output"]))
    return "\n".join(parts)


def numbers_in(text: str) -> set[float]:
    return {round(float(x.replace(",", "")), 2) for x in re.findall(r"\d[\d,]*\.?\d*", text) if x.strip(",.")}
