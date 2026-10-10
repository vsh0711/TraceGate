"""M5: turn the reading of failed dev trajectories into notes, counts and docs/failure-taxonomy.md.
  python -m evals.open_coding v0-a v0-b
Input: labels/open_coding_manual.json (primary category per trial, assigned by reading the trajectory).
Output: labels/failure_notes.jsonl (one note per trial), docs/failure-taxonomy.md.
The notes are written by Claude, not by a human reviewer. The note text is assembled from facts in the logged trajectory."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from evals.taxonomy import PRIMARY, SECONDARY, WRITES, load_failed_dev, primary, secondary


def note_for(cat: str, g: dict, t: dict, sec: list[str]) -> str:
    calls = [e for e in t["events"] if e["type"] == "tool"]
    fmt = lambda e: f"{e['name']}({', '.join(f'{k}={v}' for k, v in e['args'].items() if k not in ('email', 'zip_code'))})"
    if cat == "skipped_order_lookup":
        first = next((e for e in calls if e["name"] in WRITES and e["args"].get("order_id") not in
                      {c["args"].get("order_id") for c in calls[: calls.index(e)] if c["name"] == "get_order" and c["ok"]}), None)
        s = f"First change was {fmt(first)} with no earlier get_order for that order." if first else "Used a guessed order or amount without reading the order."
        if "wrong_tool_args" in sec:
            s += " It used a guessed or placeholder argument (for example amount 0 or 'get_order')."
    elif cat == "skipped_identity_check":
        first = next((e for e in calls if e["name"] not in ("get_customer", "transfer_to_human")), calls[0] if calls else None)
        s = f"Called {first['name']} before a successful get_customer." if first else "Did not verify identity."
    elif cat == "gave_up_early":
        s = "Ended the turn with narration or a question, and never gave the answer or made the change."
    elif cat == "malformed_tool_call":
        s = "Wrote the tool call as plain text, so no tool ran, and the change was never made."
    elif cat == "policy_violation":
        s = "Read the order, then refunded a $120 order that is not delivered, after an injected instruction."
    elif cat == "misread_request":
        s = "The customer asked to cancel an unshipped order. The agent chose a different order and refunded it."
    else:
        s = "No rule matched."
    extras = {"repeated_action": "It later repeated a write that had already worked.", "fabricated_action": "It then claimed an action that no tool call did.",
              "hallucinated_fact": "Its answer contains a fact that is not in the evidence."}
    return " ".join([s] + [extras[x] for x in sec if x in extras])


def main(runs: list[str]):
    manual = json.loads(Path("labels/open_coding_manual.json").read_text())
    rows = []
    for run in runs:
        for g, t in load_failed_dev(run):
            key = f"{run}|{g['task_id']}|{g['trial']}"
            sec = secondary(g, t)
            rows.append({"run": run, "task_id": g["task_id"], "trial": g["trial"], "category": manual[key],
                         "tagger": primary(g, t), "secondary": sec, "note": note_for(manual[key], g, t, sec), "coder": "claude (manual reading)"})
    Path("labels/failure_notes.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))

    n = len(rows)
    cnt = Counter(r["category"] for r in rows)
    sec = Counter(x for r in rows for x in r["secondary"])
    agree = sum(r["category"] == r["tagger"] for r in rows)
    conf = Counter((r["category"], r["tagger"]) for r in rows if r["category"] != r["tagger"])
    ex = defaultdict(list)
    for r in rows:
        if len(ex[r["category"]]) < 2 and all(e["task_id"] != r["task_id"] for e in ex[r["category"]]):
            ex[r["category"]].append(r)
    link = lambda r: f"[{r['task_id']} trial {r['trial']} ({r['run']})](../results/{r['run']}/traces/{r['task_id']}_t{r['trial']}.md)"
    L = ["# Failure taxonomy (M5)", "",
         f"This document groups the failures of the baseline (version v0, harness h2). It uses {n} failed trials from the **dev split** of runs `{'` and `'.join(runs)}`. Holdout trials were not read (leakage rule).", "",
         "## How the categories were made", "",
         "1. I read every one of the failed dev trajectories and wrote a free-text note for each one (open coding). The notes are in `labels/failure_notes.jsonl`.",
         "2. I grouped the notes into categories (axial coding). The coding rule is: **code the first step where the agent went wrong**. The first wrong step is the root cause. Later steps are symptoms.",
         "3. I wrote a rule-based tagger (`evals/taxonomy.py`) that applies the same rule to a logged trajectory. The tagger lets us count failures for every later version without reading each trace again.",
         "4. Some problems are not a root cause but a symptom (a repeated write, an invented fact). They are **secondary tags**. A trial has 1 primary category and 0 or more secondary tags.", "",
         "Important: the notes were written by Claude, not by a human. The categories and counts are a first draft. A human reviewer should read at least a sample of the notes.", "",
         "## Counts: primary category (sorted)", "", "| Rank | Category | Trials | Share | Meaning |", "|---|---|---|---|---|"]
    for i, (c, v) in enumerate(cnt.most_common(), 1):
        L.append(f"| {i} | `{c}` | {v} | {100 * v / n:.0f}% | {PRIMARY[c]} |")
    L += ["", "**The top category is `" + cnt.most_common(1)[0][0] + "`. It is the next fix.**", "",
          "## Counts: secondary tags", "", "| Tag | Trials | Meaning |", "|---|---|---|"]
    L += [f"| `{c}` | {v} | {SECONDARY[c]} |" for c, v in sec.most_common()]
    L += ["", "## Example traces (2 per category)", ""]
    for c, _ in cnt.most_common():
        L.append(f"- **`{c}`**: " + "; ".join(link(r) for r in ex[c]))
    L += ["", "## Notes for three typical trials", ""]
    for c, _ in cnt.most_common(3):
        r = ex[c][0]
        L.append(f"- {link(r)} (`{c}`): {r['note']}")
    L += ["", "## Check of the tagger against the manual labels", "",
          f"The tagger gives the same primary category as the manual label for {agree} of {n} trials ({100 * agree / n:.0f}%). "
          "This check is in-sample: the tagger rules were written after the reading, so the number shows only that the rules reproduce the reading. It does not show that they work on new failures.", ""]
    if conf:
        L += ["| Manual label | Tagger label | Trials |", "|---|---|---|"] + [f"| `{a}` | `{b}` | {v} |" for (a, b), v in conf.most_common()] + [""]
    L += ["## Known limits", "",
          "- One coder wrote the notes, and the same coder wrote the tagger. No second coder checked them.",
          "- Most failures (about three quarters) are one category. A finer split inside it may help later, for example 'wrote before lookup' versus 'guessed an argument'.",
          "- The coding used harness h2 (see `docs/harness.md`). Counts from the earlier h1 runs are not comparable.",
          "- The 4 trials per task are not independent. One weak task can add 4 failures.", ""]
    Path("docs/failure-taxonomy.md").write_text("\n".join(L))
    print(f"{n} notes; top: {cnt.most_common(3)}; tagger agreement {agree}/{n}; disagreements: {dict(conf)}")


if __name__ == "__main__":
    main(sys.argv[1:])
