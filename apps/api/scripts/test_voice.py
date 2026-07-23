"""
TZMICHA AI OS - Live Voice Test
Tests the full pipeline: You type → AI thinks → AI speaks (real voice)

Run: python test_voice.py
"""

import asyncio
import httpx
import os
import sys
import tempfile
import subprocess
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


async def test_elevenlabs_tts(text: str) -> bytes:
    """Test ElevenLabs TTS - convert text to speech"""
    print(f"  🔊 ElevenLabs: Converting to speech...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
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
            timeout=15.0,
        )
        
        if response.status_code == 200:
            print(f"  ✅ ElevenLabs: Audio generated ({len(response.content)} bytes)")
            return response.content
        else:
            print(f"  ❌ ElevenLabs Error: {response.status_code} - {response.text[:200]}")
            return b""


async def test_groq_llm(messages: list, product_info: str = "") -> str:
    """Test Groq LLM - generate AI response"""
    print(f"  🧠 Groq: Thinking...")
    
    system_prompt = f"""You are Alex, a friendly AI voice assistant.
    
RULES:
- Talk like a REAL human on a phone call
- Keep responses SHORT (1-2 sentences max)
- Be friendly, warm, professional
- Use natural language
- If someone speaks Hindi or Telugu, respond in that language
- Never sound robotic

{f"Business Info: {product_info}" if product_info else ""}"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system_prompt}] + messages,
                "temperature": 0.7,
                "max_tokens": 100,
            },
            timeout=15.0,
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            print(f"  ✅ Groq: Response generated")
            return reply
        else:
            print(f"  ❌ Groq Error: {response.status_code} - {response.text[:200]}")
            return "Sorry, I'm having trouble thinking right now."


async def test_deepgram_stt(audio_bytes: bytes) -> str:
    """Test Deepgram STT - convert speech to text"""
    print(f"  👂 Deepgram: Transcribing...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&detect_language=true",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav",
            },
            content=audio_bytes,
            timeout=15.0,
        )
        
        if response.status_code == 200:
            data = response.json()
            transcript = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
            language = data.get("results", {}).get("channels", [{}])[0].get("detected_language", "en")
            print(f"  ✅ Deepgram: Transcribed (language: {language})")
            return transcript
        else:
            print(f"  ❌ Deepgram Error: {response.status_code} - {response.text[:200]}")
            return ""


def play_audio(audio_bytes: bytes):
    """Play audio on Windows using MCI (supports MP3, waits for full playback)"""
    import ctypes
    
    temp_file = os.path.join(os.path.abspath("."), "_test_audio.mp3")
    with open(temp_file, "wb") as f:
        f.write(audio_bytes)
    
    # Windows MCI API - native MP3 support, waits for completion
    winmm = ctypes.windll.winmm
    buf = ctypes.create_unicode_buffer(256)
    
    def mci(cmd):
        winmm.mciSendStringW(cmd, buf, 255, 0)
        return buf.value
    
    try:
        mci("close test_audio")
        mci(f'open "{temp_file}" type mpegvideo alias test_audio')
        length = mci("status test_audio length")
        mci("play test_audio from 0")
        
        # Wait for full playback
        import time
        wait_seconds = (int(length) / 1000.0) + 1.0 if length.isdigit() else 8.0
        time.sleep(wait_seconds)
        
        mci("close test_audio")
    except Exception:
        # Fallback
        os.startfile(temp_file)
        import time
        time.sleep(5)
    
    try:
        os.unlink(temp_file)
    except Exception:
        pass


async def run_voice_test():
    """Full voice test - type text, hear AI respond"""
    
    print("""
    ╔══════════════════════════════════════════════════╗
    ║         TZMICHA AI OS - Voice Test              ║
    ║     Testing: Groq + ElevenLabs Pipeline         ║
    ╠══════════════════════════════════════════════════╣
    ║  Type a message → AI responds → You HEAR it    ║
    ║  Type 'quit' to exit                           ║
    ║  Type 'hindi' to test Hindi                    ║
    ║  Type 'telugu' to test Telugu                  ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    # Verify keys
    print("  Checking API keys...")
    if not GROQ_API_KEY:
        print("  ❌ GROQ_API_KEY missing!")
        return
    if not ELEVENLABS_API_KEY:
        print("  ❌ ELEVENLABS_API_KEY missing!")
        return
    if not DEEPGRAM_API_KEY:
        print("  ❌ DEEPGRAM_API_KEY missing!")
        return
    print("  ✅ All API keys found\n")
    
    conversation_history = []
    
    # Test with a greeting first
    print("=" * 50)
    print("  🎯 Quick API Test - AI will greet you:")
    print("=" * 50)
    
    # Generate greeting
    greeting = await test_groq_llm(
        [{"role": "user", "content": "Say a short friendly greeting. You just called someone."}]
    )
    print(f"\n  🤖 AI says: \"{greeting}\"\n")
    
    # Convert to speech
    audio = await test_elevenlabs_tts(greeting)
    if audio:
        print(f"  🔊 Playing audio... (listen!)\n")
        play_audio(audio)
    
    print("\n" + "=" * 50)
    print("  Now have a conversation! Type anything:")
    print("=" * 50 + "\n")
    
    conversation_history.append({"role": "assistant", "content": greeting})
    
    while True:
        # Get user input
        user_input = input("  👤 You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n  👋 Goodbye! Voice test complete.")
            break
        
        if user_input.lower() == "hindi":
            user_input = "Aap kaise hain? Mujhe fees ke baare mein batao"
            print(f"  👤 You (Hindi): {user_input}")
        
        if user_input.lower() == "telugu":
            user_input = "Namaskaram, fee entha? Telugu lo cheppandi"
            print(f"  👤 You (Telugu): {user_input}")
        
        print()
        
        # Add to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        ai_response = await test_groq_llm(conversation_history)
        print(f"  🤖 AI says: \"{ai_response}\"\n")
        
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Convert to speech
        audio = await test_elevenlabs_tts(ai_response)
        if audio:
            print(f"  🔊 Playing audio...\n")
            play_audio(audio)
        
        print()


