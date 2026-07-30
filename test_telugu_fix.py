"""
Fix Telugu pronunciation.
Edge TTS Telugu voice needs TELUGU SCRIPT (not English letters).
When we write in Telugu script, pronunciation is PERFECT.
"""
import asyncio
import edge_tts
import os
import time
import ctypes


def play_full(filepath: str):
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


async def test(voice, text, label, rate="+15%"):
    print(f"\n    🔊 {label}")
    print(f"    📝 {text}")
    output = os.path.join(os.path.expanduser("~"), "_test_te.mp3")
    communicate = edge_tts.Communicate(text, voice, rate=rate)
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
    ║   TELUGU PRONUNCIATION TEST                      ║
    ║   Telugu Script vs English Letters               ║
    ╚══════════════════════════════════════════════════╝
    """)

    # BAD: English letters (wrong pronunciation)
    print("    ═══ TEST 1: English letters (WRONG pronunciation) ═══")
    await test(
        "te-IN-ShrutiNeural",
        "Namaskaram! Nenu Priya ni. Fee ante yearly one lakh twenty thousand untundi. Transport separate ga untundi.",
        "Latin script (will mispronounce)",
        rate="+15%"
    )

    input("\n    Press Enter for correct version...")

    # GOOD: Telugu script (PERFECT pronunciation)
    print("\n    ═══ TEST 2: Telugu script (PERFECT pronunciation) ═══")
    await test(
        "te-IN-ShrutiNeural",
        "నమస్కారం! నేను ప్రియ ని. ఫీ అంటే yearly one lakh twenty thousand ఉంటుంది. Transport separate గా ఉంటుంది.",
        "Telugu script (pure Telugu sound)",
        rate="+15%"
    )

    input("\n    Press Enter for natural conversation style...")

    # BEST: Mix Telugu script + English words naturally
    print("\n    ═══ TEST 3: Natural Tenglish (Telugu script + English) ═══")
    await test(
        "te-IN-ShrutiNeural",
        "హాయ్! నేను ప్రియ ని, TZMICHA Technologies నుండి call చేస్తున్నాను. మీరు ఎలా ఉన్నారు?",
        "Natural Tenglish (BEST - Telugu + English mix)",
        rate="+18%"
    )

    input("\n    Press Enter for Hindi test...")

    # Hindi script test
    print("\n    ═══ TEST 4: Hindi (Devanagari script) ═══")
    await test(
        "hi-IN-SwaraNeural",
        "नमस्ते! मैं प्रिया बोल रही हूँ, TZMICHA Technologies से। आप कैसे हैं? क्या मैं आपकी help कर सकती हूँ?",
        "Hindi Devanagari (perfect Hindi pronunciation)",
        rate="+15%"
    )

    input("\n    Press Enter for Indian English...")

    # Indian English
    print("\n    ═══ TEST 5: Indian English (Neerja) ═══")
    await test(
        "en-IN-NeerjaExpressiveNeural",
        "Hey! So basically we do AI voice agents. Like, your AI picks up calls automatically. Pretty cool right?",
        "Indian English (natural, fast)",
        rate="+20%"
    )

    print(f"\n\n    ✅ RESULTS:")
    print(f"    ─────────────────────────────────")
    print(f"    Telugu: USE TELUGU SCRIPT (తెలుగు) for perfect pronunciation")
    print(f"    Hindi: USE HINDI SCRIPT (हिंदी) for perfect pronunciation")  
    print(f"    English: Latin letters work fine")
    print(f"    ─────────────────────────────────")
    print(f"    SOLUTION: LLM will generate Telugu/Hindi in native script!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
