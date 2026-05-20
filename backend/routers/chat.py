from fastapi import APIRouter, Request, HTTPException
from backend.models.chat import ChatRequest, ChatResponse
from backend.utils.logger import get_logger

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = get_logger(__name__)


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request):
    chat_svc = request.app.state.chat_service

    try:
        session_id = chat_svc.get_or_create_session(payload.session_id)
        response_text = chat_svc.reply(session_id, payload.message)
    except Exception as exc:
        logger.error("Chat error: %s", exc)
        raise HTTPException(status_code=500, detail="AI service error. Please try again.")

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        ai_mode=chat_svc.ai_mode,
    )


@router.delete("/{session_id}")
async def clear_session(session_id: str, request: Request):
    request.app.state.chat_service.clear_session(session_id)
    return {"message": "Session cleared", "session_id": session_id}
