from datetime import datetime, timezone
from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request: Request):
    state = request.app.state
    return {
        "status": "healthy",
        "ai_mode": state.ai_mode,
        "model": state.model_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
