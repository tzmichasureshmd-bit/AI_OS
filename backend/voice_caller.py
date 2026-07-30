"""
Voice Caller - Real AI Phone Calls
Twilio (telephony) + Deepgram (STT) + ElevenLabs (TTS) + Groq (AI brain)
"""

import asyncio
import json
import base64
import httpx
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Connect
from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER,
    DEEPGRAM_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID,
    SERVER_PUBLIC_URL
)

# Twilio client
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None

# Active voice calls tracking
active_voice_calls = {}


def make_call(phone_number: str, lead_id: int, client_id: int, opening_message: str) -> dict:
    """Initiate a real phone call via Twilio"""
    if not twilio_client:
        return {"error": "Twilio not configured. Add credentials to .env"}

    call_id = f"voice_{client_id}_{lead_id}"
    active_voice_calls[call_id] = {
        "lead_id": lead_id,
        "client_id": client_id,
        "opening_message": opening_message,
        "transcript": [],
        "status": "initiating"
    }

    # Twilio calls your webhook URL when person picks up
    call = twilio_client.calls.create(
        to=phone_number,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{SERVER_PUBLIC_URL}/voice/webhook/answer?call_id={call_id}",
        status_callback=f"{SERVER_PUBLIC_URL}/voice/webhook/status?call_id={call_id}",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
    )

    active_voice_calls[call_id]["twilio_sid"] = call.sid
    active_voice_calls[call_id]["status"] = "ringing"

    return {"call_id": call_id, "twilio_sid": call.sid, "status": "ringing"}


def generate_answer_twiml(call_id: str) -> str:
    """Generate TwiML when person answers - connects to WebSocket for streaming"""
    response = VoiceResponse()

    # Connect to our WebSocket for real-time audio streaming
    connect = Connect()
    connect.stream(url=f"wss://{SERVER_PUBLIC_URL.replace('https://', '').replace('http://', '')}/voice/ws/{call_id}")
    response.append(connect)

    return str(response)


async def text_to_speech_elevenlabs(text: str) -> bytes:
    """Convert text to speech using ElevenLabs (human-like voice)"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_turbo_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            },
            timeout=10.0
        )
        if response.status_code == 200:
            return response.content
        return b""


async def speech_to_text_deepgram(audio_bytes: bytes) -> str:
    """Convert speech to text using Deepgram (fast ~300ms)"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/mulaw"
            },
            content=audio_bytes,
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            transcript = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
            return transcript
        return ""


def end_voice_call(call_id: str) -> dict:
    """Hang up a call"""
    if call_id not in active_voice_calls:
        return {"error": "Call not found"}

    call_data = active_voice_calls[call_id]
    if twilio_client and call_data.get("twilio_sid"):
        twilio_client.calls(call_data["twilio_sid"]).update(status="completed")

    call_data["status"] = "completed"
    return {"status": "completed", "transcript": call_data["transcript"]}


def get_call_status(call_id: str) -> dict:
    """Get current call status"""
    if call_id not in active_voice_calls:
        return {"error": "Call not found"}
    data = active_voice_calls[call_id]
    return {"call_id": call_id, "status": data["status"], "transcript_length": len(data["transcript"])}
