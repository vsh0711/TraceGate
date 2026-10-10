"""Scripted user. It sends the next scripted message each time the agent ends a turn with text."""


class ScriptedUser:
    def __init__(self, messages: list[str]):
        self._messages = list(messages)
        self._i = 0

    def first(self) -> str:
        return self._next()

    def reply(self, _agent_text: str) -> str | None:
        return self._next()

    def _next(self):
        if self._i >= len(self._messages):
            return None
        m = self._messages[self._i]
        self._i += 1
        return m
