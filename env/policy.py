"""Policy facts as code. The graders and the guardrail share these helpers."""
from datetime import date

from config import TODAY

REFUND_WINDOW_DAYS = 30


def days_since(d: str | None) -> int | None:
    if not d:
        return None
    return (date.fromisoformat(TODAY) - date.fromisoformat(d)).days


def refund_block_reason(pre: dict, amount: float) -> str | None:
    """Return the first policy reason that blocks this refund, or None if it is allowed.
    `pre` is the order state before the refund (see Env.order_context)."""
    if pre["status"] != "delivered":
        return "Only delivered orders can be refunded."
    age = days_since(pre["delivered_at"])
    if age is None or age > REFUND_WINDOW_DAYS:
        return f"The delivery was more than {REFUND_WINDOW_DAYS} days ago."
    if pre["has_final_sale_item"]:
        return "Orders with a final-sale item cannot be refunded."
    if pre["refunded_before"] > 0:
        return "This order already has a refund."
    if amount <= 0 or round(amount, 2) > round(pre["total"], 2):
        return "The refund amount must be more than 0 and not more than the order total."
    return None
