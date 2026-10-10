# Harness versions

The harness is the simulated user and the loop that drives each trial. A change of harness changes what a score means. For this reason every trajectory records its harness version.

## h1 (first baseline, archived)

The scripted user sent its replies in a fixed order. A task that changes one order got the reply "Yes, please go ahead." two times, whatever the agent said.

Problem found in the error analysis (M5): after a correct refund or cancel, the second "yes" made the agent repeat the action. About one third of the failed trials (36 of 113 in run v0-a, 38 of 112 in run v0-b) contained a repeated write after a successful write. The agent also invented follow-up refunds. A real customer does not confirm an action that is already done. The h1 baseline therefore measured the agent and an unrealistic user together.

The h1 runs are kept in `results/_archive_harness_h1/` for the record. Do not compare them with h2 runs.

## h2 (current)

The scripted user reacts to the agent (see `agent/user.py`):

1. The agent asks a question: the user sends the next scripted reply.
2. The agent makes a statement: the user sends the next planned follow-up that carries new information, if one exists. A task with two requests gets one reminder.
3. Otherwise the conversation ends.

What did not change: the tasks, the expected results, the split, the holdout hash, the graders, the model, the temperature and the number of trials. The change was made before any version was compared, so no iteration result depends on it. The baseline was measured again with h2.

## Known limits of h2

- The user still stops when the agent ends a turn with a statement that gives no answer. An agent that narrates ("I will check the order") and stops fails the task. We count this as a real failure ("gave up early").
- The user does not invent new requests. Replies come from the task script.
