# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

Python is managed by **uv** (installed at `~/.local/bin/uv.exe`). Use it for all Python commands:

```bash
# Start dev server (hot reload)
uv run uvicorn backend.main:app --reload

# Start on a specific port
uv run uvicorn backend.main:app --reload --port 8080

# Install / sync dependencies
uv pip install -r requirements.txt
```

App runs at `http://localhost:8000`. Swagger UI at `http://localhost:8000/docs`.

## Environment

Copy `.env.example` to `.env`. No API keys are required — the app uses Ollama locally.

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2     # any model pulled via `ollama pull <name>`
LOG_LEVEL=INFO
MAX_CHAT_HISTORY=20
```

**AI mode is determined at startup**, not per-request. On startup, `get_ai_service()` in `backend/services/ai_service.py` calls `ollama.list()` as a connectivity check. If Ollama is unreachable, the app runs in `mock` mode for the entire session. The `/health` endpoint reports the current mode.

## Architecture

### Request flow

```
HTTP request → FastAPI router (backend/routers/)
                   ↓
             Service layer (backend/services/)
                   ↓
        AI service (OllamaAIService or MockAIService)
                   ↓
             Pydantic response model → JSON
```

### Service wiring

Services are instantiated **once at startup** in `backend/main.py` via the `lifespan` context manager and attached to `app.state`. Routers access them through `request.app.state` — there is no FastAPI `Depends()` injection currently.

### AI service design

`backend/services/ai_service.py` defines two classes with an identical interface:
- `OllamaAIService` — calls local Ollama; uses `format="json"` for structured outputs
- `MockAIService` — keyword-matching fallback; deterministic responses, no LLM needed

Both expose:
- `chat_completion(messages: list[dict], system: str) -> str`
- `structured_completion(prompt: str, system: str) -> dict`

To add a new AI provider, implement these two methods and wire it into `get_ai_service()`.

### Chat session state

`backend/services/chat_service.py` stores all sessions in a **module-level dict** (`_sessions`). This is intentional for a POC — state is in-process, not persisted. Sessions are capped at `MAX_CHAT_HISTORY` messages (sliding window).

### Incident analysis

`backend/services/incident_service.py` makes a single `structured_completion()` call that returns all fields at once: summary, category, severity (P1–P4), assignment group, troubleshooting steps, ETA, and confidence score. The expected JSON schema is embedded directly in `INCIDENT_ANALYSIS_PROMPT_TEMPLATE` in `backend/prompts/templates.py`.

### Frontend

Pure HTML/CSS/JS — no build step, no framework. FastAPI serves it as `StaticFiles` mounted at `/` (registered last in `main.py` so API routes take precedence). All API calls use `fetch()` against the same origin. The three tabs (Chat, Incident Analyzer, Sample Incidents) are pure DOM switching — no routing library.

## Adding features

**New AI capability**: Add a prompt template to `backend/prompts/templates.py`, add a method to `IncidentService` or `ChatService`, add a router endpoint, add the same method to `MockAIService` for fallback.

**New endpoint**: Add a file in `backend/routers/`, include it in `backend/main.py` with `app.include_router(...)`.

**Changing the LLM model**: Set `OLLAMA_MODEL` in `.env` and restart. Any model available via `ollama list` works.
