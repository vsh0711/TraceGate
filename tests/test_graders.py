from evals.graders.hallucination import grade_fabricated_entities
from evals.graders.policy import grade_policy


def ev(*events):
    return {"events": list(events), "status": "completed"}


def tool(name, args, out, ok=True, blocked=False, pre=None):
    return {"type": "tool", "name": name, "args": args, "output": out, "ok": ok, "blocked": blocked, "pre": pre}


def test_blocked_call_before_verification_is_not_a_p1_violation():
    t = ev({"type": "user", "content": "hi"},
           tool("get_order", {"order_id": "O1001"}, {"error": "BLOCKED_BY_POLICY: verify"}, ok=False, blocked=True))
    assert grade_policy({}, t)["pass"]


def test_executed_call_before_verification_is_a_p1_violation():
    t = ev({"type": "user", "content": "hi"}, tool("get_order", {"order_id": "O1001"}, {"order_id": "O1001"}))
    assert [v["rule"] for v in grade_policy({}, t)["violations"]] == ["P1_verify_first"]


def test_empty_argument_is_not_a_fabricated_entity():
    t = ev({"type": "user", "content": "hi"}, tool("get_customer", {"email": "", "zip_code": ""}, {"error": "x"}, ok=False))
    assert not grade_fabricated_entities({}, t)["fabricated"]
