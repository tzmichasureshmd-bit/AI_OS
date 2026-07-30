import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def get_voices():
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": os.getenv("ELEVENLABS_API_KEY")},
            timeout=10,
        )
        if r.status_code == 200:
            voices = r.json().get("voices", [])
            print(f"\nAvailable voices for YOUR account ({len(voices)}):\n")
            for v in voices[:20]:
                labels = v.get("labels", {})
                accent = labels.get("accent", "")
                gender = labels.get("gender", "")
                print(f"  {v['name']:20} | ID: {v['voice_id']} | {accent} {gender}")
            print(f"\n  Use any of these Voice IDs in .env")
        else:
            print(f"Error: {r.status_code} - {r.text[:300]}")

asyncio.run(get_voices())
