"""M4: compare the judge with your hand labels. Report TPR, TNR, Cohen's kappa on judge-test.
  python -m evals.judge_validation [--split judge-test|judge-dev] [--model MODEL]
The POSITIVE class is "bad" (hallucination or failed refusal), so TPR = share of real failures that the judge catches,
and TNR = share of good outputs that the judge does not flag."""
import argparse
import json
import random
from pathlib import Path

import config
from evals.graders import judge
from evals.graders.common import final_answer
from evals.label import LABELS
from evals.runner import load_trajectories
from evals.tasks import load_tasks

PAD = (" Thank you very much for contacting our store today. We really value your loyalty, and we hope that you have "
       "a wonderful and relaxing day. Please do not hesitate to reach out again if there is anything else at all that we can do.")


def kappa(y_true, y_pred) -> float:
    n = len(y_true)
    po = sum(a == b for a, b in zip(y_true, y_pred)) / n
    pe = sum((sum(a == c for a in y_true) / n) * (sum(b == c for b in y_pred) / n) for c in set(y_true) | set(y_pred))
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def confusion(y_true, y_pred) -> dict:
    tp = sum(t and p for t, p in zip(y_true, y_pred)); fn = sum(t and not p for t, p in zip(y_true, y_pred))
    tn = sum((not t) and (not p) for t, p in zip(y_true, y_pred)); fp = sum((not t) and p for t, p in zip(y_true, y_pred))
    return {"tp": tp, "fn": fn, "tn": tn, "fp": fp, "n": len(y_true),
            "tpr": tp / (tp + fn) if tp + fn else None, "tnr": tn / (tn + fp) if tn + fp else None,
            "kappa": kappa(y_true, y_pred) if y_true else None}


def run(split: str, model: str | None, bias_n: int = 20) -> dict:
    labels = [l for l in map(json.loads, Path(LABELS).read_text().splitlines()) if l["judge_split"] == split]
    tasks = {t["id"]: t for t in load_tasks()}
    trajs = {}
    claim_h, claim_j, trial_h, trial_j, ref_h, ref_j = [], [], [], [], [], []
    stability = {"position_same": 0, "position_total": 0, "pad_same": 0, "pad_total": 0}
    rng = random.Random(0)
    for i, l in enumerate(labels):
        trajs.setdefault(l["run"], {(t["task_id"], t["trial"]): t for t in load_trajectories(l["run"])})
        traj, task = trajs[l["run"]][(l["task_id"], l["trial"])], tasks[l["task_id"]]
        ev = judge.transcript(traj)
        claims = [c["claim"] for c in l["claims"]]
        got = judge.label_claims(claims, ev, model)       # same claims as the human labeled
        for h, j in zip(l["claims"], got):
            claim_h.append(h["label"] != "supported"); claim_j.append(j["label"] != "supported")
        trial_h.append(l["hallucinated"]); trial_j.append(any(j["label"] != "supported" for j in got))
        if l["refusal_pass"] is not None:
            r = judge.grade_refusal(task, traj, model)
            ref_h.append(not l["refusal_pass"]); ref_j.append(not r["pass"])
        if i < bias_n and len(claims) > 1:                # position bias: reverse the claim order
            rev = judge.label_claims(claims[::-1], ev, model)[::-1]
            stability["position_total"] += len(claims)
            stability["position_same"] += sum((a["label"] != "supported") == (b["label"] != "supported") for a, b in zip(got, rev))
        if i < bias_n:                                    # verbosity bias: pad the answer with polite filler
            padded = {**traj, "events": [dict(e, content=e["content"] + PAD) if e.get("final") else e for e in traj["events"]]}
            pg = judge.grade_claims(task, padded, model)
            stability["pad_total"] += 1
            stability["pad_same"] += pg["hallucinated"] == trial_j[-1]   # the verdict must not change
    return {"split": split, "model": model or config.JUDGE_MODEL, "judge_version": config.JUDGE_PROMPT_VERSION,
            "n_trials": len(labels), "claim_level": confusion(claim_h, claim_j), "trial_level": confusion(trial_h, trial_j),
            "refusal": confusion(ref_h, ref_j) if ref_h else None, "bias": stability}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="judge-test")
    ap.add_argument("--model")
    a = ap.parse_args()
    res = run(a.split, a.model)
    Path(f"results/judge_validation_{a.split}_{config.JUDGE_PROMPT_VERSION}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