async def run_api_verification():
    """Quick verification that all APIs work"""
    print("""
    ╔══════════════════════════════════════════════════╗
    ║      TZMICHA AI OS - API Verification           ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Test 1: Groq
    print("  [1/3] Testing Groq (LLM - Brain)...")
    try:
        response = await test_groq_llm([{"role": "user", "content": "Say hello in one word"}])
        results["Groq"] = "✅ Working" if response and not response.startswith("Sorry") else "❌ Failed"
        print(f"        Response: {response}")
    except Exception as e:
        results["Groq"] = f"❌ Error: {str(e)[:50]}"
    
    print()
    
    # Test 2: ElevenLabs
    print("  [2/3] Testing ElevenLabs (TTS - Voice)...")
    try:
        audio = await test_elevenlabs_tts("Hello, this is a test.")
        results["ElevenLabs"] = f"✅ Working ({len(audio)} bytes)" if audio else "❌ Failed"
    except Exception as e:
        results["ElevenLabs"] = f"❌ Error: {str(e)[:50]}"
    
    print()
    
    # Test 3: Deepgram
    print("  [3/3] Testing Deepgram (STT - Ears)...")
    try:
        # We'll just verify the API key works with a simple request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.deepgram.com/v1/projects",
                headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
                timeout=10.0,
            )
            results["Deepgram"] = "✅ Working" if response.status_code == 200 else f"❌ Status {response.status_code}"
    except Exception as e:
        results["Deepgram"] = f"❌ Error: {str(e)[:50]}"
    
    print()
    print("  " + "=" * 40)
    print("  RESULTS:")
    print("  " + "=" * 40)
    for service, status in results.items():
        print(f"    {service:15} → {status}")
    print("  " + "=" * 40)
    
    all_good = all("✅" in v for v in results.values())
    if all_good:
        print("\n  🎉 ALL APIS WORKING! Ready for voice test.\n")
    else:
        print("\n  ⚠️ Some APIs have issues. Check keys in .env\n")
    
    return all_good


if __name__ == "__main__":
    print("\n  Choose test mode:")
    print("  1. Verify APIs (quick check all keys work)")
    print("  2. Full Voice Test (conversation with AI voice)")
    print()
    
    choice = input("  Enter 1 or 2: ").strip()
    
    if choice == "1":
        asyncio.run(run_api_verification())
    elif choice == "2":
        asyncio.run(run_voice_test())
    else:
        # Default: verify first, then voice test
        print("\n  Running API verification first...\n")
        all_good = asyncio.run(run_api_verification())
        if all_good:
            print("  Starting voice test...\n")
            asyncio.run(run_voice_test())
