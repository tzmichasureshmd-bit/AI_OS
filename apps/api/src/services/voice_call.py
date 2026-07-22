"""Voice Call Service - Real-time audio pipeline with barge-in."""

import asyncio
from typing import Optional, Callable
from datetime import datetime
from ..core.interfaces import STTProvider, TTSProvider
from ..core.models import VoiceCallState, CallStatus
from .conversation import ConversationService
from .memory import MemoryService


class VoiceCallService:
    def __init__(self, stt: STTProvider, tts: TTSProvider, conversation: ConversationService, memory: MemoryService):
        self.stt = stt
        self.tts = tts
        self.conversation = conversation
        self.memory = memory
        self._calls: dict[str, VoiceCallState] = {}

    async def start_call(self, call_id: str, **kwargs) -> tuple[str, str]:
        cid, opening = await self.conversation.start_conversation(**kwargs)
        ctx = self.memory.get_conversation(cid)
        self._calls[call_id] = VoiceCallState(call_id=call_id, conversation=ctx, status=CallStatus.CONNECTED)
        return cid, opening

    async def generate_audio(self, text: str, language: str = "en") -> bytes:
        return await self.tts.synthesize(text, language)

    async def process_audio_chunk(self, call_id: str, audio: bytes, on_response: Callable = None) -> Optional[str]:
        state = self._calls.get(call_id)
        if not state:
            return None
        state.audio_buffer += audio
        if len(state.audio_buffer) >= 16000:
            buf = state.audio_buffer
            state.audio_buffer = b""
            transcript = await self.stt.transcribe_buffer(buf)
            if transcript and transcript.strip():
                if state.status == CallStatus.SPEAKING:
                    state.is_interrupted = True
                    self.conversation.interrupt(state.conversation.conversation_id)
                state.status = CallStatus.PROCESSING
                response = await self.conversation.process_message(state.conversation.conversation_id, transcript)
                if response and on_response:
                    state.status = CallStatus.SPEAKING
                    audio_out = await self.tts.synthesize(response, state.conversation.current_language)
                    on_response(audio_out)
                state.status = CallStatus.LISTENING
                return transcript
        return None

    async def end_call(self, call_id: str) -> dict:
        state = self._calls.pop(call_id, None)
        if not state:
            return {"error": "Not found"}
        summary = await self.conversation.end_conversation(state.conversation.conversation_id)
        summary["duration"] = int((datetime.utcnow() - state.started_at).total_seconds())
        return summary

    def get_status(self, call_id: str) -> dict:
        state = self._calls.get(call_id)
        if not state:
            return {"error": "Not found"}
        return {"call_id": call_id, "status": state.status.value, "duration": int((datetime.utcnow() - state.started_at).total_seconds())}

    def get_active_calls(self) -> list[dict]:
        return [self.get_status(cid) for cid in self._calls]
