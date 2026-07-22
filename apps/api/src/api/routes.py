"""API Routes - REST + WebSocket endpoints."""

import uuid
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

_voice = None
_conversation = None
_memory = None


def inject_services(voice, conversation, memory):
    global _voice, _conversation, _memory
    _voice = voice
    _conversation = conversation
    _memory = memory


class StartRequest(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    business_context: str = ""
    goal: str = ""
    language: str = "en"

class MessageRequest(BaseModel):
    message: str


@router.get("/")
def health():
    return {"platform": "TZMICHA AI OS", "engine": "Voice AI", "status": "running"}


@router.get("/status")
def status():
    return {"active_calls": _voice.get_active_calls() if _voice else [], "conversations": _memory.get_active_conversations() if _memory else []}


@router.post("/conversation/start")
async def start_conv(req: StartRequest):
    cid, opening = await _conversation.start_conversation(
        customer_name=req.customer_name, customer_phone=req.customer_phone,
        business_context=req.business_context, goal=req.goal, language=req.language,
    )
    return {"conversation_id": cid, "ai_message": opening}


@router.post("/conversation/{cid}/message")
async def send_msg(cid: str, req: MessageRequest):
    response = await _conversation.process_message(cid, req.message)
    ctx = _memory.get_conversation(cid)
    return {
        "ai_message": response,
        "language": ctx.current_language if ctx else "en",
        "active_topic": ctx.active_topic.topic_name if ctx and ctx.active_topic else None,
    }


@router.post("/conversation/{cid}/end")
async def end_conv(cid: str):
    return await _conversation.end_conversation(cid)


@router.post("/voice/call/start")
async def start_call(req: StartRequest):
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    cid, opening = await _voice.start_call(
        call_id=call_id, customer_name=req.customer_name,
        customer_phone=req.customer_phone, business_context=req.business_context,
        goal=req.goal, language=req.language,
    )
    audio = await _voice.generate_audio(opening, req.language)
    return {
        "call_id": call_id, "conversation_id": cid,
        "opening_message": opening,
        "audio_base64": base64.b64encode(audio).decode() if audio else "",
    }


@router.post("/voice/call/{call_id}/end")
async def end_call(call_id: str):
    return await _voice.end_call(call_id)


@router.get("/voice/call/{call_id}/status")
def call_status(call_id: str):
    return _voice.get_status(call_id)
