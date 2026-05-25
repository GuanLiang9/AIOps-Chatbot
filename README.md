# ARIA — AIOps Chatbot

**AI-powered ITSM assistant** for IT support chat, incident classification, severity estimation, and troubleshooting recommendations.

Built with Python · FastAPI · Ollama (local LLM) · HTML/CSS/JS — **zero API cost, zero signup**.

---

## Features

| Feature | Description |
|---------|-------------|
| 💬 AI Chat | Conversational IT support powered by a local LLM |
| 🔍 Incident Analyzer | Paste any incident → get summary, category, severity, assignment group, and troubleshooting steps |
| 📊 Severity Estimation | Automatic P1–P4 classification with SLA guidance |
| 👥 Assignment Routing | AI-suggested assignment group based on incident type |
| 📋 Sample Incidents | 10 realistic ITSM incidents across all IT categories |
| 🔶 Mock Fallback | Works without Ollama — returns intelligent templated responses |

---

## Quick Start

### 1. Install Ollama (one-time)

Download and install from [ollama.com](https://ollama.com), then pull a model:

```bash
ollama pull llama3.2
```

Keep Ollama running in the background:
```bash
ollama serve
```

> **No Ollama?** The app still works — it falls back to intelligent mock responses automatically.

### 2. Set up Python environment

```bash
cd "AIOps Chatbot"
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env
```

The default `.env` works out of the box with Ollama. Edit `OLLAMA_MODEL` to use a different model (e.g. `mistral`, `llama3.1`).

### 4. Start the server

```bash
uvicorn backend.main:app --reload
```

Open **http://localhost:8000** in your browser.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server status, AI mode, model name |
| `POST` | `/api/chat` | Chat message |
| `DELETE` | `/api/chat/{session_id}` | Clear conversation |
| `GET` | `/api/incidents/samples` | List all sample incidents |
| `POST` | `/api/incidents/analyze` | Analyze a custom incident |
| `POST` | `/api/incidents/analyze-sample/{id}` | Analyze a sample by ID |

Interactive docs: **http://localhost:8000/docs**

### Chat request/response

```json
POST /api/chat
{ "message": "My laptop won't connect to VPN", "session_id": null }

→ { "response": "...", "session_id": "uuid", "ai_mode": "ollama" }
```

### Incident analysis request/response

```json
POST /api/incidents/analyze
{
  "title": "Email server down",
  "description": "Exchange server not responding since 09:00...",
  "affected_users": 300
}

→ {
  "summary": "...",
  "category": "Email/Communication",
  "severity": "P2",
  "severity_label": "High",
  "assignment_group": "Application Support",
  "troubleshooting_steps": ["...", "..."],
  "estimated_resolution_time": "2-4 hours",
  "confidence_score": 0.88,
  "ai_mode": "ollama"
}
```

---

## Project Structure

```
AIOps Chatbot/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── models/              # Pydantic request/response models
│   ├── services/            # AI, chat, and incident business logic
│   ├── routers/             # API endpoint handlers
│   ├── prompts/             # LLM prompt templates
│   ├── data/                # Sample incident JSON data
│   └── utils/               # Logging
├── frontend/
│   ├── index.html           # Single-page app
│   ├── style.css            # Dark enterprise theme
│   └── app.js               # UI logic and API calls
├── requirements.txt
└── .env.example
```

---

## Supported Ollama Models

| Model | Size | Notes |
|-------|------|-------|
| `llama3.2` (default) | ~2 GB | Fast, good quality |
| `llama3.1` | ~4 GB | Higher quality |
| `mistral` | ~4 GB | Strong reasoning |
| `phi3` | ~2 GB | Lightweight |

Change model: edit `OLLAMA_MODEL` in `.env`.

---

## Future Enhancements

- **Streaming chat** — word-by-word response via SSE
- **RAG knowledge base** — embed IT documentation, retrieve context
- **Ticket similarity search** — find related past incidents via embeddings
- **Trend dashboard** — charts for incident volume, severity distribution
- **LangSmith tracing** — observability for LLM calls
- **Multi-provider support** — swap Ollama for cloud provider via env var

---
The current implementation is a proof-of-concept using simulated incident telemetry and static alert datasets. The architecture is designed to later support real-time integrations with observability and cloud monitoring platforms such as CloudWatch, Grafana, and Prometheus.
