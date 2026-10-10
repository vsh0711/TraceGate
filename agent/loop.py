"""The agent loop: model call -> tool calls -> tool results -> repeat. Every step is logged."""
import hashlib
import json
import time

import config
from agent import llm
from agent.tool_specs import tool_schemas
from agent.versions import VERSIONS, system_prompt
from env.policy import refund_block_reason
from env.tools import Env, dumps


def stable_seed(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) % (2**31)


def run_trial(task: dict, version: str, trial: int, salt: str = "", user=None, exemplars: str = "",
              use_cache: bool = True, model: str | None = None, tool_desc_override: dict | None = None) -> dict:
    """Run one trial of one task. Return the trajectory (a plain dict)."""
    from agent.user import ScriptedUser
    cfg = VERSIONS[version]
    model = model or config.AGENT_MODEL
    env = Env()
    user = user or ScriptedUser(task["input"])
    tools = tool_schemas(tool_desc_override or cfg["descriptions"])
    seed = stable_seed(task["id"], trial, salt)
    system = system_prompt(version, exemplars)

    messages = [{"role": "system", "content": system}]
    events = []   # the logged trajectory
    totals = {"prompt_tokens": 0, "completion_tokens": 0, "latency": 0.0, "llm_calls": 0}
    t_start = time.time()

    def add_user(text):
        messages.append({"role": "user", "content": text})
        events.append({"type": "user", "content": text})

    add_user(user.first())
    status = "max_steps"
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
                blocked = None
                if cfg["validator"] and name == "issue_refund" and pre:
                    try:
                        blocked = refund_block_reason(pre, float(args.get("amount", 0)))
                    except (TypeError, ValueError):
                        blocked = "The refund amount must be a number."
                if blocked:
                    out = {"error": f"BLOCKED_BY_POLICY: {blocked}"}
                else:
                    out = env.call(name, args)
                events.append({"type": "tool", "name": name, "args": args, "output": out,
                               "ok": "error" not in out, "blocked": bool(blocked), "pre": pre, "usage": usage})
                messages.append({"role": "tool", "tool_call_id": c["id"], "content": dumps(out)})
            continue

        text = r["content"] or ""
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
            "status": status, "events": events, "final_diff": env.final_state_diff(),
            "totals": {**totals, "latency": round(totals["latency"], 3),
                       "wall": round(time.time() - t_start, 3),
                       "cost_usd": llm.cost_usd(totals["prompt_tokens"], totals["completion_tokens"])}}
