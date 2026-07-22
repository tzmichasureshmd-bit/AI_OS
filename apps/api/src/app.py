"""
TZMICHA AI OS - Main Application
Entry point. Dependency injection wires all services together.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .providers.factory import ProviderFactory
from .services.memory import MemoryService
from .services.language import LanguageService
from .services.knowledge import KnowledgeService
from .services.workflow import WorkflowService
from .services.voice_enhancer import VoiceEnhancer
from .services.conversation import ConversationService
from .services.voice_call import VoiceCallService
from .api import router, inject_services


@asynccontextmanager
async def lifespan(app):
    settings = get_settings()
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║         TZMICHA AI OS v{settings.app_version}             ║
    ║      Enterprise AI Voice Platform            ║
    ╠══════════════════════════════════════════════╣
    ║  API:        http://localhost:{settings.port}          ║
    ║  Docs:       http://localhost:{settings.port}/docs      ║
    ║  LLM:        {settings.llm_provider:<15}           ║
    ║  STT:        {settings.stt_provider:<15}           ║
    ║  TTS:        {settings.tts_provider:<15}           ║
    ║  Env:        {settings.app_env:<15}           ║
    ╚══════════════════════════════════════════════╝
    """)

    # Init database
    try:
        from .database import init_db
        await init_db()
        print("  ✓ Database ready")
    except Exception as e:
        print(f"  ⚠ Database: {e}")

    yield
    print("  TZMICHA AI OS shutting down...")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="TZMICHA AI OS",
        version=settings.app_version,
        description="Enterprise AI Voice Platform - AI Employees that sound human",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # === Providers (config-driven) ===
    llm = ProviderFactory.create_llm()
    stt = ProviderFactory.create_stt()
    tts = ProviderFactory.create_tts()

    # === Services ===
    memory = MemoryService(window_size=settings.memory_window_size)
    language = LanguageService()
    knowledge = KnowledgeService()
    workflow = WorkflowService()
    enhancer = VoiceEnhancer()

    conversation = ConversationService(
        llm=llm, memory=memory, language=language,
        knowledge=knowledge, workflow=workflow, enhancer=enhancer,
    )

    voice = VoiceCallService(
        stt=stt, tts=tts, conversation=conversation, memory=memory,
    )

    # === Inject into routes ===
    inject_services(voice=voice, conversation=conversation, memory=memory)

    # === Routes ===
    app.include_router(router, prefix="/api/v1")

    @app.get("/")
    def root():
        return {
            "platform": "TZMICHA AI OS",
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
        }

    return app


app = create_app()
