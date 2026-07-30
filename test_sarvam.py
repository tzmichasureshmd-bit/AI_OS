"""
Test Sarvam AI - PURE Telugu/Hindi voice
Native Indian pronunciation. Built for Indian languages.
"""
import os
import time
import ctypes
from sarvamai import SarvamAI
from sarvamai.play import play, save

SARVAM_KEY = "sk_qhw027f8_mihfH0NToycAnbxI4sASGHMi"

client = SarvamAI(api_subscription_key=SARVAM_KEY)


def play_full(filepath: str):
    """Play audio completely using Windows MCI."""
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


def test_voice(text, language, speaker, label, pace=1.2):
    print(f"\n    🔊 {label}")
    print(f"    🎤 Speaker: {speaker} | Language: {language} | Pace: {pace}")
    print(f"    📝 {text}")
    
    try:
        response = client.text_to_speech.convert(
            text=text,
            target_language_code=language,
            model="bulbul:v3",
            speaker=speaker,
            pace=pace,
        )
        
        output = os.path.abspath("_sarvam_test.wav")
        save(response, output)
        print(f"    ▶️  Playing...", flush=True)
        play_full(output)
        
        try:
            os.unlink(output)
        except:
            pass
    except Exception as e:
        print(f"    ❌ Error: {e}")


def main():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║   SARVAM AI - Pure Indian Voice Test             ║
    ║   Telugu | Hindi | Indian English                ║
    ║   Native pronunciation. Built for India.         ║
    ╚══════════════════════════════════════════════════╝
    """)

    # 1. Telugu - priya (Female)
    test_voice(
        "నమస్కారం! నేను ప్రియ ని, TZMICHA Technologies నుండి call చేస్తున్నాను. మీరు ఎలా ఉన్నారు? Fee అంటే yearly ఒక లక్ష ఇరవై వేలు ఉంటుంది. Transport separate గా ఉంటుంది.",
        "te-IN",
        "priya",
        "TELUGU - priya (Pure Telugu Female)",
        pace=1.2
    )

    input("\n    Press Enter for next...")

    # 2. Telugu - kavitha (Another female voice)
    test_voice(
        "హాయ్! మీకు ఏమైనా doubts ఉంటే నన్ను అడగండి. మా services చాలా బాగుంటాయి. Monthly 5000 నుండి start అవుతుంది.",
        "te-IN",
        "kavitha",
        "TELUGU - kavitha (Another Female Voice)",
        pace=1.3
    )

    input("\n    Press Enter for another Telugu voice...")

    # 2b. Telugu - shruti
    test_voice(
        "హలో! నేను TZMICHA నుండి call చేస్తున్నాను. మీకు AI voice agents గురించి చెప్పాలని. ఒక్క నిమిషం time ఉందా?",
        "te-IN",
        "shruti",
        "TELUGU - shruti (Female)",
        pace=1.2
    )

    input("\n    Press Enter for Hindi...")

    # 3. Hindi - neha (Female)
    test_voice(
        "नमस्ते! मैं प्रिया बोल रही हूँ TZMICHA Technologies से। हमारी AI voice service basically आपके लिए calls handle करती है। Monthly 5000 से start होता है।",
        "hi-IN",
        "neha",
        "HINDI - neha (Female, Natural Hindi)",
        pace=1.2
    )

    input("\n    Press Enter for Indian English...")

    # 4. Indian English - shreya
    test_voice(
        "Hey! This is Priya from TZMICHA Technologies. So basically, we build AI voice agents that sound like real people. Starts from 5000 a month. Want me to explain more?",
        "en-IN",
        "shreya",
        "INDIAN ENGLISH - shreya (Female, Indian Accent)",
        pace=1.2
    )

    input("\n    Press Enter for fast Telugu...")

    # 5. Telugu - Fast pace (like real phone call)
    test_voice(
        "హాయ్! నేను ప్రియ ని. So basically, మా company AI voice agents build చేస్తుంది. Like, customer call చేస్తే AI pick up చేస్తుంది. Real person లాగా మాట్లాడుతుంది.",
        "te-IN",
        "priya",
        "TELUGU - priya (FAST - like real phone call)",
        pace=1.5
    )

    print(f"\n\n    ✅ DONE!")
    print(f"    ─────────────────────────────")
    print(f"    Sarvam voices for our agent:")
    print(f"    Telugu:  Priya / Kavitha")
    print(f"    Hindi:   Neha / Shreya")
    print(f"    English: Shreya")
    print(f"    ─────────────────────────────")
    print(f"    Pure Indian pronunciation!")
    print()


if __name__ == "__main__":
    main()
