# TZMICHA AI OS

**Enterprise AI Voice Platform — AI Employees that sound human.**

Build AI workers (Receptionist, Sales Executive, HR Recruiter, Support Agent) that make and receive phone calls like real humans. One platform, any industry.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/tzmicha/ai-os.git
cd ai-os

# 2. Setup environment
cp .env.example .env
# Add your API keys to .env

# 3. Run infrastructure
docker compose up -d

# 4. Run backend
cd apps/api
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8000

# 5. Open
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              TZMICHA AI OS                    │
├─────────────────────────────────────────────┤
│                                              │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│   │ Voice   │  │ Conver- │  │Knowledge│   │
│   │ Engine  │  │ sation  │  │ Engine  │   │
│   │(STT+TTS)│  │ Engine  │  │  (RAG)  │   │
│   └────┬────┘  └────┬────┘  └────┬────┘   │
│        │             │             │         │
│   ┌────┴─────────────┴─────────────┴────┐   │
│   │         Provider Adapters            │   │
│   │  Groq│OpenAI│Deepgram│ElevenLabs    │   │
│   └─────────────────────────────────────┘   │
│                                              │
├─────────────────────────────────────────────┤
│  PostgreSQL │ Redis │ Qdrant │ Twilio       │
└─────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Frontend | Next.js 15 (coming soon) |
| Database | PostgreSQL |
| Cache | Redis |
| Vector DB | Qdrant |
| LLM | Groq / OpenAI / Ollama / Anthropic |
| STT | Deepgram / Whisper |
| TTS | ElevenLabs / Piper |
| Telephony | Twilio |
| Container | Docker |

---

## Project Structure

```
ai-os/
├── apps/
│   ├── api/              ← Backend (FastAPI Voice Engine)
│   └── web/              ← Frontend (Next.js 15 - coming soon)
├── packages/
│   └── shared/           ← Shared types, utils
├── infra/
│   ├── docker/           ← Dockerfiles per service
│   ├── nginx/            ← Reverse proxy config
│   └── scripts/          ← Deploy & setup scripts
├── docs/                 ← Documentation
├── docker-compose.yml    ← Local development
├── docker-compose.prod.yml ← Production
├── Makefile              ← Common commands
└── .env.example          ← Environment template
```

---

## License

Proprietary - TZMICHA Technologies
