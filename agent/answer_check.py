"""Answer validator (version v4): checks the draft final answer BEFORE the customer sees it.
If the draft claims an action that no tool call did, states an id or amount that is not in the evidence, or adds
details that no source gives (refund timelines, payment methods, emails), the model gets one chance to rewrite.
Note: the first two checks use the same detectors as the hallucination graders. They fall by design. The
independent LLM judge on the holdout is the real test of this fix."""
import re

from config import TODAY
from evals.graders import hallucination as H
from evals.graders.common import evidence_text, executed, numbers_in, tool_events

# Details that the store policy and the tools never give. Taken from reading failed dev trials.
INVENTED_DETAIL = re.compile(r"(business days?|original payment method|payment method|will receive an email|confirmation email|"
                             r"email (?:confirmation|notification)|within \d+ (?:hours?|days?)|credited (?:back )?to)", re.I)


def check(events: list[dict], draft: str) -> list[str]:
    """Return a list of problems with the draft answer (empty if it is fine)."""
    problems = []
    traj = {"events": events}
    done = {e["name"] for e in tool_events(traj) if executed(e)}
    # 1. claims an action that no successful tool call did
    for sent in re.split(r"(?<=[.!?])\s+|\n+", draft):
        if H._NEG.search(sent):
            continue
        for tool, pat in H.ACTION_PATTERNS.items():
            if H._KEYWORD[tool] in sent.lower() and pat.search(sent) and tool not in done:
                problems.append(f'You wrote "{sent.strip()[:90]}" but no {tool} call succeeded. Do not say it is done.')
                break
    # 2. an id or amount that no tool result or customer message contains
    evidence = evidence_text(traj) + "\n" + TODAY
    known, nums, ans = H._known(evidence), numbers_in(evidence), H._entities(draft)
    for kind in ("order", "customer", "refund", "email", "date"):
        for x in sorted(ans[kind] - known[kind]):
            problems.append(f"{x} is not in any tool result or customer message. Remove it.")
    for m in sorted(ans["money"]):
        if m not in nums:
            problems.append(f"The amount ${m:g} is not in any tool result or customer message. Remove it.")
    # 3. details that nothing in the system gives
    m = INVENTED_DETAIL.search(draft)
    if m:
        problems.append(f'"{m.group(0)}" is a detail that no tool result or policy gives. Remove it.')
    return problems[:4]
