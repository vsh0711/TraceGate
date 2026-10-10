"""Scripted user (harness version h2). It reacts to the agent instead of sending replies in a fixed order.

Rules:
1. The agent asks a question  -> send the next scripted reply (an answer, "yes", or "no, that is all").
2. The agent makes a statement -> send the next planned follow-up that carries new information, if one exists.
   For a task with two requests, send ONE reminder ("Is everything in my request done?").
   Otherwise the conversation ends.
This stops a repeated "yes" from pushing the agent to repeat an action that is already done (harness h1 problem)."""
import re

HARNESS_VERSION = "h2"
YES_PREFIX = "yes, please go ahead"
BYE_PREFIX = "no, that is all"
ASK = re.compile(r"\?|\b(confirm|proceed|go ahead|would you like|do you want|shall i|please provide|can you|could you)\b", re.I)
REMINDER = "Thank you. Is everything in my request done?"


class ScriptedUser:
    def __init__(self, messages: list[str]):
        self.first_message = messages[0]
        self.queue = list(messages[1:])
        goal = self.first_message.split(". ", 1)[-1]   # skip the identity sentence ("... and my zip code is 94107.")
        self.multi = bool(re.search(r"\b(and|also)\b", goal, re.I))
        self.reminded = False

    def first(self) -> str:
        return self.first_message

    @staticmethod
    def _plain(msg: str) -> bool:
        low = msg.lower()
        return low.startswith(YES_PREFIX) or low.startswith(BYE_PREFIX)

    def reply(self, agent_text: str):
        if ASK.search(agent_text):
            return self.queue.pop(0) if self.queue else None
        for i, m in enumerate(self.queue):          # a planned follow-up with new information
            if not self._plain(m):
                del self.queue[: i + 1]
                return m
        if self.multi and not self.reminded:
            self.reminded = True
            return REMINDER
        return None
