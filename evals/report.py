"""Report for one run. Usage: python -m evals.report <run_id>
Writes results/<run_id>/report.md, report.json and traces/*.md (one file per trial)."""
import argparse
import json
from collections import Counter, defaultdict

import numpy as np

from evals.grade import load_grades
from evals.runner import load_trajectories, run_dir
from evals.tasks import load_tasks
from stats import metrics as M

CATEGORIES = ["lookup", "cancel", "refund", "address", "multi", "adversarial"]


def _rate(xs):
    xs = list(xs)
    return float(np.mean(xs)) if xs else float("nan")


def compute(grades: list[dict]) -> dict:
    """All metrics from the brief's section 4, for one set of graded trials."""
    out = {"n_trials": len(grades), "n_tasks": len({g["task_id"] for g in grades})}
    if not grades:
        return out
    pt = M.per_task(grades)
    n = max(len(v) for v in pt.values())
    out["success"] = dict(zip(("rate", "lo", "hi"), M.bootstrap_ci(pt)))
    out["pass_hat"] = {k: M.pass_hat(pt, k) for k in range(1, n + 1)}
    out["pass_at"] = {k: M.pass_at(pt, k) for k in range(1, n + 1)}
    out["by_category"] = {c: _rate(g["success"] for g in grades if g["category"] == c) for c in CATEGORIES
                          if any(g["category"] == c for g in grades)}
    out["by_difficulty"] = {d: _rate(g["success"] for g in grades if g["difficulty"] == d) for d in ("easy", "medium", "hard")
                            if any(g["difficulty"] == d for g in grades)}
    out["grader_pass"] = {k: _rate(g[k]["pass"] for g in grades) for k in ("state", "answer", "policy")}
    out["policy_violation_rate"] = _rate(not g["policy"]["pass"] for g in grades)
    out["policy_violations_by_rule"] = dict(Counter(r for g in grades for r in {v["rule"] for v in g["policy"]["violations"]}))   # trials, not events
    # tools: precision / recall per tool and overall
    tp, fp, fn = Counter(), Counter(), Counter()
    for g in grades:
        tp.update(g["tools"]["tp"]); fp.update(g["tools"]["fp"]); fn.update(g["tools"]["fn"])
    out["tool_pr"] = {t: {"precision": tp[t] / (tp[t] + fp[t]) if tp[t] + fp[t] else None,
                          "recall": tp[t] / (tp[t] + fn[t]) if tp[t] + fn[t] else None}
                      for t in sorted(set(tp) | set(fp) | set(fn))}
    out["tool_precision"] = _rate(g["tools"]["precision"] for g in grades)
    out["tool_recall"] = _rate(g["tools"]["recall"] for g in grades)
    calls = sum(g["args"]["calls"] for g in grades)
    out["arg_schema_valid_rate"] = sum(g["args"]["schema_valid"] for g in grades) / calls if calls else 1.0
    out["arg_entities_real_rate"] = sum(g["args"]["entities_real"] for g in grades) / calls if calls else 1.0
    scored = sum(g["args"]["scored_calls"] for g in grades)
    out["arg_correct_rate"] = sum(g["args"]["correct"] for g in grades) / scored if scored else 1.0
    out["steps_ratio"] = _rate(g["efficiency"]["ratio"] for g in grades)
    out["loop_rate"] = _rate(g["efficiency"]["loop"] for g in grades)
    out["blocked_calls_per_trial"] = _rate(g.get("blocked_calls", 0) for g in grades)
    out["fabricated_entity_rate"] = _rate(g["fab_entity"]["fabricated"] for g in grades)
    out["fabricated_action_rate"] = _rate(g["fab_action"]["fabricated"] for g in grades)
    judged = [g for g in grades if "claims" in g]
    out["n_judged"] = len(judged)
    if judged:
        out["hallucination_rate"] = _rate(g["claims"]["hallucinated"] for g in judged)
        total = sum(g["claims"]["n_claims"] for g in judged)
        out["claim_unsupported_rate"] = sum(g["claims"]["unsupported"] for g in judged) / total if total else 0.0
        out["claim_contradicted_rate"] = sum(g["claims"]["contradicted"] for g in judged) / total if total else 0.0
        out["n_claims"] = total
        ref = [g["refusal"]["pass"] for g in judged if g.get("refusal")]
        out["refusal_explained_rate"] = _rate(ref) if ref else None
    wins = sum(g["success"] for g in grades)
    cost = sum(g["totals"]["cost_usd"] for g in grades)
    out["cost_per_success"] = cost / wins if wins else None
    out["cost_per_trial"] = cost / len(grades)
    out["p95_latency_s"] = M.p95([g["totals"]["latency"] for g in grades])
    out["statuses"] = dict(Counter(g["status"] for g in grades))
    return out


