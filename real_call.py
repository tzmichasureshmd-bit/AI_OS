"""
TZMICHA AI OS - Real Phone Calling
AI calls a real phone number. Person picks up. AI talks naturally.

SETUP NEEDED:
1. Twilio account (free $15 credit)
2. ngrok running: ngrok http 8000
3. Fill in credentials below or in .env

RUN:
  py real_call.py
"""

import asyncio
import os
import json
import time
import base64
import ctypes
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import Response
import uvicorn
import httpx
from sarvamai import SarvamAI
from sarvamai.play import save as sarvam_save

load_dotenv()

# ===== CONFIGURATION =====
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
SERVER_PUBLIC_URL = os.getenv("SERVER_PUBLIC_URL", "")  # ngrok URL

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "sk_qhw027f8_mihfH0NToycAnbxI4sASGHMi")

# AI Employee config
AI_NAME = "Priya"
COMPANY = "misha Technologies"
VOICE = "suhani"
LANGUAGE = "te-IN"

# ===== APP =====
app = FastAPI(title="TZMICHA AI OS - Real Calling")

# Conversation state
conversations = {}

SYSTEM_PROMPT = """You are {name}, a real Indian girl working at {company}. You're ON A PHONE CALL right now.

RULES:
- Talk like a REAL person on phone. Short, natural, casual.
- MAX 2 sentences per response. ALWAYS complete the sentence.
- WRITE TELUGU WORDS IN TELUGU SCRIPT (తెలుగు). English words in English.
- Example: "హాయ్! fee అంటే 5000 per month ఉంటుంది."
- Use fillers: "hmm...", "so...", "actually..."
- Never sound like AI. Never say "How can I assist you?"
- If they say bye, say a quick natural goodbye.

COMPANY INFO:
{company} - AI voice solutions
Price: 5000/month
Location: Hyderabad

You are {name}. Be real. Be human."""


async def get_ai_response(conversation_history: list) -> str:
    """Get response from Groq LLM"""
    system = SYSTEM_PROMPT.format(name=AI_NAME, company=COMPANY)

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system}] + conversation_history[-16:],
                "temperature": 0.9,
                "max_tokens": 150,
            },
            timeout=15.0,
        )

        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            reply = reply.replace("*", "").replace("😊", "").replace("😄", "")
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]
            # Trim incomplete sentences
            if reply and reply[-1] not in '.!?।"':
                for i in range(len(reply) - 1, -1, -1):
                    if reply[i] in '.!?।':
                        reply = reply[:i+1]
                        break
            return reply
        return "హాయ్! ఒక్క moment ..."


async def text_to_speech(text: str) -> bytes:
    """Convert text to speech using Sarvam AI"""
    sarvam = SarvamAI(api_subscription_key=SARVAM_API_KEY)

    try:
        response = sarvam.text_to_speech.convert(
            text=text,
            target_language_code=LANGUAGE,
            model="bulbul:v3",
            speaker=VOICE,
            pace=1.3,
            speech_sample_rate=8000,  # Telephony quality (8kHz for phone calls)
        )
        # Save to get bytes
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sarvam_save(response, tmp.name)
        with open(tmp.name, "rb") as f:
            audio_bytes = f.read()
        os.unlink(tmp.name)
        return audio_bytes
    except Exception as e:
        print(f"TTS Error: {e}")
        return b""


async def speech_to_text(audio_bytes: bytes) -> str:
    """Convert speech to text using Sarvam AI"""
    sarvam = SarvamAI(api_subscription_key=SARVAM_API_KEY)

    try:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.write(audio_bytes)
        tmp.close()

        response = sarvam.speech_to_text.convert(
            file=tmp.name,
            language_code=LANGUAGE,
            model="saaras:v2",
        )
        os.unlink(tmp.name)
        return response.transcript if hasattr(response, 'transcript') else str(response)
    except Exception as e:
        print(f"STT Error: {e}")
        return ""


# ===== TWILIO ENDPOINTS =====

@app.get("/")
def home():
    return {"status": "TZMICHA AI OS - Real Calling Server Running", "ai": AI_NAME, "company": COMPANY}


@app.post("/voice/inbound")
async def handle_inbound(request: Request):
    """When someone calls YOUR Twilio number, this handles it"""
    form = await request.form()
    caller = form.get("From", "unknown")
    call_sid = form.get("CallSid", "")

    print(f"\n📞 INBOUND CALL from {caller}")

    # Initialize conversation
    conversations[call_sid] = {
        "history": [],
        "caller": caller,
    }

    # Generate greeting
    greeting = f"హాయ్! నేను {AI_NAME} ని, {COMPANY} నుంచి. మీరు ఎలా ఉన్నారు?"
    conversations[call_sid]["history"].append({"role": "assistant", "content": greeting})

    # Generate TTS for greeting
    audio = await text_to_speech(greeting)

    # TwiML - play greeting then gather speech
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{greeting}</Say>
    <Gather input="speech" action="{SERVER_PUBLIC_URL}/voice/respond?call_sid={call_sid}" method="POST" speechTimeout="3" language="te-IN">
    </Gather>
    <Say>Call ended. Goodbye.</Say>
