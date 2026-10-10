"""Tool descriptions. Two sets exist. v0 is short. RICH adds when-to-use and prerequisites."""
from env.tools import PARAMS, TOOL_NAMES

TERSE = {
    "get_customer": "Look up a customer.",
    "list_orders": "List orders.",
    "get_order": "Get an order.",
    "cancel_order": "Cancel an order.",
    "issue_refund": "Issue a refund.",
    "update_address": "Change the address of an order.",
    "transfer_to_human": "Transfer to a human agent.",
}

RICH = {
    "get_customer": "Verify the customer's identity. Call this FIRST, before any other tool. "
                    "Needs the customer's email and zip code. Returns customer_id. "
                    "An error means the identity is NOT verified: do not continue.",
    "list_orders": "List the order ids, statuses and totals for one verified customer_id. "
                   "Use it when the customer does not know the order id. Needs customer_id from get_customer.",
    "get_order": "Read one order: status, delivered_at, items (with final_sale flag), total, address, "
                 "refunds and customer_id. ALWAYS call it before cancel_order, issue_refund or update_address. "
                 "Check that customer_id is the verified customer.",
    "cancel_order": "WRITE ACTION. Cancel one order. Allowed only when the order status is 'processing'. "
                    "Ask the customer to confirm first. Never call it for shipped, delivered or cancelled orders.",
    "issue_refund": "WRITE ACTION. Refund money for one order. Allowed only when status is 'delivered', "
                    "delivered 30 days ago or less, no final_sale item, and no earlier refund. "
                    "amount must be more than 0 and not more than the order total. Ask the customer to confirm first.",
    "update_address": "WRITE ACTION. Change the shipping address of one order. Allowed only when the order "
                      "status is 'processing'. Ask the customer to confirm first.",
    "transfer_to_human": "Transfer the customer to a human. Use it only when the customer asks for a person, "
                         "or when the request needs a decision that the policy does not cover.",
}

PARAM_DOC = {
    "email": "Customer email address.", "zip_code": "Customer zip code, as text.",
    "customer_id": "Customer id such as C1.", "order_id": "Order id such as O1001.",
    "amount": "Refund amount in US dollars.", "new_address": "The full new address.",
    "reason": "Short reason for the transfer.",
}


def tool_schemas(descriptions: dict) -> list[dict]:
    out = []
    for name in TOOL_NAMES:
        props = {p: {"type": t, "description": PARAM_DOC[p]} for p, t in PARAMS[name].items()}
        out.append({"type": "function", "function": {
            "name": name, "description": descriptions[name],
            "parameters": {"type": "object", "properties": props,
                           "required": list(PARAMS[name]), "additionalProperties": False}}})
    return out