def render_trace(task, traj, g) -> str:
    L = [f"# {task['id']} trial {traj['trial']}: {'PASS' if g['success'] else 'FAIL'}",
         f"- version: {traj['version']}  status: {traj['status']}  category: {g['category']}  split: {g['split']}",
         f"- request: {task['input'][0]}",
         f"- expected change: `{json.dumps(task['expected'])}`",
         f"- actual change: `{json.dumps(traj['final_diff'])}`",
         f"- graders: state={g['state']['pass']} answer={g['answer']['pass']} policy={g['policy']['pass']} "
         f"fab_entity={g['fab_entity']['fabricated']} fab_action={g['fab_action']['fabricated']}"]
    for v in g["policy"]["violations"]:
        L.append(f"- POLICY {v['rule']}: {v['detail']}")
    for it in g["fab_entity"]["items"]:
        L.append(f"- FABRICATED ENTITY: {it}")
    for it in g["fab_action"]["items"]:
        L.append(f"- FABRICATED ACTION: {it['sentence']}")
    for c in g.get("claims", {}).get("claims", []):
        if c["label"] != "supported":
            L.append(f"- CLAIM {c['label'].upper()}: {c['claim']} ({c['reason']})")
    L.append("\n## Trajectory")
    for e in traj["events"]:
        if e["type"] in ("user", "assistant"):
            L.append(f"**{e['type'].upper()}**: {e['content']}")
        elif e["type"] == "tool":
            tag = " [BLOCKED]" if e.get("blocked") else ""
            L.append(f"**TOOL** `{e['name']}({json.dumps(e['args'])})`{tag} -> `{json.dumps(e['output'])}`")
        else:
            L.append(f"**{e['type'].upper()}**: {e.get('content')}")
    return "\n\n".join(L) + "\n"


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def examples(grades, pred, k=3):
    hits = [g for g in grades if pred(g)][:k]
    return ", ".join(f"[{g['task_id']}/t{g['trial']}](traces/{g['task_id']}_t{g['trial']}.md)" for g in hits) or "none"


