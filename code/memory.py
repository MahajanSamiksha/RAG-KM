from langchain_core.chat_history import InMemoryChatMessageHistory

# Global session store
session_store = {}

def get_memory(session_id: str):
    """Returns the chat history object for a given session_id."""
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

def get_full_chat_history(session_id: str):
    """Returns the full chat history (list of messages) for a session."""
    if session_id in session_store:
        return session_store[session_id].messages
    return []

def export_history_to_markdown(session_id: str, file_path: str):
    history = get_full_chat_history(session_id)
    with open(file_path, "w", encoding="utf-8") as f:
        for msg in history:
            role = msg.type.capitalize()
            f.write(f"**{role}:** {msg.content}\n\n")

def clear_memory(session_id: str):
    """Clears the chat history for a given session_id."""
    if session_id in session_store:
        del session_store[session_id]
    return