"""
Conversation memory: store and retrieve chat history for context.
"""


class Memory:
    def __init__(self, max_messages: int = 6):
        self.history: list[dict] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages :]

    def get_history(self) -> list[dict]:
        return self.history
