class ConversationMemory:

    _memory = {}

    @classmethod
    def save(cls, session_id, question, answer):
        cls._memory[session_id] = {
            "question": question,
            "answer": answer
        }

    @classmethod
    def get(cls, session_id):
        return cls._memory.get(session_id)

    @classmethod
    def clear(cls, session_id):
        if session_id in cls._memory:
            del cls._memory[session_id]