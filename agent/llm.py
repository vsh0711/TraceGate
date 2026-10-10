"""One function for every model call. It adds a disk cache and retries."""
import hashlib
import json
import os
import threading
import time
from pathlib import Path

import litellm

import config

litellm.drop_params = True
litellm.suppress_debug_info = True
CACHE_DIR = Path(".cache/llm")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
_lock = threading.Lock()
_last_call = {}


def _key(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def complete(model: str, messages: list, tools: list | None = None, temperature: float = 0.0,
             max_tokens: int = 512, seed: int | None = None, use_cache: bool = True,
             min_interval: float = 0.0) -> dict:
    """Return {content, tool_calls:[{id,name,arguments}], prompt_tokens, completion_tokens, latency, cached}.
    `min_interval` spaces calls to one model (used for free-tier API limits)."""
    payload = {"model": model, "messages": messages, "tools": tools, "temperature": temperature,
               "max_tokens": max_tokens, "seed": seed}
    path = CACHE_DIR / f"{_key(payload)}.json"
    if use_cache and path.exists():
        out = json.loads(path.read_text())
        out["cached"] = True
        return out

    kwargs = dict(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    if tools:
        kwargs["tools"] = tools
    if seed is not None:
        kwargs["seed"] = seed
    if model.startswith("ollama"):
        kwargs["num_ctx"] = config.NUM_CTX
        kwargs["keep_alive"] = "30m"

    last_err = None
    for attempt in range(6):
        if min_interval:
            with _lock:
                wait = _last_call.get(model, 0) + min_interval - time.time()
                if wait > 0:
                    time.sleep(wait)
                _last_call[model] = time.time()
        t0 = time.time()
        try:
            resp = litellm.completion(**kwargs)
            break
        except Exception as e:  # network, rate limit, bad tool-call output
            last_err = e
            time.sleep(3 * 2 ** attempt)
    else:
        raise RuntimeError(f"Model call failed after retries: {last_err}")
    latency = time.time() - t0
    msg = resp.choices[0].message
    calls = []
    for i, tc in enumerate(getattr(msg, "tool_calls", None) or []):
        raw = tc.function.arguments
        try:
            args = json.loads(raw) if isinstance(raw, str) else dict(raw or {})
        except json.JSONDecodeError:
            args = {"__raw__": raw}
        calls.append({"id": tc.id or f"call_{i}", "name": tc.function.name, "arguments": args})
    usage = getattr(resp, "usage", None)
    out = {"content": msg.content or "", "tool_calls": calls,
           "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
           "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
           "latency": round(latency, 3), "cached": False}
    if use_cache:
        tmp = path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
        tmp.write_text(json.dumps(out))
        tmp.replace(path)
    return out


def cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens * config.NOTIONAL_PRICE_IN + completion_tokens * config.NOTIONAL_PRICE_OUT) / 1e6
