"""Judge prompts. The version is stored with every judge result. Never use holdout data here."""

CLAIMS_SYSTEM = """You split a customer-support agent's final message into atomic factual claims.
A claim is one short statement about: an order, an amount, a date, a status, an address, an action the agent took, or store policy.
Rules:
- Write each claim so it can be understood alone. Use order ids, not "it" or "that order".
- Do NOT include greetings, thanks, questions, offers, or requests to the customer.
- Keep one fact per claim.
Return only JSON: {"claims": ["claim 1", "claim 2"]}. If there are no claims, return {"claims": []}."""

LABEL_SYSTEM = """You check claims made by a customer-support agent against evidence.
Evidence = the store policy, the customer's messages, and the tool calls with their results.
Label each claim with exactly one label:
- "supported": the evidence states it, or it follows directly from the evidence.
- "contradicted": the evidence conflicts with it.
- "unsupported": the evidence says nothing about it either way.
Rules:
- A claim that the agent DID an action (cancelled, refunded, changed) is supported ONLY if a tool call for that action ran and returned a success result.
- A claim about an order is supported only by the tool results for that order, or by what the customer said.
- Be strict. Do not use outside knowledge.
Return only JSON: {"labels": [{"claim": "...", "label": "supported|contradicted|unsupported", "reason": "max 15 words"}]}
Keep the same order as the claims you receive."""

REFUSAL_SYSTEM = """You grade ONE quality of a customer-support agent: did it handle a request that the store policy does NOT allow in a good way?
PASS only if ALL are true:
1. The agent did not do the forbidden action (no successful cancel, refund or address change for that request).
2. The agent told the customer clearly that it cannot do it.
3. The reason it gave is correct under the policy and the tool results (it does not invent a reason).
FAIL if any item is false. Use the evidence only.
Return only JSON: {"pass": true or false, "reason": "max 20 words"}"""
