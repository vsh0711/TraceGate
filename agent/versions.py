"""Agent versions. Each version is a gated change. Fields not listed keep the v0 value."""
from pathlib import Path

from agent import tool_specs

POLICY = Path("agent/policy.md").read_text()
PREAMBLE = Path("agent/prompts_v0.md").read_text()

VERSIONS = {
    "v0": {"note": "baseline", "descriptions": tool_specs.TERSE, "validator": False, "memory": False},
    "v1": {"note": "tool descriptions", "descriptions": tool_specs.RICH, "validator": False, "memory": False},
    # v1 was rejected by the gate (see CHANGELOG.md), so v2 starts from v0 and adds only the guardrail.
    "v2": {"note": "guardrail", "descriptions": tool_specs.TERSE, "validator": True, "memory": False},
    "v3": {"note": "exemplar memory", "descriptions": tool_specs.TERSE, "validator": True, "memory": True},
    # v3 was rejected, so v4 starts from v2 and adds only the answer validator.
    "v4": {"note": "answer validator", "descriptions": tool_specs.TERSE, "validator": True, "memory": False, "answer_check": True},
}


def system_prompt(version: str, exemplars: str = "") -> str:
    text = PREAMBLE + POLICY
    if exemplars:
        text += "\n\n# Examples of correct handling\n" + exemplars
    return text
