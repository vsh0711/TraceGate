"""Build the trajectory that a perfect agent would produce for a task. Used to test task validity."""
from env.tools import WRITE_TOOLS, Env


def reference_trajectory(task) -> dict:
    env = Env()
    ev = [{"type": "user", "content": task["input"][0]}]
    msgs = list(task["input"][1:])          # the scripted replies, in order
    calls = task["reference_calls"]
    reads = [c for c in calls if c["name"] not in WRITE_TOOLS]
    writes = [c for c in calls if c["name"] in WRITE_TOOLS]

    def ask_user(question):
        ev.append({"type": "assistant", "content": question, "final": False})
        ev.append({"type": "user", "content": msgs.pop(0)})

    def run(c):
        args = c["args"]
        pre = env.order_context(args["order_id"]) if "order_id" in args else None
        out = env.call(c["name"], args)
        ev.append({"type": "tool", "name": c["name"], "args": args, "output": out, "ok": "error" not in out,
                   "blocked": False, "pre": pre})
        return out

    if task["tags"].get("sub") == "no_identity":      # the customer gives the identity only when asked
        ask_user("Please give me your email and zip code.")
    for c in reads:
        if "error" in run(c):                         # for example a mistyped email: ask again
            ask_user("That did not match our records. Please check it and try again.")
    if writes:
        ask_user("I will make the change. Do you confirm?")
        for c in writes:
            run(c)
    final = " ".join(task["answer_contains"]) or "I have helped with your request."
    if not writes:
        final = " ".join(task["answer_contains"]) or "I am sorry, I cannot do this under the store policy."
    ev.append({"type": "assistant", "content": final, "final": True})
    return {"task_id": task["id"], "version": "ref", "trial": 0, "status": "completed", "events": ev,
            "final_diff": env.final_state_diff(),
            "totals": {"prompt_tokens": 0, "completion_tokens": 0, "latency": 0, "wall": 0, "cost_usd": 0, "llm_calls": 1}}
