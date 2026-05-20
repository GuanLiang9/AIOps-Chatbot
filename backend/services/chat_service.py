import uuid
from backend.config import settings
from backend.prompts.templates import CHAT_SYSTEM_PROMPT
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory session store: {session_id: [{"role": ..., "content": ...}]}
_sessions: dict[str, list[dict]] = {}


class ChatService:
    def __init__(self, ai_service, ai_mode: str):
        self._ai = ai_service
        self.ai_mode = ai_mode

    def get_or_create_session(self, session_id: str | None) -> str:
        if session_id and session_id in _sessions:
            return session_id
        new_id = str(uuid.uuid4())
        _sessions[new_id] = []
        logger.info("Created new chat session: %s", new_id)
        return new_id

    def reply(self, session_id: str, user_message: str) -> str:
        history = _sessions.setdefault(session_id, [])

        history.append({"role": "user", "content": user_message})

        # Keep sliding window to control context size
        window = history[-settings.MAX_CHAT_HISTORY :]

        response_text = self._ai.chat_completion(
            messages=window,
            system=CHAT_SYSTEM_PROMPT,
        )

        history.append({"role": "assistant", "content": response_text})

        # Trim stored history to MAX_CHAT_HISTORY messages
        if len(history) > settings.MAX_CHAT_HISTORY:
            _sessions[session_id] = history[-settings.MAX_CHAT_HISTORY :]

        logger.info("Session %s | user: %.60s… | reply: %.60s…", session_id, user_message, response_text)
        return response_text

    def clear_session(self, session_id: str) -> None:
        _sessions.pop(session_id, None)
