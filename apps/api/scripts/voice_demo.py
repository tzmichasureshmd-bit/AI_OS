"""
TZMICHA AI OS - Voice Calling Agent Demo
4 Languages: English, British English, Hindi, Telugu

Run: py voice_demo.py
"""

import asyncio
import httpx
import os
import sys
import time
import ctypes
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Voice mapping per language
VOICES = {
    "english": {
        "id": "cgSgspJ2msm6clMCkdW9",
        "name": "Jessica (Indian Girl Voice)",
    },
    "british": {
        "id": "pFZP5JQG7iQjIQuC4Bku",
        "name": "Lily (British Girl)",
    },
    "hindi": {
        "id": "cgSgspJ2msm6clMCkdW9",
        "name": "Jessica (Hindi Girl)",
    },
    "telugu": {
        "id": "cgSgspJ2msm6clMCkdW9",
        "name": "Jessica (Telugu Girl)",
    },
}

current_language = "english"
conversation_history = []
ai_name = "Priya"
company_name = "TZMICHA Technologies"


# ===== AUDIO PLAYER (Windows Native - NO external packages) =====

def play_audio_full(filepath: str):
    """
    Play MP3 file using Windows MCI (Media Control Interface).
    This is built into Windows - no pip install needed.
    WAITS for the FULL audio to finish before returning.
    """
    filepath = os.path.abspath(filepath)
    
    # Windows MCI API via ctypes
    winmm = ctypes.windll.winmm
    
    # Send MCI command
    def mci_send(command: str) -> str:
        buf = ctypes.create_unicode_buffer(256)
        err = winmm.mciSendStringW(command, buf, 255, 0)
        return buf.value
    
    try:
        # Close any previous instance
        mci_send("close tzmicha_audio")
        
        # Open the file
        mci_send(f'open "{filepath}" type mpegvideo alias tzmicha_audio')
        
        # Get the total length in milliseconds
        length_str = mci_send("status tzmicha_audio length")
        total_ms = int(length_str) if length_str.isdigit() else 10000
        
        # Play from start
        mci_send("play tzmicha_audio from 0")
        
        # Wait for playback to complete
        wait_time = (total_ms / 1000.0) + 0.5
        time.sleep(wait_time)
        
        # Close
        mci_send("close tzmicha_audio")
        
    except Exception as e:
        # Ultimate fallback
        print(f"    [Playing with default player...]")
        os.startfile(filepath)
        # Estimate: ~16KB per second of audio
        file_size = os.path.getsize(filepath)
        estimated = max(3, int(file_size / 14000) + 2)
        time.sleep(estimated)


# ===== TTS =====

async def speak(text: str, voice_id: str) -> None:
    """Convert text to speech using ElevenLabs and play FULL audio"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.3,
                    "use_speaker_boost": True,
                },
            },
            timeout=20.0,
        )

        if response.status_code == 200:
            # Save to file
            audio_path = os.path.abspath("_tzmicha_voice.mp3")
            with open(audio_path, "wb") as f:
                f.write(response.content)

            # Play FULL audio (waits until complete)
            play_audio_full(audio_path)

            # Cleanup
            try:
                os.unlink(audio_path)
            except Exception:
                pass
        else:
            print(f"    [Voice Error: {response.status_code} - {response.text[:100]}]")


# ===== LLM =====

SYSTEM_PROMPT = """You are {ai_name}, a professional AI voice assistant at {company}.

LANGUAGE RULES:
- Current language: {language}
- If customer uses Telugu words (entha, ela, cheppandi, undi) → respond in Telugu transliteration
- If customer uses Hindi words (batao, kaise, kitna, bhai) → respond in Hindi transliteration
- If customer says "speak british" → use British English style
- Support MIXED language naturally (Tenglish, Hinglish)
- For Telugu: Use transliteration like "Namaskaram sir, ela unnaru?"
- For Hindi: Use transliteration like "Namaste sir, kaise hain aap?"
- For British: Use "Brilliant", "Lovely", "Quite right", "Indeed"

PERSONALITY:
- Talk like a REAL human employee on a phone call
- Friendly, warm, professional
- Keep responses SHORT (1-3 sentences MAX)
- Use natural fillers: "Hmm...", "Sure...", "Right..."
- Show emotion - excitement, empathy
- Never sound robotic