</Response>"""

    return Response(content=twiml, media_type="application/xml")


@app.post("/voice/respond")
async def handle_response(request: Request, call_sid: str = ""):
    """Handle customer's speech response"""
    form = await request.form()
    speech_result = form.get("SpeechResult", "")

    print(f"    👤 Customer: {speech_result}")

    if not speech_result or call_sid not in conversations:
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response><Say>Sorry, I didn't catch that. Goodbye.</Say><Hangup/></Response>"""
        return Response(content=twiml, media_type="application/xml")

    # Add to history
    conversations[call_sid]["history"].append({"role": "user", "content": speech_result})

    # Check if customer wants to end
    end_words = ["bye", "goodbye", "end", "thanks bye", "okay bye", "cut"]
    if any(w in speech_result.lower() for w in end_words):
        goodbye = "సరే, thanks for calling! మళ్ళీ మాట్లాడుకుందాం. Bye!"
        print(f"    🤖 {AI_NAME}: {goodbye}")
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Say voice="alice">{goodbye}</Say><Hangup/></Response>"""
        return Response(content=twiml, media_type="application/xml")

    # Get AI response
    ai_response = await get_ai_response(conversations[call_sid]["history"])
    conversations[call_sid]["history"].append({"role": "assistant", "content": ai_response})

    print(f"    🤖 {AI_NAME}: {ai_response}")

    # Continue conversation
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{ai_response}</Say>
    <Gather input="speech" action="{SERVER_PUBLIC_URL}/voice/respond?call_sid={call_sid}" method="POST" speechTimeout="3" language="te-IN">
    </Gather>
    <Say>నేను మీ response కోసం wait చేస్తున్నాను.</Say>
    <Gather input="speech" action="{SERVER_PUBLIC_URL}/voice/respond?call_sid={call_sid}" method="POST" speechTimeout="5" language="te-IN">
    </Gather>
</Response>"""

    return Response(content=twiml, media_type="application/xml")


@app.post("/voice/outbound")
async def make_outbound_call(phone_number: str = ""):
    """AI calls someone (outbound)"""
    if not phone_number:
        return {"error": "Provide phone_number parameter"}

    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return {"error": "Twilio credentials not set. Add to .env file."}

    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        call = client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{SERVER_PUBLIC_URL}/voice/inbound",
            status_callback=f"{SERVER_PUBLIC_URL}/voice/status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
        )
        print(f"\n📞 OUTBOUND CALL to {phone_number} - SID: {call.sid}")
        return {"status": "calling", "call_sid": call.sid, "to": phone_number}
    except Exception as e:
        return {"error": str(e)}


@app.post("/voice/status")
async def call_status(request: Request):
    """Twilio sends status updates here"""
    form = await request.form()
    status = form.get("CallStatus", "")
    print(f"    📊 Call Status: {status}")
    return {"ok": True}


# ===== MAIN =====

def main():
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║   TZMICHA AI OS - Real Phone Calling Server      ║
    ╠══════════════════════════════════════════════════╣
    ║  AI: {AI_NAME}                                          ║
    ║  Company: {COMPANY}                          ║
    ║  Voice: {VOICE} (Telugu)                           ║
    ╠══════════════════════════════════════════════════╣
    ║  Server: http://localhost:8000                    ║
    ║  Docs: http://localhost:8000/docs                 ║
    ╠══════════════════════════════════════════════════╣
    ║  TO MAKE A CALL:                                 ║
    ║  POST http://localhost:8000/voice/outbound        ║
    ║  ?phone_number=+91XXXXXXXXXX                     ║
    ╠══════════════════════════════════════════════════╣
    ║  SETUP NEEDED:                                   ║
    ║  1. Twilio credentials in .env                   ║
    ║  2. ngrok running: ngrok http 8000               ║
    ║  3. Set SERVER_PUBLIC_URL in .env                 ║
    ╚══════════════════════════════════════════════════╝
    """)

    if not TWILIO_ACCOUNT_SID:
        print("  ⚠️  TWILIO_ACCOUNT_SID not set in .env")
    if not TWILIO_AUTH_TOKEN:
        print("  ⚠️  TWILIO_AUTH_TOKEN not set in .env")
    if not SERVER_PUBLIC_URL:
        print("  ⚠️  SERVER_PUBLIC_URL not set (run ngrok http 8000 first)")
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and SERVER_PUBLIC_URL:
        print("  ✅ All credentials set. Ready to make calls!")

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
