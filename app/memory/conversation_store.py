class ConversationStore:

    def __init__(self):
        self.conversations = {}

    def get(self, conversation_id: str) -> list[dict]:
        return self.conversations.get(conversation_id, [])

    def save(self, conversation_id: str, history: list[dict]):
        self.conversations[conversation_id] = history

    def clear(self, conversation_id: str):
        self.conversations.pop(conversation_id, None)