RULES:
- MAX 2-3 sentences per response (this is a phone call, not email)
- Ask ONE question at a time
- Remember everything discussed
- Never repeat yourself
- Vary your language (don't always say the same phrases)

COMPANY INFO:
{company} - AI-powered solutions for businesses
Services: AI Voice Agents, AI Automation, Custom AI Development
Pricing: Plans from Rs. 5,000/month
Location: Hyderabad, Telangana
Working Hours: 9 AM to 6 PM IST"""


async def think(user_message: str) -> str:
    """Get AI response"""
    global current_language, conversation_history

    msg_lower = user_message.lower()
    if any(w in msg_lower for w in ["telugu", "cheppandi", "entha", "ela", "undi", "meeru", "bagundi"]):
        current_language = "telugu"
    elif any(w in msg_lower for w in ["hindi", "batao", "bhai", "kaise", "kitna", "haan", "mein"]):
        current_language = "hindi"
    elif any(w in msg_lower for w in ["british", "brilliant", "lovely", "quite"]):
        current_language = "british"
    elif any(w in msg_lower for w in ["english", "speak english"]):
        current_language = "english"

    conversation_history.append({"role": "user", "content": user_message})

    lang_names = {
        "english": "American English",
        "british": "British English",
        "hindi": "Hindi (Hinglish - use Latin script transliteration)",
        "telugu": "Telugu (Tenglish - use Latin script transliteration)",
    }

    system = SYSTEM_PROMPT.format(
        ai_name=ai_name,
        company=company_name,
        language=lang_names[current_language],
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system}] + conversation_history[-20:],
                "temperature": 0.7,
                "max_tokens": 120,
            },
            timeout=15.0,
        )

        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            conversation_history.append({"role": "assistant", "content": reply})
            return reply
        else:
            return "Sorry, one moment please..."


# ===== MAIN DEMO =====

async def run_demo():
    global current_language, conversation_history

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          TZMICHA AI OS - Voice Calling Agent              ║
    ║                                                           ║
    ║   AI Employee: Priya                                      ║
    ║   Company: TZMICHA Technologies                           ║
    ║   Languages: English | British | Hindi | Telugu           ║
    ║                                                           ║
    ║   • Type message → AI responds with REAL VOICE           ║
    ║   • Say "Telugu lo cheppandi" → Telugu                    ║
    ║   • Say "Hindi mein baat karo" → Hindi                   ║
    ║   • Say "speak british" → British English                 ║
    ║   • Type "quit" to end                                    ║
    ║                                                           ║
    ║   🔊 TURN SPEAKER ON - FULL AUDIO WILL PLAY              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    print("    📞 Calling...")
    time.sleep(1)
    print("    📞 Ringing...")
    time.sleep(1)
    print("    ✅ Connected!\n")

    # AI greeting
    greeting = f"Hello! This is {ai_name} from {company_name}. How are you doing today?"
    conversation_history.append({"role": "assistant", "content": greeting})

    print(f"    🤖 {ai_name}: {greeting}")
    voice = VOICES[current_language]
    print(f"    🔊 [{voice['name']}] Speaking...", flush=True)
    await speak(greeting, voice["id"])
    print()

    # Conversation loop
    while True:
        print("    " + "─" * 50)
        user_input = input(f"    👤 Customer: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["quit", "exit", "bye", "end", "q"]:
            print(f"\n    🤖 {ai_name}: ", end="", flush=True)
            goodbye = await think("Customer is ending the call. Say a warm natural goodbye in 1 sentence.")
            print(goodbye)
            voice = VOICES[current_language]
            print(f"    🔊 [{voice['name']}] Speaking...", flush=True)
            await speak(goodbye, voice["id"])
            print(f"\n    📴 Call Ended")
            print(f"    ⏱️  Total turns: {len(conversation_history) // 2}")
            break

        # Think
        print(f"\n    🤖 {ai_name}: ", end="", flush=True)
        start = time.time()
        response = await think(user_input)
        think_time = time.time() - start
        print(response)
        print(f"    ⚡ Think time: {think_time:.1f}s")

        # Speak FULL response
        voice = VOICES[current_language]
        print(f"    🔊 [{voice['name']}] Speaking full response...", flush=True)
        await speak(response, voice["id"])
        print()


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\n    📴 Call ended.")
    finally:
        # Cleanup any leftover audio file
        try:
            os.unlink("_tzmicha_voice.mp3")
        except Exception:
            pass
