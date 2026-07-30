"""
Quick Voice Test - Plays 5 best voices automatically
No interaction needed. Just run and listen.

Run: py quick_voice_test.py
"""
import os
import time
import ctypes
from sarvamai import SarvamAI
from sarvamai.play import save

SARVAM_KEY = "sk_qhw027f8_mihfH0NToycAnbxI4sASGHMi"
client = SarvamAI(api_subscription_key=SARVAM_KEY)


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
        total_ms = int(length_str) if length_str.isdigit() else 8000
        mci("play tz from 0")
        elapsed = 0
        while elapsed < total_ms + 500:
            time.sleep(0.2)
            elapsed += 200
            pos = mci("status tz position")
            if pos.isdigit() and int(pos) >= total_ms - 100:
                break
        time.sleep(0.5)
        mci("close tz")
    except Exception:
        os.startfile(filepath)
        time.sleep(5)


# Top 5 voices to demo
DEMO_VOICES = [
    {
        "name": "suhani",
        "label": "SUHANI (Telugu Female) - Our Primary Voice",
        "text": "హాయ్! నేను Suhani ని, misha Technologies నుంచి call చేస్తున్నా. మీకు ఒక exciting offer ఉంది, ఒక్క నిమిషం free గా ఉన్నారా?",
        "lang": "te-IN"
    },
    {
        "name": "kavitha",
        "label": "KAVITHA (Hindi Female) - Hindi Voice",
        "text": "हाय! मैं Kavitha हूँ, misha Technologies से बात कर रही हूँ। आपके लिए एक special offer है, क्या आप एक minute बात कर सकते हैं?",
        "lang": "hi-IN"
    },
    {
        "name": "shreya",
        "label": "SHREYA (English Female) - English Voice",
        "text": "Hey! This is Shreya from misha Technologies. I have something really exciting to share with you, do you have a quick minute?",
        "lang": "en-IN"
    },
    {
        "name": "aditya",
        "label": "ADITYA (Hindi Male) - Male Voice",
        "text": "हेलो! मैं Aditya बोल रहा हूँ, misha Technologies से। आपके business के लिए एक AI solution है, सुनेंगे?",
        "lang": "hi-IN"
    },
    {
        "name": "rahul",
        "label": "RAHUL (Telugu Male) - Telugu Male Voice",
        "text": "హాయ్! నేను Rahul ని, misha Technologies నుంచి call చేస్తున్నా. మీ business కోసం ఒక AI solution ఉంది, వినగలరా?",
        "lang": "te-IN"
    },
]


def main():
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║   TZMICHA AI - QUICK VOICE TEST (5 Best Voices)     ║
    ╠══════════════════════════════════════════════════════╣
    ║   Sit back and listen! Each voice plays auto.        ║
    ║   Volume UP!                                         ║
    ╚══════════════════════════════════════════════════════╝
    """)

    time.sleep(1)

    for i, voice in enumerate(DEMO_VOICES):
        print(f"    ─────────────────────────────────────────────")
        print(f"    [{i+1}/5] {voice['label']}")
        print(f"    Text: \"{voice['text'][:60]}...\"")
        print(f"    Playing...", flush=True)

        try:
            response = client.text_to_speech.convert(
                text=voice["text"],
                target_language_code=voice["lang"],
                model="bulbul:v3",
                speaker=voice["name"],
                pace=1.2,
            )

            output = os.path.abspath("_quick_test.wav")
            save(response, output)
            play_full(output)

            try:
                os.unlink(output)
            except:
                pass

            print(f"    Done!")

        except Exception as e:
            print(f"    ERROR: {str(e)[:100]}")

        # Small gap between voices
        time.sleep(1)
        print()

    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║   ALL 5 VOICES PLAYED!                               ║
    ╠══════════════════════════════════════════════════════╣
    ║   Suhani  → Telugu Female (Primary)                  ║
    ║   Kavitha → Hindi Female                             ║
    ║   Shreya  → English Female                           ║
    ║   Aditya  → Hindi Male                               ║
    ║   Rahul   → Telugu Male                              ║
    ╠══════════════════════════════════════════════════════╣
    ║   These are REAL AI voices, not robotic TTS!         ║
    ║   Sounds like actual humans on a phone call.         ║
    ╚══════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
