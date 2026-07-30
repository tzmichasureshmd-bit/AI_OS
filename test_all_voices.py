"""
Sarvam AI - Listen to ALL voices
37 voices total. Hear each one and pick your favorite.
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
        time.sleep(0.3)
        mci("close tz")
    except Exception:
        os.startfile(filepath)
        time.sleep(5)


# ALL 37 voices available in bulbul:v3
ALL_VOICES = [
    # FEMALE voices
    {"name": "priya", "gender": "Female"},
    {"name": "neha", "gender": "Female"},
    {"name": "kavitha", "gender": "Female"},
    {"name": "ritu", "gender": "Female"},
    {"name": "shreya", "gender": "Female"},
    {"name": "ishita", "gender": "Female"},
    {"name": "simran", "gender": "Female"},
    {"name": "kavya", "gender": "Female"},
    {"name": "pooja", "gender": "Female"},
    {"name": "roopa", "gender": "Female"},
    {"name": "tanya", "gender": "Female"},
    {"name": "shruti", "gender": "Female"},
    {"name": "suhani", "gender": "Female"},
    {"name": "rupali", "gender": "Female"},
    {"name": "niharika", "gender": "Female"},
    # MALE voices
    {"name": "aditya", "gender": "Male"},
    {"name": "rahul", "gender": "Male"},
    {"name": "rohan", "gender": "Male"},
    {"name": "amit", "gender": "Male"},
    {"name": "dev", "gender": "Male"},
    {"name": "ratan", "gender": "Male"},
    {"name": "varun", "gender": "Male"},
    {"name": "manan", "gender": "Male"},
    {"name": "sumit", "gender": "Male"},
    {"name": "kabir", "gender": "Male"},
    {"name": "aayan", "gender": "Male"},
    {"name": "shubh", "gender": "Male"},
    {"name": "ashutosh", "gender": "Male"},
    {"name": "advait", "gender": "Male"},
    {"name": "anand", "gender": "Male"},
    {"name": "tarun", "gender": "Male"},
    {"name": "sunny", "gender": "Male"},
    {"name": "mani", "gender": "Male"},
    {"name": "gokul", "gender": "Male"},
    {"name": "vijay", "gender": "Male"},
    {"name": "mohit", "gender": "Male"},
    {"name": "rehan", "gender": "Male"},
    {"name": "soham", "gender": "Male"},
]

# Test text in Telugu - natural phone call opening
# Each voice will say its OWN name
TELUGU_TEXT_TEMPLATE = "హాయ్! నా పేరు {name}, నేను misSha IT SOLUTION  company నుంచి call చేస్తున్నా. మీతో ఒక్క నిమిషం మాట్లాడవచ్చా? free గా ఉన్నారా?"


def main():
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║   SARVAM AI - ALL VOICES ({len(ALL_VOICES)} total)              ║
    ║   15 Female + 22 Male                            ║
    ║   Listen and pick your favorite!                 ║
    ╚══════════════════════════════════════════════════╝

    FEMALE VOICES (15):
    priya, neha, kavitha, ritu, shreya, ishita,
    simran, kavya, pooja, roopa, tanya, shruti,
    suhani, rupali, niharika

    MALE VOICES (22):
    aditya, rahul, rohan, amit, dev, ratan, varun,
    manan, sumit, kabir, aayan, shubh, ashutosh,
    advait, anand, tarun, sunny, mani, gokul, vijay,
    mohit, rehan, soham
    """)

    print("    OPTIONS:")
    print("    1. Listen to ALL FEMALE voices")
    print("    2. Listen to ALL MALE voices")
    print("    3. Listen to ALL voices")
    print("    4. Listen to specific voice (type name)")
    print()

    choice = input("    Enter choice (1/2/3/4): ").strip()

    if choice == "1":
        voices = [v for v in ALL_VOICES if v["gender"] == "Female"]
    elif choice == "2":
        voices = [v for v in ALL_VOICES if v["gender"] == "Male"]
    elif choice == "3":
        voices = ALL_VOICES
    elif choice == "4":
        name = input("    Enter voice name: ").strip().lower()
        voices = [{"name": name, "gender": "?"}]
    else:
        voices = [v for v in ALL_VOICES if v["gender"] == "Female"]

    print(f"\n    Playing {len(voices)} voices in Telugu...\n")

    for i, voice in enumerate(voices):
        print(f"    [{i+1}/{len(voices)}] 🔊 {voice['name'].upper()} ({voice['gender']})")
        
        try:
            # Each voice says its own name
            text = TELUGU_TEXT_TEMPLATE.format(name=voice["name"])
            response = client.text_to_speech.convert(
                text=text,
                target_language_code="te-IN",
                model="bulbul:v3",
                speaker=voice["name"],
                pace=1.2,
            )
            
            output = os.path.abspath("_voice_test.wav")
            save(response, output)
            play_full(output)
            
            try:
                os.unlink(output)
            except:
                pass

        except Exception as e:
            print(f"    ❌ Error: {str(e)[:80]}")

        # Ask to continue or skip
        action = input(f"    [Enter=next | 's'=star this voice | 'q'=quit]: ").strip().lower()
        if action == 'q':
            break
        elif action == 's':
            print(f"    ⭐ STARRED: {voice['name']}")
        print()

    print(f"\n    ✅ Done! Tell me which voice you liked best.")


if __name__ == "__main__":
    main()
