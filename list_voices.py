import edge_tts
import asyncio

async def main():
    voices = await edge_tts.list_voices()
    
    print("TELUGU VOICES:")
    for v in voices:
        if "te-IN" in v["ShortName"]:
            print(f"  {v['ShortName']:35} | {v['Gender']:8} | {v.get('FriendlyName','')}")
    
    print("\nHINDI VOICES:")
    for v in voices:
        if "hi-IN" in v["ShortName"]:
            print(f"  {v['ShortName']:35} | {v['Gender']:8} | {v.get('FriendlyName','')}")
    
    print("\nINDIAN ENGLISH VOICES:")
    for v in voices:
        if "en-IN" in v["ShortName"]:
            print(f"  {v['ShortName']:35} | {v['Gender']:8} | {v.get('FriendlyName','')}")
    
    print("\nBRITISH FEMALE VOICES:")
    for v in voices:
        if "en-GB" in v["ShortName"] and "Female" in v["Gender"]:
            print(f"  {v['ShortName']:35} | {v['Gender']:8} | {v.get('FriendlyName','')}")

asyncio.run(main())
