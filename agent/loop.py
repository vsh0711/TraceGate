"""The agent loop: model call -> tool calls -> tool results -> repeat. Every step is logged."""
import hashlib
import json
import time

import config
from agent import llm
from agent.answer_check import check as check_answer
from agent.guard import Guard
from agent.tool_specs import tool_schemas
from agent.versions import VERSIONS, system_prompt
from env.tools import Env, dumps


def stable_seed(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) % (2**31)


def run_trial(task: dict, version: str, trial: int, salt: str = "", user=None, exemplars: str = "",
              use_cache: bool = True, model: str | None = None, tool_desc_override: dict | None = None) -> dict:
    """Run one trial of one task. Return the trajectory (a plain dict)."""
    from agent.user import HARNESS_VERSION, ScriptedUser
    cfg = VERSIONS[version]
    model = model or config.AGENT_MODEL
    env = Env()
    user = user or ScriptedUser(task["input"])
    tools = tool_schemas(tool_desc_override or cfg["descriptions"])
    seed = stable_seed(task["id"], trial, salt)
    system = system_prompt(version, exemplars)

    guard = Guard() if cfg["validator"] else None
    messages = [{"role": "system", "content": system}]
    events = []   # the logged trajectory
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "latency": 0.0, "llm_calls": 0}
    t_start = time.time()

    def add_user(text):
        messages.append({"role": "user", "content": text})
        events.append({"type": "user", "content": text})

    add_user(user.first())
    status = "max_steps"
    rewritten = False
    for step in range(config.MAX_STEPS):
        try:
            r = llm.complete(model, messages, tools, config.TEMPERATURE, config.MAX_TOKENS, seed + step, use_cache)
        except Exception as e:  # model call failed after retries
            status = "error"
            events.append({"type": "error", "content": str(e)[:300]})
            break
        totals["prompt_tokens"] += r["prompt_tokens"]
        totals["completion_tokens"] += r["completion_tokens"]
        totals["latency"] += r["latency"]
        totals["llm_calls"] += 1
        usage = {"prompt_tokens": r["prompt_tokens"], "completion_tokens": r["completion_tokens"],
                 "latency": r["latency"], "cached": r["cached"]}

        if r["tool_calls"]:
            messages.append({"role": "assistant", "content": r["content"] or None, "tool_calls": [
                {"id": c["id"], "type": "function",
                 "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                for c in r["tool_calls"]]})
            if r["content"]:
                events.append({"type": "assistant", "content": r["content"], "usage": usage})
            for c in r["tool_calls"]:
                name, args = c["name"], c["arguments"]
                pre = env.order_context(args["order_id"]) if isinstance(args.get("order_id"), str) else None
                blocked = guard.check(name, args, pre) if guard else None
                if blocked:
                    out = {"error": f"BLOCKED_BY_POLICY: {blocked}"}
                    if cfg.get("remediate") and blocked.startswith("Read the order first") and pre is not None:
                        # Remediation (v5): the system reads the order for the agent, logs that read as a tool event, and
                        # returns the real order data in the error. The agent still decides what to do next.
                        order = env.call("get_order", {"order_id": args["order_id"]})
                        if "error" not in order:
                            guard.update("get_order", {"order_id": args["order_id"]}, order)
                            events.append({"type": "tool", "name": "get_order", "args": {"order_id": args["order_id"]}, "output": order,
                                           "ok": True, "blocked": False, "auto": True, "pre": pre, "usage": usage})
                            out = {"error": f"BLOCKED_BY_POLICY: {blocked}", "order_now_read_by_system": order,
                                   "next_step": "Use these real values. Check the policy. Then retry, or explain to the customer why you cannot."}
                else:
                    out = env.call(name, args)
                    if guard:
                        guard.update(name, args, out)
                events.append({"type": "tool", "name": name, "args": args, "output": out,
                               "ok": "error" not in out, "blocked": bool(blocked), "pre": pre, "usage": usage})
                messages.append({"role": "tool", "tool_call_id": c["id"], "content": dumps(out)})
            continue

        text = r["content"] or ""
        if cfg.get("answer_check") and not rewritten:
            problems = check_answer(events, text)
            if problems:                      # one chance to rewrite the draft answer
                rewritten = True
                note = ("SYSTEM CHECK: your draft answer has problems. " + " ".join(problems) +
                        " Rewrite the answer. State only facts that tool results or the customer gave you, and say that an action is done only if its tool call succeeded.")
                events.append({"type": "validator", "draft": text, "problems": problems, "usage": usage})
                messages.append({"role": "assistant", "content": text})
                messages.append({"role": "user", "content": note})
                continue
        rewritten = False
        messages.append({"role": "assistant", "content": text})
        events.append({"type": "assistant", "content": text, "usage": usage, "final": False})
        nxt = user.reply(text)
        if nxt is None:
            status = "completed"
            break
        add_user(nxt)

    for e in reversed(events):   # mark the last assistant text as the final answer
        if e["type"] == "assistant":
            e["final"] = True
            break
    return {"task_id": task["id"], "version": version, "trial": trial, "salt": salt, "model": model,
            "harness": HARNESS_VERSION, "status": status, "events": events, "final_diff": env.final_state_diff(),
            "totals": {**totals, "latency": round(totals["latency"], 3),
                       "wall": round(time.time() - t_start, 3),
                       "cost_usd": llm.cost_usd(totals["prompt_tokens"], totals["completion_tokens"])}}
