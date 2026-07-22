"""
TZMICHA AI OS - Configuration
All settings loaded from environment. Switch providers by changing .env only.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Platform
    app_name: str = "TZMICHA AI OS"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "change-this-in-production"

    # Provider Selection
    stt_provider: str = Field(default="deepgram")
    tts_provider: str = Field(default="elevenlabs")
    llm_provider: str = Field(default="groq")

    # Database
    database_url: str = "postgresql+asyncpg://tzmicha:tzmicha_dev_2024@localhost:5432/tzmicha"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Deepgram
    deepgram_api_key: str = ""
    deepgram_stt_model: str = "nova-2"
    deepgram_tts_model: str = "aura-asteria-en"

    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "EXAVITQu4vr4xnSDxMaL"
    elevenlabs_model: str = "eleven_turbo_v2"

    # Piper
    piper_model_path: str = "./models/piper/en_US-lessac-medium.onnx"

    # Whisper
    whisper_model_size: str = "base"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    server_public_url: str = "http://localhost:8000"

    # Conversation
    max_conversation_turns: int = 50
    memory_window_size: int = 20
    default_language: str = "en"
    supported_languages: str = "en,hi,te"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
