from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None, description="Omit to start a new session")


class ChatResponse(BaseModel):
    response: str
    session_id: str
    ai_mode: str    # "ollama" or "mock"
