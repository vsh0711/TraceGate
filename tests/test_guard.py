from agent.guard import Guard
from env.tools import Env


def ctx(order_id):
    return Env().order_context(order_id)


def verified_guard():
    g = Guard()
    g.update("get_customer", {}, {"customer_id": "C1"})
    return g


def test_blocks_order_tools_before_verification():
    assert "Identity is not verified" in Guard().check("get_order", {"order_id": "O1001"}, ctx("O1001"))


def test_blocks_write_before_get_order():
    g = verified_guard()
    assert "Read the order first" in g.check("cancel_order", {"order_id": "O1002"}, ctx("O1002"))
    g.update("get_order", {}, {"order_id": "O1002"})
    assert g.check("cancel_order", {"order_id": "O1002"}, ctx("O1002")) is None


def test_blocks_guessed_ids_and_other_customers_orders():
    g = verified_guard()
    assert g.check("cancel_order", {"order_id": "get_order"}, None)
    g.update("get_order", {}, {"order_id": "O1004"})          # O1004 belongs to C2
    assert "does not belong" in g.check("update_address", {"order_id": "O1004", "new_address": "x"}, ctx("O1004"))


def test_status_and_refund_rules():
    g = verified_guard()
    for oid in ("O1001", "O1003", "O1002"):
        g.update("get_order", {}, {"order_id": oid})
    assert "processing" in g.check("update_address", {"order_id": "O1001", "new_address": "x"}, ctx("O1001"))
    assert g.check("issue_refund", {"order_id": "O1001", "amount": 40.0}, ctx("O1001")) is None
    assert "more than 0" in g.check("issue_refund", {"order_id": "O1001", "amount": 400}, ctx("O1001"))
    assert "30 days" in g.check("issue_refund", {"order_id": "O1003", "amount": 45}, ctx("O1003"))
    g3 = Guard()
    g3.update("get_customer", {}, {"customer_id": "C3"})      # O1008 belongs to C3 and has a final-sale item
    g3.update("get_order", {}, {"order_id": "O1008"})
    assert "final-sale" in g3.check("issue_refund", {"order_id": "O1008", "amount": 20}, ctx("O1008"))
    assert "delivered" in g.check("issue_refund", {"order_id": "O1002", "amount": 5}, ctx("O1002"))


def test_failed_tool_results_do_not_unlock_anything():
    g = Guard()
    g.update("get_customer", {}, {"error": "No customer matches"})
    assert g.verified is None