def write_report(run_id: str):
    grades, trajs = load_grades(run_id), {(t["task_id"], t["trial"]): t for t in load_trajectories(run_id)}
    tasks = {t["id"]: t for t in load_tasks()}
    d = run_dir(run_id)
    (d / "traces").mkdir(exist_ok=True)
    for g in grades:
        tr = trajs[(g["task_id"], g["trial"])]
        (d / "traces" / f"{g['task_id']}_t{g['trial']}.md").write_text(render_trace(tasks[g["task_id"]], tr, g))
    cfg = json.loads((d / "config.json").read_text())
    res = {"config": cfg, "all": compute(grades), "dev": compute([g for g in grades if g["split"] == "dev"]),
           "holdout": compute([g for g in grades if g["split"] == "holdout"])}
    (d / "report.json").write_text(json.dumps(res, indent=2, default=str))

    L = [f"# Run report: {run_id}", "",
         f"Version **{cfg['version']}** ({cfg['version_note']}). Model `{cfg['model']}`, temperature {cfg['temperature']}, "
         f"{cfg['trials']} trials per task, {cfg['n_tasks']} tasks. Dataset v{next(iter(tasks.values()))['dataset_version'][1:]}."
         " Cost is a notional price (see config.py), not a real invoice.", ""]
    for split in ("all", "dev", "holdout"):
        m = res[split]
        if not m.get("n_trials"):
            continue
        s = m["success"]
        L += [f"## Split: {split} ({m['n_tasks']} tasks, {m['n_trials']} trials)", "",
              "| Metric | Value |", "|---|---|",
              f"| Success rate (95% CI, bootstrap over tasks) | {pct(s['rate'])} ({pct(s['lo'])} to {pct(s['hi'])}) |"]
        for k in m["pass_hat"]:
            L.append(f"| pass^{k} / pass@{k} | {pct(m['pass_hat'][k])} / {pct(m['pass_at'][k])} |")
        L += [f"| Outcome graders passing: state / answer / policy | {pct(m['grader_pass']['state'])} / {pct(m['grader_pass']['answer'])} / {pct(m['grader_pass']['policy'])} |",
              f"| Policy violation rate | {pct(m['policy_violation_rate'])} |",
              f"| Tool selection precision / recall | {pct(m['tool_precision'])} / {pct(m['tool_recall'])} |",
              f"| Args: schema-valid / real entities / correct | {pct(m['arg_schema_valid_rate'])} / {pct(m['arg_entities_real_rate'])} / {pct(m['arg_correct_rate'])} |",
              f"| Efficiency: steps / reference steps; loop rate | {m['steps_ratio']:.2f}; {pct(m['loop_rate'])} |",
              f"| Guardrail blocks per trial | {m['blocked_calls_per_trial']:.2f} |",
              f"| Fabricated entity rate | {pct(m['fabricated_entity_rate'])} |",
              f"| Fabricated action rate | {pct(m['fabricated_action_rate'])} |"]
        if m.get("n_judged"):
            L += [f"| Hallucination rate (response level, judge) | {pct(m['hallucination_rate'])} |",
                  f"| Claim-level unsupported / contradicted rate ({m['n_claims']} claims) | {pct(m['claim_unsupported_rate'])} / {pct(m['claim_contradicted_rate'])} |",
                  f"| Refusal explained (judge, refusal tasks) | {pct(m.get('refusal_explained_rate'))} |"]
        cps = m["cost_per_success"]
        L += [f"| Notional cost per successful task | {'n/a' if cps is None else f'${cps:.4f}'} |",
              f"| p95 latency per trial (model time) | {m['p95_latency_s']:.1f} s |", ""]
        L += ["| Category | Success |", "|---|---|"] + [f"| {c} | {pct(v)} |" for c, v in m["by_category"].items()]
        L += ["", "| Difficulty | Success |", "|---|---|"] + [f"| {c} | {pct(v)} |" for c, v in m["by_difficulty"].items()]
        L += ["", "| Tool | Precision | Recall |", "|---|---|---|"] + \
             [f"| {t} | {pct(v['precision'])} | {pct(v['recall'])} |" for t, v in m["tool_pr"].items()]
        if m["policy_violations_by_rule"]:
            L += ["", "| Policy rule broken | Trials |", "|---|---|"] + \
                 [f"| {r} | {c} |" for r, c in sorted(m["policy_violations_by_rule"].items())]
        L.append("")
    L += ["## Examples to click through", "",
          f"- Failed trials: {examples(grades, lambda g: not g['success'])}",
          f"- Policy violations: {examples(grades, lambda g: not g['policy']['pass'])}",
          f"- Fabricated entities: {examples(grades, lambda g: g['fab_entity']['fabricated'])}",
          f"- Fabricated actions: {examples(grades, lambda g: g['fab_action']['fabricated'])}",
          f"- Hallucinated (judge): {examples(grades, lambda g: g.get('claims', {}).get('hallucinated'))}",
          f"- Looped: {examples(grades, lambda g: g['efficiency']['loop'])}"]
    (d / "report.md").write_text("\n".join(L) + "\n")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("run_id")
    a = ap.parse_args()
    r = write_report(a.run_id)
    s = r["all"]["success"]
    print(f"{a.run_id}: success {pct(s['rate'])} ({pct(s['lo'])} to {pct(s['hi'])}); report in results/{a.run_id}/report.md")
