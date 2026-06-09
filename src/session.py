from langchain.schema import HumanMessage, AIMessage

_sessions: dict[str, list] = {}


def get_session_history(session_id: str) -> list:
    return _sessions.get(session_id, [])


def save_session_message(session_id: str, role: str, content: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    if role == "user":
        _sessions[session_id].append(HumanMessage(content=content))
    else:
        _sessions[session_id].append(AIMessage(content=content))


def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]
