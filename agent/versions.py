"""Agent versions. Each version is a gated change. Fields not listed keep the v0 value."""
from pathlib import Path

from agent import tool_specs

POLICY = Path("agent/policy.md").read_text()
PREAMBLE = Path("agent/prompts_v0.md").read_text()

VERSIONS = {
    "v0": {"note": "baseline", "descriptions": tool_specs.TERSE, "validator": False, "memory": False},
    "v1": {"note": "tool descriptions", "descriptions": tool_specs.RICH, "validator": False, "memory": False},
    "v2": {"note": "refund validator", "descriptions": tool_specs.RICH, "validator": True, "memory": False},
    "v3": {"note": "exemplar memory", "descriptions": tool_specs.RICH, "validator": True, "memory": True},
}


def system_prompt(version: str, exemplars: str = "") -> str:
    text = PREAMBLE + POLICY
    if exemplars:
        text += "\n\n# Examples of correct handling\n" + exemplars
    return text
