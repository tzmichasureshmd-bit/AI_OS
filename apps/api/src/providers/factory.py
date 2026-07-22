"""Provider Factory - creates providers based on config."""

from ..core.interfaces import STTProvider, TTSProvider, LLMProvider
from ..config import get_settings


class ProviderFactory:
    @staticmethod
    def create_stt() -> STTProvider:
        provider = get_settings().stt_provider.lower()
        if provider == "deepgram":
            from .stt.deepgram import DeepgramSTT
            return DeepgramSTT()
        elif provider == "whisper":
            from .stt.whisper import WhisperSTT
            return WhisperSTT()
        elif provider == "openai":
            from .stt.openai_stt import OpenAISTT
            return OpenAISTT()
        raise ValueError(f"Unknown STT: {provider}")

    @staticmethod
    def create_tts() -> TTSProvider:
        provider = get_settings().tts_provider.lower()
        if provider == "elevenlabs":
            from .tts.elevenlabs import ElevenLabsTTS
            return ElevenLabsTTS()
        elif provider == "deepgram":
            from .tts.deepgram import DeepgramTTS
            return DeepgramTTS()
        elif provider == "piper":
            from .tts.piper import PiperTTS
            return PiperTTS()
        raise ValueError(f"Unknown TTS: {provider}")

    @staticmethod
    def create_llm() -> LLMProvider:
        provider = get_settings().llm_provider.lower()
        if provider == "groq":
            from .llm.groq import GroqLLM
            return GroqLLM()
        elif provider == "ollama":
            from .llm.ollama import OllamaLLM
            return OllamaLLM()
        elif provider == "openai":
            from .llm.openai_llm import OpenAILLM
            return OpenAILLM()
        elif provider == "anthropic":
            from .llm.anthropic import AnthropicLLM
            return AnthropicLLM()
        raise ValueError(f"Unknown LLM: {provider}")
