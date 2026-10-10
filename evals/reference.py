"""Build the trajectory that a perfect agent would produce for a task. Used to test task validity."""
from env.tools import WRITE_TOOLS, Env


def reference_trajectory(task) -> dict:
    env = Env()
    ev = [{"type": "user", "content": task["input"][0]}]
    calls = task["reference_calls"]
    reads = [c for c in calls if c["name"] not in WRITE_TOOLS]
    writes = [c for c in calls if c["name"] in WRITE_TOOLS]

    def run(c):
        args = c["args"]
        pre = env.order_context(args["order_id"]) if "order_id" in args else None
        out = env.call(c["name"], args)
        ev.append({"type": "tool", "name": c["name"], "args": args, "output": out, "ok": "error" not in out,
                   "blocked": False, "pre": pre})

    for c in reads:
        run(c)
    if writes:
        ev.append({"type": "assistant", "content": "I will make the change. Do you confirm?", "final": False})
        ev.append({"type": "user", "content": task["input"][1]})
        for c in writes:
            run(c)
    final = " ".join(task["answer_contains"]) or "I have helped with your request."
    if not writes:
        final = " ".join(task["answer_contains"]) or "I am sorry, I cannot do this under the store policy."
    ev.append({"type": "assistant", "content": final, "final": True})
    return {"task_id": task["id"], "version": "ref", "trial": 0, "status": "completed", "events": ev,
            "final_diff": env.final_state_diff(),
            "totals": {"prompt_tokens": 0, "completion_tokens": 0, "latency": 0, "wall": 0, "cost_usd": 0, "llm_calls": 1}}
