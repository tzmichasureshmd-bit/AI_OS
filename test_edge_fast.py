"""
Test Edge TTS - FASTER speed (like real human on phone)
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


async def test(voice, text, label, rate="+15%", pitch="+0Hz"):
    print(f"\n    🔊 {label} (Rate: {rate})")
    print(f"    📝 \"{text}\"")
    output = "_test_fast.mp3"
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
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
    ║   SPEED TEST - Finding the perfect pace         ║
    ║   Same voice, different speeds                  ║
    ╚══════════════════════════════════════════════════╝
    """)

    text_te = "Namaskaram! Nenu Priya ni. Fee ante yearly one lakh twenty thousand untundi. Transport separate ga untundi."
    text_en = "Hey! So basically we do AI voice agents. It's like, your AI picks up calls automatically. Starts from 5000 a month."

    # Telugu - 3 speeds
    print("    ═══ TELUGU (Shruti) ═══")
    
    await test("te-IN-ShrutiNeural", text_te, "Normal speed", rate="+0%")
    input("    Press Enter for faster...")
    
    await test("te-IN-ShrutiNeural", text_te, "Slightly fast (natural phone)", rate="+18%")
    input("    Press Enter for even faster...")
    
    await test("te-IN-ShrutiNeural", text_te, "Fast (energetic)", rate="+30%")
    
    input("\n    Press Enter for English tests...")

    # English - 3 speeds
    print("\n    ═══ INDIAN ENGLISH (Neerja) ═══")
    
    await test("en-IN-NeerjaExpressiveNeural", text_en, "Normal speed", rate="+0%")
    input("    Press Enter for faster...")
    
    await test("en-IN-NeerjaExpressiveNeural", text_en, "Slightly fast (natural phone)", rate="+18%")
    input("    Press Enter for even faster...")
    
    await test("en-IN-NeerjaExpressiveNeural", text_en, "Fast (energetic)", rate="+30%")

    print(f"\n\n    Which speed felt most natural?")
    print(f"    +0%  = Slow/formal")
    print(f"    +18% = Natural phone call")
    print(f"    +30% = Energetic/quick")
    print()


if __name__ == "__main__":
    asyncio.run(main())
