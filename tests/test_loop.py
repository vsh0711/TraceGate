"""The agent loop with a fake model: the guard and the remediation of v5."""
import json

import pytest

from agent import loop
from evals.tasks import load_tasks


def fake_model(script):
    """Return a replacement for llm.complete that plays the scripted answers in order."""
    it = iter(script)

    def complete(model, messages, tools, temperature, max_tokens, seed, use_cache):
        r = next(it)
        return {"content": r.get("content", ""), "tool_calls": r.get("calls", []), "prompt_tokens": 1,
                "completion_tokens": 1, "latency": 0.0, "cached": False}
    return complete


def call(i, name, **args):
    return {"id": f"c{i}", "name": name, "arguments": args}


TASK = {"id": "TX", "input": ["Hi, my email is alice.nguyen@example.com and my zip code is 94107. Please cancel order O1002.", "Yes, please go ahead."]}
SCRIPT = [{"calls": [call(1, "get_customer", email="alice.nguyen@example.com", zip_code="94107")]},
          {"content": "I will cancel O1002. Do you confirm?"},
          {"calls": [call(2, "cancel_order", order_id="O1002")]},        # no get_order first: the guard blocks it
          {"calls": [call(3, "cancel_order", order_id="O1002")]},        # the retry
          {"content": "Order O1002 is cancelled."}]


def run(version, monkeypatch):
    monkeypatch.setattr(loop.llm, "complete", fake_model(SCRIPT))
    return loop.run_trial(TASK, version, 0, use_cache=False)


def test_v2_blocks_a_write_before_get_order_and_the_retry_is_still_blocked(monkeypatch):
    t = run("v2", monkeypatch)
    cancels = [e for e in t["events"] if e["type"] == "tool" and e["name"] == "cancel_order"]
    assert [e["blocked"] for e in cancels] == [True, True]            # the agent never read the order
    assert t["final_diff"]["orders"] == {}


def test_v5_reads_the_order_for_the_agent_and_then_allows_the_retry(monkeypatch):
    t = run("v5", monkeypatch)
    tools = [e for e in t["events"] if e["type"] == "tool"]
    assert [e["name"] for e in tools] == ["get_customer", "get_order", "cancel_order", "cancel_order"]
    assert tools[1].get("auto") and tools[1]["ok"]                      # logged as a system read
    assert tools[2]["blocked"] and "order_now_read_by_system" in tools[2]["output"]
    assert tools[3]["ok"] and not tools[3]["blocked"]
    assert t["final_diff"]["orders"] == {"O1002": {"status": "cancelled"}}
