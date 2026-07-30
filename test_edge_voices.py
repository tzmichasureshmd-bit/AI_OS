"""
Test Edge TTS - Hear all 4 language voices
FREE. No API key. Pure native pronunciation.
"""
import asyncio
import edge_tts
import os
import time
import ctypes


def play_full(filepath: str):
    """Play MP3 completely using Windows MCI."""
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
        elapsed = 0
        while elapsed < total_ms + 500:
            time.sleep(0.2)
            elapsed += 200
            pos = mci("status tz position")
            if pos.isdigit() and int(pos) >= total_ms - 100:
                break
        time.sleep(0.3)
        mci("close tz")
    except Exception:
        os.startfile(filepath)
        time.sleep(5)


async def test_voice(voice: str, text: str, label: str):
    """Generate and play one voice."""
    print(f"\n    🔊 {label}")
    print(f"    📝 \"{text}\"")
    print(f"    🎤 Voice: {voice}")
    
    output = "_test_edge.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)
    
    print(f"    ▶️  Playing...", flush=True)
    play_full(output)
    
    try:
        os.unlink(output)
    except:
        pass


async def main():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║   EDGE TTS - Free Voice Test (All 4 Languages)  ║
    ║   100% FREE | Native Pronunciation | No API Key ║
    ╚══════════════════════════════════════════════════╝
    """)

    # 1. Telugu Female - Shruti
    await test_voice(
        "te-IN-ShrutiNeural",
        "Namaskaram! Nenu Priya ni, TZMICHA Technologies nundi call chesthunnanu. Meeru ela unnaru?",
        "TELUGU - Shruti (Female, Pure Telugu)"
    )
    
    input("\n    Press Enter for next voice...")

    # 2. Hindi Female - Swara
    await test_voice(
        "hi-IN-SwaraNeural",
        "Namaste! Main Priya bol rahi hoon, TZMICHA Technologies se. Aap kaise hain? Kya main aapki kuch help kar sakti hoon?",
        "HINDI - Swara (Female, Pure Hindi)"
    )
    
    input("\n    Press Enter for next voice...")

    # 3. Indian English Female - Neerja
    await test_voice(
        "en-IN-NeerjaExpressiveNeural",
        "Hey! This is Priya from TZMICHA Technologies. So basically, we build AI voice agents that sound like real people. Pretty cool, right?",
        "INDIAN ENGLISH - Neerja Expressive (Female, Indian Accent)"
    )
    
    input("\n    Press Enter for next voice...")

    # 4. British English Female - Sonia
    await test_voice(
        "en-GB-SoniaNeural",
        "Hello! This is Priya from TZMICHA Technologies. We offer quite brilliant AI voice solutions. Shall I tell you more about it?",
        "BRITISH ENGLISH - Sonia (Female, British)"
    )

    print(f"\n\n    ✅ All 4 voices tested!")
    print(f"    ─────────────────────────────────")
    print(f"    Telugu:   te-IN-ShrutiNeural")
    print(f"    Hindi:    hi-IN-SwaraNeural")
    print(f"    English:  en-IN-NeerjaExpressiveNeural")
    print(f"    British:  en-GB-SoniaNeural")
    print(f"    ─────────────────────────────────")
    print(f"    ALL FREE. No limits. No API key.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
