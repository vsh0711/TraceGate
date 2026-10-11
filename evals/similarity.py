"""Text similarity for (1) dataset dedup and (2) exemplar retrieval.
Uses embeddings from the model API when available, and falls back to TF-IDF cosine."""
import hashlib
import json
import math
import os
import re
import time
from pathlib import Path
from collections import Counter

import numpy as np

EMBED_MODEL = "gemini/gemini-embedding-001"
_backend = {"name": None}


def _tokens(t: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", t.lower())


def _tfidf(texts: list[str]) -> np.ndarray:
    docs = [Counter(_tokens(t)) for t in texts]
    vocab = sorted({w for d in docs for w in d})
    idx = {w: i for i, w in enumerate(vocab)}
    df = Counter(w for d in docs for w in d)
    X = np.zeros((len(texts), len(vocab)))
    for i, d in enumerate(docs):
        for w, c in d.items():
            X[i, idx[w]] = (1 + math.log(c)) * math.log((1 + len(texts)) / (1 + df[w]) + 1)
    return X


EMB_CACHE = Path(".cache/emb")


def _embed_api(texts: list[str]) -> list[list[float]]:
    """Embed with the API. Each text is cached on disk. A per-minute rate limit is waited out, not skipped."""
    import litellm
    from agent.llm import _retry_delay
    EMB_CACHE.mkdir(parents=True, exist_ok=True)
    paths = [EMB_CACHE / (hashlib.sha256(f"{EMBED_MODEL}|{t}".encode()).hexdigest() + ".json") for t in texts]
    missing = [i for i, p in enumerate(paths) if not p.exists()]
    for start in range(0, len(missing), 20):
        chunk = missing[start:start + 20]
        for attempt in range(8):
            try:
                r = litellm.embedding(model=EMBED_MODEL, input=[texts[i] for i in chunk])
                for i, d in zip(chunk, r.data):
                    paths[i].write_text(json.dumps(d["embedding"]))
                break
            except Exception as e:
                wait = _retry_delay(str(e))
                if wait is None or wait > 600 or attempt == 7:
                    raise
                time.sleep(min(wait + 1, 70))
    return [json.loads(p.read_text()) for p in paths]


def embed(texts: list[str]) -> np.ndarray:
    """Return L2-normalised vectors. Uses the embedding API when a key is set. It falls back to TF-IDF only when no
    key is set or the daily quota is gone. The backend that was used is reported by backend()."""
    X = None
    if os.environ.get("GEMINI_API_KEY"):
        try:
            X = np.array(_embed_api(texts), dtype=float)
            _backend["name"] = "embedding-api"
        except Exception as e:
            print(f"WARNING: embedding API failed ({str(e)[:80]}); using TF-IDF", flush=True)
    if X is None:
        X = _tfidf(texts)
        _backend["name"] = "tfidf"
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(n == 0, 1, n)


def backend() -> str | None:
    return _backend["name"]


def most_similar(query: str, corpus: list[str], k: int = 2) -> list[tuple[int, float]]:
    X = embed([query] + corpus)
    sims = X[1:] @ X[0]
    order = np.argsort(-sims)[:k]
    return [(int(i), float(sims[i])) for i in order]


def is_duplicate(text: str, existing: list[str], threshold: float = 0.88) -> bool:
    if not existing:
        return False
    return most_similar(text, existing, 1)[0][1] >= threshold
