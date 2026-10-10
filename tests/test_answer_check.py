from agent.answer_check import check

EV = [{"type": "user", "content": "refund O1001 please"},
      {"type": "tool", "name": "get_order", "args": {"order_id": "O1001"}, "output": {"order_id": "O1001", "total": 40.0},
       "ok": True, "blocked": False}]


def test_flags_false_action_unknown_amount_and_invented_detail():
    problems = check(EV, "I've issued your refund of $45.00 for O1001. It will be credited to your original payment method.")
    text = " ".join(problems)
    assert "no issue_refund call succeeded" in text and "$45" in text and "credited to" in text


def test_clean_answer_passes():
    assert check(EV, "The total of order O1001 is $40.00. Shall I refund it?") == []


def test_action_claim_is_fine_after_a_successful_call():
    ev = EV + [{"type": "tool", "name": "issue_refund", "args": {"order_id": "O1001", "amount": 40.0},
                "output": {"refund_id": "R101", "order_id": "O1001", "amount": 40.0}, "ok": True, "blocked": False}]
    assert check(ev, "I have issued your refund of $40.00 for order O1001. The refund id is R101.") == []
