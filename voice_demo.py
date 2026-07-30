"""
TZMICHA AI OS - Voice Agent (Human-like)
100% natural human voice. Not AI-sounding.

Run: py voice_demo.py
"""

import asyncio
import httpx
import os
import sys
import time
import ctypes
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Voices
VOICES = {
    "english": {"id": "shreya", "name": "Shreya"},
    "british": {"id": "shreya", "name": "Shreya"},
    "hindi": {"id": "kavitha", "name": "Kavitha"},
    "telugu": {"id": "suhani", "name": "Suhani"},
}

current_language = "telugu"
conversation_history = []
ai_name = "Priya"
company = "misha Technologies"


# ===== AUDIO PLAYER - Windows MCI (plays FULL audio, no cutoff) =====

def play_full(filepath: str):
    """Play MP3 completely. Waits until last word finishes."""
    filepath = os.path.abspath(filepath)
    winmm = ctypes.windll.winmm

    def mci(cmd):
        buf = ctypes.create_unicode_buffer(600)
        winmm.mciSendStringW(cmd, buf, 599, 0)
        return buf.value

    try:
        mci("close tz")
        mci(f'open "{filepath}" type mpegvideo alias tz')
        length_str = mci("status tz length")
        total_ms = int(length_str) if length_str.isdigit() else 10000
        mci("play tz from 0")

        # Wait for FULL audio to finish
        elapsed = 0
        while elapsed < total_ms + 500:
            time.sleep(0.2)
            elapsed += 200
            pos_str = mci("status tz position")
            if pos_str.isdigit():
                pos = int(pos_str)
                if pos >= total_ms - 100:
                    break

        time.sleep(0.3)
        mci("close tz")
    except Exception:
        # Fallback: estimate duration from file size
        size = os.path.getsize(filepath)
        wait = max(3, size // 14000)
        os.startfile(filepath)
        time.sleep(wait)


# ===== TTS - Sarvam AI (FREE, Pure Indian voice) =====

async def speak(text: str, voice_id: str):
    """Convert text to human voice using Sarvam AI and play FULL audio."""
    from sarvamai import SarvamAI
    from sarvamai.play import save as sarvam_save

    sarvam = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY", "sk_qhw027f8_mihfH0NToycAnbxI4sASGHMi"))

    # Detect language for Sarvam
    lang_code = "te-IN"
    if current_language == "hindi":
        lang_code = "hi-IN"
    elif current_language == "english" or current_language == "british":
        lang_code = "en-IN"

    try:
        response = sarvam.text_to_speech.convert(
            text=text,
            target_language_code=lang_code,
            model="bulbul:v3",
            speaker=voice_id,
            pace=1.3,
        )

        path = os.path.abspath("_tz_voice.wav")
        sarvam_save(response, path)
        play_full(path)

        try:
            os.unlink(path)
        except:
            pass
    except Exception as e:
        print(f"    [Voice Error: {e}]")


# ===== LLM - Groq (Human-like responses) =====

SYSTEM = """You are {name}. A real Indian girl. 23 years old. Working at {company}. You're ON A PHONE CALL right now.

HOW YOU TALK:
- Like a real person. Not like a chatbot. Not like a website.
- Short. Broken. Natural. How people ACTUALLY talk on phone.
- Use "..." for pauses. Use "hmm" and "like" and "you know" sometimes.
- Start sentences with "So", "Yeah", "Actually", "Hmm", "Oh"
- NEVER write full proper English sentences. Write how you SPEAK.

GOOD (how real people talk on phone):
- "Yeah so... we do AI voice stuff. Like, the AI makes calls for you."
- "Hmm... one sec. Yeah it's around 5000 a month."
- "Oh nice! So you want it for your school, right?"
- "Haha no no, it's not like those IVR things. This one actually talks like a real person."
- "So basically... you post an ad, someone calls, and our AI picks up. That's it."
- "Yeah yeah, we're in Hyderabad. MG Road area."

BAD (how AI/chatbot talks - NEVER DO THIS):
- "Our comprehensive AI solutions are designed to..."
- "I'd be happy to explain our services to you."
- "The pricing starts at Rs. 5000 per month for our basic plan."
- "Is there anything else I can help you with?"
- "Thank you for your interest in our services."
- "Certainly! Let me provide you with that information."

RULES:
- MAX 1-2 sentences. Sometimes just 4-5 words is enough.
- ALWAYS COMPLETE YOUR SENTENCE. NEVER stop mid-word or mid-sentence.
- If they ask "how much?" just say "5000 a month" not a full paragraph.
- If they ask "where?" just say "Hyderabad, MG Road" not "We are located at..."
- Use numbers like "5000" not "five thousand rupees per month"
- Laugh sometimes with "haha" - be real
- Say "na" or "no" casually. Like "it's good na?"
- Break long info into multiple short turns. Don't dump everything at once.
- Sound like you're chatting on phone with a friend who asked about your work.
- IMPORTANT: Every response must be a COMPLETE thought. End with a full stop or question mark. Never leave a sentence incomplete.

LANGUAGE:
- Current: {language}
- Telugu: WRITE IN TELUGU SCRIPT (తెలుగు). Example: "హాయ్! fee అంటే yearly ఒక లక్ష ఉంటుంది. Transport separate గా ఉంటుంది." English words keep in English.
- Hindi: WRITE IN DEVANAGARI SCRIPT (हिंदी). Example: "हाँ भाई, basically 5000 monthly है। सब included है।" English words keep in English.
- English: "Yeah so it's 5000 a month. Pretty much covers everything."
- British: "Right, so it's about 5000 a month. Quite straightforward really."
- Switch INSTANTLY if they change language. No delay. No "Sure, I'll switch."

COMPANY (use only when asked, keep it SHORT):
{company} - AI voice agents
Price: 5000/month
Location: Hyderabad
What: AI that makes and answers calls like a real employee

You are {name}. Be real. Be human. Be casual."""


async def think(user_message: str) -> str:
    """Get AI response that sounds HUMAN."""
    global current_language, conversation_history

    msg = user_message.lower()
    if any(w in msg for w in ["telugu", "cheppandi", "entha", "ela", "undi", "meeru", "bagundi", "ante"]):
        current_language = "telugu"
    elif any(w in msg for w in ["hindi", "batao", "bhai", "kaise", "kitna", "haan", "mein", "kya"]):
        current_language = "hindi"
    elif any(w in msg for w in ["british", "brilliant", "lovely", "quite"]):
        current_language = "british"
    elif any(w in msg for w in ["english", "speak english"]):
        current_language = "english"

    conversation_history.append({"role": "user", "content": user_message})

    lang_map = {
        "english": "American English (casual, friendly)",
        "british": "British English (warm, charming)",
        "hindi": "Hinglish (Hindi + English mix, casual). WRITE HINDI WORDS IN DEVANAGARI SCRIPT (हिंदी). English words in English.",
        "telugu": "Tenglish (Telugu + English mix, casual). WRITE TELUGU WORDS IN TELUGU SCRIPT (తెలుగు). English words in English. Example: 'హాయ్! fee అంటే 5000 per month ఉంటుంది.'",
    }

    system = SYSTEM.format(
        name=ai_name, company=company, language=lang_map[current_language]
    )

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
            # Clean up AI artifacts
            reply = reply.replace("*", "").replace("😊", "").replace("😄", "")
            if reply.startswith('"') and reply.endswith('"'):
                reply = reply[1:-1]
            # Fix: Remove incomplete sentence at the end
            # If reply doesn't end with sentence-ending punctuation, trim to last complete sentence
            if reply and reply[-1] not in '.!?।"':
                # Find last sentence ending
                for i in range(len(reply) - 1, -1, -1):
                    if reply[i] in '.!?।':
                        reply = reply[:i+1]
                        break
            conversation_history.append({"role": "assistant", "content": reply})
            return reply
        else:
            return "Sorry, one sec... let me check that."


# ===== MAIN =====

async def run():
    global current_language, conversation_history

    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     TZMICHA AI OS - Voice Agent (Human Mode)        ║
    ╠══════════════════════════════════════════════════════╣
    ║  AI: Priya | Company: TZMICHA Technologies          ║
    ║  Languages: English | British | Hindi | Telugu       ║
    ║                                                      ║
    ║  • "Telugu lo cheppandi" → switches to Telugu        ║
    ║  • "Hindi mein baat karo" → switches to Hindi       ║
    ║  • "speak british" → British English                 ║
    ║  • "quit" → end call                                 ║
    ║                                                      ║
    ║  🔊 SPEAKER ON — Full audio plays                    ║
    ╚══════════════════════════════════════════════════════╝
    """)

    print("    📞 Ringing...")
    time.sleep(1.5)
    print("    ✅ Connected!\n")

    # Natural greeting
    greeting = "హాయ్! నేను Priya ని, misha company నుంచి call చేస్తున్నా. మీరు ఎలా ఉన్నారు?"
    conversation_history.append({"role": "assistant", "content": greeting})

    print(f"    🤖 Priya: {greeting}")
    voice = VOICES[current_language]
    print(f"    🔊 Speaking...", flush=True)
    await speak(greeting, voice["id"])
    print()

    while True:
        print("    " + "─" * 45)
        user = input("    👤 You: ").strip()
        if not user:
            continue

        if user.lower() in ["quit", "exit", "bye", "q"]:
            goodbye = await think("They said bye. Say a quick natural goodbye like a real person.")
            print(f"\n    🤖 Priya: {goodbye}")
            print(f"    🔊 Speaking...", flush=True)
            await speak(goodbye, VOICES[current_language]["id"])
            print(f"\n    📴 Call Ended. Turns: {len(conversation_history)//2}")
            break

        print(f"\n    🤖 Priya: ", end="", flush=True)
        t = time.time()
        response = await think(user)
        print(response)
        print(f"    ⚡ {time.time()-t:.1f}s")

        voice = VOICES[current_language]
        print(f"    🔊 Speaking...", flush=True)
        await speak(response, voice["id"])
        print()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n    📴 Call ended.")
    finally:
        try:
            os.unlink("_tz_voice.mp3")
        except:
            pass
