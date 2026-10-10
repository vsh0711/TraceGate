"""The store environment and its 7 tools.
The tools check data integrity only. They do NOT enforce policy.
Policy is the agent's job, and the graders check it."""
import json

from env import seed
from env.policy import days_since

TOOL_NAMES = ["get_customer", "list_orders", "get_order", "cancel_order",
              "issue_refund", "update_address", "transfer_to_human"]
WRITE_TOOLS = {"cancel_order", "issue_refund", "update_address"}

# Parameter schemas. Descriptions live in agent/tool_specs.py (they change per version).
PARAMS = {
    "get_customer": {"email": "string", "zip_code": "string"},
    "list_orders": {"customer_id": "string"},
    "get_order": {"order_id": "string"},
    "cancel_order": {"order_id": "string"},
    "issue_refund": {"order_id": "string", "amount": "number"},
    "update_address": {"order_id": "string", "new_address": "string"},
    "transfer_to_human": {"reason": "string"},
}


class Env:
    def __init__(self):
        self.db = seed.build_db()
        self.initial = seed.snapshot(self.db)
        self._refund_n = 100

    # ---- helpers -------------------------------------------------------
    def order_context(self, order_id: str) -> dict | None:
        """State of an order right now. The runner stores this as `pre` on each tool event."""
        r = self.db.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
        if not r:
            return None
        refunded = self.db.execute("SELECT COALESCE(SUM(amount),0) FROM refunds WHERE order_id=?",
                                   (order_id,)).fetchone()[0]
        final = self.db.execute(
            "SELECT COUNT(*) FROM order_items oi JOIN products p USING(product_id) "
            "WHERE oi.order_id=? AND p.final_sale=1", (order_id,)).fetchone()[0]
        return {"order_id": order_id, "customer_id": r["customer_id"], "status": r["status"],
                "delivered_at": r["delivered_at"], "total": r["total"],
                "refunded_before": round(refunded, 2), "has_final_sale_item": bool(final),
                "days_since_delivery": days_since(r["delivered_at"])}

    def customer_exists(self, customer_id: str) -> bool:
        return self.db.execute("SELECT 1 FROM customers WHERE customer_id=?", (customer_id,)).fetchone() is not None

    def final_state_diff(self) -> dict:
        return seed.diff(self.initial, seed.snapshot(self.db))

    # ---- tools ---------------------------------------------------------
    def call(self, name: str, args: dict) -> dict:
        fn = getattr(self, f"_t_{name}", None)
        if fn is None:
            return {"error": f"Unknown tool: {name}"}
        try:
            return fn(**args)
        except TypeError as e:
            return {"error": f"Bad arguments: {e}"}

    def _t_get_customer(self, email: str, zip_code: str):
        r = self.db.execute("SELECT * FROM customers WHERE lower(email)=lower(?) AND zip_code=?",
                            (email, str(zip_code))).fetchone()
        if not r:
            return {"error": "No customer matches this email and zip code."}
        return {"customer_id": r["customer_id"], "name": r["name"], "email": r["email"]}

    def _t_list_orders(self, customer_id: str):
        if not self.customer_exists(customer_id):
            return {"error": f"Customer {customer_id} not found."}
        rows = self.db.execute("SELECT order_id,status,placed_at,total FROM orders WHERE customer_id=? ORDER BY order_id",
                               (customer_id,)).fetchall()
        return {"orders": [dict(r) for r in rows]}

    def _t_get_order(self, order_id: str):
        r = self.db.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
        if not r:
            return {"error": f"Order {order_id} not found."}
        items = self.db.execute(
            "SELECT p.name, oi.quantity, p.price, p.final_sale FROM order_items oi JOIN products p USING(product_id) "
            "WHERE oi.order_id=?", (order_id,)).fetchall()
        refunds = self.db.execute("SELECT refund_id, amount FROM refunds WHERE order_id=?", (order_id,)).fetchall()
        return {"order_id": order_id, "customer_id": r["customer_id"], "status": r["status"],
                "placed_at": r["placed_at"], "delivered_at": r["delivered_at"], "address": r["address"],
                "total": r["total"],
                "items": [{"name": i["name"], "quantity": i["quantity"], "price": i["price"],
                           "final_sale": bool(i["final_sale"])} for i in items],
                "refunds": [{"refund_id": x["refund_id"], "amount": x["amount"]} for x in refunds]}

    def _t_cancel_order(self, order_id: str):
        r = self.db.execute("SELECT status FROM orders WHERE order_id=?", (order_id,)).fetchone()
        if not r:
            return {"error": f"Order {order_id} not found."}
        if r["status"] == "cancelled":
            return {"error": "Order is already cancelled."}
        self.db.execute("UPDATE orders SET status='cancelled' WHERE order_id=?", (order_id,))
        self.db.commit()
        return {"order_id": order_id, "status": "cancelled"}

    def _t_issue_refund(self, order_id: str, amount: float):
        if not self.db.execute("SELECT 1 FROM orders WHERE order_id=?", (order_id,)).fetchone():
            return {"error": f"Order {order_id} not found."}
        try:
            amount = round(float(amount), 2)
        except (TypeError, ValueError):
            return {"error": "Amount must be a number."}
        if amount <= 0:
            return {"error": "Amount must be more than 0."}
        self._refund_n += 1
        rid = f"R{self._refund_n}"
        self.db.execute("INSERT INTO refunds VALUES (?,?,?,?)", (rid, order_id, amount, "2026-10-01"))
        self.db.commit()
        return {"refund_id": rid, "order_id": order_id, "amount": amount}

    def _t_update_address(self, order_id: str, new_address: str):
        if not self.db.execute("SELECT 1 FROM orders WHERE order_id=?", (order_id,)).fetchone():
            return {"error": f"Order {order_id} not found."}
        self.db.execute("UPDATE orders SET address=? WHERE order_id=?", (new_address, order_id))
        self.db.commit()
        return {"order_id": order_id, "address": new_address}

    def _t_transfer_to_human(self, reason: str):
        return {"status": "transferred", "reason": reason}


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)
