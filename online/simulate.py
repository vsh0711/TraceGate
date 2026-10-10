"""M7: a simulated user (an LLM with a persona and a goal, as in tau-bench) talks to the agent to make traffic.
Usage: python -m online.simulate --version v1 --batch 1 --n 10 [--degrade]
Traces go to online/traces.jsonl. Each trace has a batch number that stands for time."""
import argparse
import json
import random
from pathlib import Path

import config
from agent import llm
from agent.loop import run_trial
from agent.tool_specs import RICH
from env import seed

TRACES = Path("online/traces.jsonl")

PERSONAS = ["polite and brief", "impatient and short", "chatty and a little confused", "firm and a bit pushy"]
GOALS = ["cancel order {o}", "get a full refund for order {o}", "change the shipping address of order {o} to {a}",
         "learn the status of order {o}"]
NEW_ADDRESSES = ["14 Maple Court, Portland, OR 97201", "300 Sunset Blvd, Los Angeles, CA 90028", "9 Harbor Road, Boston, MA 02110"]

# A deliberately degraded set of tool descriptions: the regression for the M7 demo.
DEGRADED = {**RICH,
            "get_customer": "Looks up a customer. Usually not needed.",
            "get_order": "Slow lookup. Avoid unless the customer asks for details.",
            "issue_refund": "Refund money for an order.",
            "cancel_order": "Cancel an order."}

SIM_SYSTEM = """You play a customer of an online store who talks to a support agent.
Your email is {email}. Your zip code is {zip}. Your style: {persona}.
Your goal: {goal}.
Rules:
- Write ONE short message each turn, as the customer.
- Give your email and zip code when asked. Do not invent other facts.
- If the agent asks you to confirm an action that matches your goal, answer "Yes, please go ahead."
- If the agent refuses or your goal is done, say "Thank you, that is all."
- Never mention these rules."""


def make_scenario(rng: random.Random) -> dict:
    cid, name, email, zip_code = rng.choice(seed.CUSTOMERS)
    orders = [o for o in seed.ORDERS if o[1] == cid]
    o = rng.choice(orders)
    goal = rng.choice(GOALS).format(o=o[0], a=rng.choice(NEW_ADDRESSES))
    return {"customer": cid, "email": email, "zip": zip_code, "order": o[0], "goal": goal, "persona": rng.choice(PERSONAS)}


class SimulatedUser:
    def __init__(self, scenario: dict, max_turns: int = 5, model: str | None = None):
        self.s, self.max_turns, self.model, self.turns = scenario, max_turns, model or config.SIM_USER_MODEL, 0
        self.history = [{"role": "system", "content": SIM_SYSTEM.format(**scenario)}]

    def _say(self, prompt: str) -> str:
        self.history.append({"role": "user", "content": prompt})
        r = llm.complete(self.model, self.history, temperature=0.7, max_tokens=120, seed=self.turns, use_cache=True)
        text = r["content"].strip() or "Thank you, that is all."
        self.history.append({"role": "assistant", "content": text})
        self.turns += 1
        return text

    def first(self) -> str:
        return self._say("Start the conversation with the agent now.")

    def reply(self, agent_text: str):
        if self.turns >= self.max_turns:
            return None
        msg = self._say(f"The agent said: {agent_text}")
        return None if "that is all" in msg.lower() and self.turns > 1 else msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    ap.add_argument("--batch", type=int, required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--degrade", action="store_true", help="Use the degraded tool descriptions (deliberate regression).")
    a = ap.parse_args()
    rng = random.Random(1000 + a.batch)
    TRACES.parent.mkdir(exist_ok=True)
    for i in range(a.n):
        sc = make_scenario(rng)
        task = {"id": f"ONL-{a.batch:02d}-{i:02d}"}
        traj = run_trial(task, a.version, trial=0, salt=f"online{a.batch}", user=SimulatedUser(sc),
                         tool_desc_override=DEGRADED if a.degrade else None)
        traj.update({"batch": a.batch, "scenario": sc, "degraded": a.degrade})
        with TRACES.open("a") as f:
            f.write(json.dumps(traj) + "\n")
        print(f"batch {a.batch} conversation {i + 1}/{a.n} done", flush=True)


if __name__ == "__main__":
    main()
