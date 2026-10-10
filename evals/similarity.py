"""Text similarity for (1) dataset dedup and (2) exemplar retrieval.
Uses embeddings from the model API when available, and falls back to TF-IDF cosine."""
import math
import re
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


def embed(texts: list[str]) -> np.ndarray:
    """Return L2-normalised vectors. Tries the embedding API first."""
    try:
        import litellm
        r = litellm.embedding(model=EMBED_MODEL, input=texts)
        X = np.array([d["embedding"] for d in r.data], dtype=float)
        _backend["name"] = "embedding-api"
    except Exception:
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
