from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.services.ai_service import get_ai_service
from backend.services.chat_service import ChatService
from backend.services.incident_service import IncidentService
from backend.routers import health, chat, incidents
from backend.utils.logger import get_logger

logger = get_logger(__name__)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialise services once and attach to app state
    ai_service, ai_mode = get_ai_service()
    app.state.ai_mode = ai_mode
    app.state.model_name = settings.OLLAMA_MODEL if ai_mode == "ollama" else "mock"
    app.state.chat_service = ChatService(ai_service, ai_mode)
    app.state.incident_service = IncidentService(ai_service, ai_mode)

    logger.info("AIOps Chatbot started | mode=%s | model=%s", ai_mode, app.state.model_name)
    yield
    logger.info("AIOps Chatbot shutting down")


app = FastAPI(
    title="AIOps Chatbot",
    description="AI-powered ITSM assistant — incident analysis, classification, and IT support chat",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(incidents.router)

# Serve frontend at root — must be last so API routes take precedence
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
