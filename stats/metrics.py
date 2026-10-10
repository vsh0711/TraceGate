"""Statistics for the eval: pass^k, pass@k, bootstrap over tasks, paired tests, flip rate."""
from math import comb

import numpy as np


def pass_hat_k(n: int, c: int, k: int) -> float:
    """P(all k sampled trials succeed). tau-bench's pass^k."""
    return comb(c, k) / comb(n, k)


def pass_at_k(n: int, c: int, k: int) -> float:
    """P(at least one of k sampled trials succeeds)."""
    return 1 - comb(n - c, k) / comb(n, k)


# A "per_task" value is {task_id: [bool, ...]} (one bool per trial).
def per_task(grades: list[dict], key=lambda g: g["success"]) -> dict[str, list[bool]]:
    out: dict[str, list[bool]] = {}
    for g in sorted(grades, key=lambda g: (g["task_id"], g["trial"])):
        out.setdefault(g["task_id"], []).append(bool(key(g)))
    return out


def success_rate(pt: dict) -> float:
    return float(np.mean([np.mean(v) for v in pt.values()])) if pt else float("nan")


def pass_hat(pt: dict, k: int) -> float:
    vals = [pass_hat_k(len(v), sum(v), k) for v in pt.values() if len(v) >= k]
    return float(np.mean(vals)) if vals else float("nan")


def pass_at(pt: dict, k: int) -> float:
    vals = [pass_at_k(len(v), sum(v), k) for v in pt.values() if len(v) >= k]
    return float(np.mean(vals)) if vals else float("nan")


def bootstrap_ci(pt: dict, stat=success_rate, B: int = 2000, seed: int = 0, alpha: float = 0.05):
    """95% CI by resampling TASKS (not trials). Returns (point, low, high)."""
    ids = list(pt)
    rng = np.random.default_rng(seed)
    est = []
    for _ in range(B):
        pick = rng.integers(0, len(ids), len(ids))
        est.append(stat({i: pt[ids[j]] for i, j in enumerate(pick)}))
    return stat(pt), float(np.nanpercentile(est, 100 * alpha / 2)), float(np.nanpercentile(est, 100 * (1 - alpha / 2)))


def paired_bootstrap_diff(pt_a: dict, pt_b: dict, stat=success_rate, B: int = 2000, seed: int = 0):
    """CI of stat(B) - stat(A) on the SAME tasks. Returns (diff, low, high)."""
    ids = sorted(set(pt_a) & set(pt_b))
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(B):
        pick = rng.integers(0, len(ids), len(ids))
        a = {i: pt_a[ids[j]] for i, j in enumerate(pick)}
        b = {i: pt_b[ids[j]] for i, j in enumerate(pick)}
        diffs.append(stat(b) - stat(a))
    point = stat({i: pt_b[i] for i in ids}) - stat({i: pt_a[i] for i in ids})
    return float(point), float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def mcnemar_majority(pt_a: dict, pt_b: dict) -> dict:
    """Exact McNemar test on per-task success (a task succeeds if more than half of its trials succeed)."""
    from statsmodels.stats.contingency_tables import mcnemar
    ids = sorted(set(pt_a) & set(pt_b))
    maj = lambda v: sum(v) * 2 > len(v)
    b = sum(maj(pt_a[i]) and not maj(pt_b[i]) for i in ids)   # A ok, B fail
    c = sum(not maj(pt_a[i]) and maj(pt_b[i]) for i in ids)   # A fail, B ok
    ok = sum(maj(pt_a[i]) and maj(pt_b[i]) for i in ids)
    bad = len(ids) - ok - b - c
    p = mcnemar([[ok, b], [c, bad]], exact=True).pvalue
    return {"a_only": b, "b_only": c, "both": ok, "neither": bad, "p_value": float(p)}


def flip_rate(grades_a: list[dict], grades_b: list[dict], key=lambda g: g["success"]) -> float:
    """Share of (task, trial) outcomes that differ between two identical runs."""
    a = {(g["task_id"], g["trial"]): bool(key(g)) for g in grades_a}
    b = {(g["task_id"], g["trial"]): bool(key(g)) for g in grades_b}
    keys = sorted(set(a) & set(b))
    return sum(a[k] != b[k] for k in keys) / len(keys) if keys else float("nan")


def p95(values: list[float]) -> float:
    return float(np.percentile(values, 95)) if values else float("nan")
