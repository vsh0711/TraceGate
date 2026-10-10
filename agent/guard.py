"""Guardrail (version v2): a validator that runs BEFORE each tool call and blocks calls that break the policy.
A blocked call does not run. The agent gets an error that says what to do first, and it can try again.
The guard keeps its own state (verified customer, orders read), taken only from tool results."""
from env.policy import refund_block_reason

ORDER_TOOLS = {"list_orders", "get_order", "cancel_order", "issue_refund", "update_address"}
WRITES = {"cancel_order", "issue_refund", "update_address"}


class Guard:
    def __init__(self):
        self.verified: str | None = None   # customer_id from a successful get_customer
        self.read: set[str] = set()        # order ids that get_order returned

    def check(self, name: str, args: dict, pre: dict | None) -> str | None:
        """Return a reason to block the call, or None to allow it."""
        if name in ORDER_TOOLS and self.verified is None:
            return "Identity is not verified. Call get_customer with the customer's email and zip code first. Do not continue without a successful result."
        if name == "list_orders" and args.get("customer_id") != self.verified:
            return "list_orders works only for the verified customer_id."
        if name in WRITES:
            oid = args.get("order_id")
            if not isinstance(oid, str) or oid not in self.read:
                return f"Read the order first. Call get_order with the real order_id before {name}. Do not guess ids or amounts."
            if pre and pre["customer_id"] != self.verified:
                return "This order does not belong to the verified customer. Do not change it."
            if pre and name in ("cancel_order", "update_address") and pre["status"] != "processing":
                return f"Policy: {name} is allowed only when the status is 'processing'. This order is '{pre['status']}'."
            if pre and name == "issue_refund":
                try:
                    return refund_block_reason(pre, float(args.get("amount", 0)))
                except (TypeError, ValueError):
                    return "The refund amount must be a number."
        return None

    def update(self, name: str, args: dict, out: dict):
        """Record what a tool call proved. Only successful calls count."""
        if "error" in out:
            return
        if name == "get_customer":
            self.verified = out["customer_id"]
        elif name == "get_order":
            self.read.add(out["order_id"])
