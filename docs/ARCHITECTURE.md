# TZMICHA AI OS - Architecture

## System Design

```
Customer Phone Call
       │
       ▼
┌─────────────┐
│  Telephony  │  Twilio (abstracted)
│   Adapter   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  STT Engine │────▶│ Conversation│
│  (Deepgram) │     │   Engine    │
└─────────────┘     └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │  Memory  │ │ Knowledge│ │ Workflow  │
       │  Engine  │ │  (RAG)   │ │  Engine   │
       └──────────┘ └──────────┘ └──────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ LLM Provider │  Groq/OpenAI/Ollama
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Voice        │
                    │ Enhancer     │  Fillers, pauses, emotion
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  TTS Engine  │  ElevenLabs/Piper
                    └──────┬───────┘
                           │
                           ▼
                   Customer Hears AI
```

## Provider Architecture

Every external service is behind an interface. Switch by config only:

```
.env: LLM_PROVIDER=groq     → Uses Groq
.env: LLM_PROVIDER=ollama   → Uses Ollama (local)
.env: LLM_PROVIDER=openai   → Uses GPT-4
```

Zero code changes needed to switch providers.
