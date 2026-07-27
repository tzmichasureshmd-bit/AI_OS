"""
TZMICHA AI OS - Real Voice Agent (Exotel + Sarvam AI)
Answers REAL phone calls with AI voice.

SETUP:
1. ngrok running: ngrok http 7860
2. Copy ngrok URL to Exotel Voicebot Applet (wss://xxx.ngrok.io/ws)
3. Call your Exotel number: 09513886363

RUN:
  py real_agent.py --transport exotel
"""

import os
from dotenv import load_dotenv
from loguru import logger
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.sarvam.stt import SarvamSTTService
from pipecat.services.sarvam.tts import SarvamTTSService
from pipecat.services.sarvam.llm import SarvamLLMService
from pipecat.transports.websocket.fastapi import FastAPIWebsocketParams

load_dotenv(override=True)


async def bot(runner_args: RunnerArguments):
    """TZMICHA AI Voice Agent - Answers phone calls like a real person."""

    # Create transport (auto-detects Exotel WebSocket)
    transport = await create_transport(
        runner_args,
        {
            "exotel": lambda: FastAPIWebsocketParams(
                audio_in_enabled=True, audio_out_enabled=True
            ),
        },
    )

    # === AI EARS (Speech-to-Text) - Auto-detect language ===
    stt = SarvamSTTService(
        api_key=os.getenv("SARVAM_API_KEY"),
        settings=SarvamSTTService.Settings(
            model="saaras:v3",
            language="unknown",  # Auto-detect Telugu/Hindi/English
        ),
        mode="transcribe",
    )

    # === AI MOUTH (Text-to-Speech) - Suhani voice, Telugu ===
    tts = SarvamTTSService(
        api_key=os.getenv("SARVAM_API_KEY"),
        settings=SarvamTTSService.Settings(
            model="bulbul:v3",
            voice="suhani",
            language="te-IN",
            pace=1.3,
        ),
    )

    # === AI BRAIN (LLM) - Sarvam 105B ===
    llm = SarvamLLMService(
        api_key=os.getenv("SARVAM_API_KEY"),
        settings=SarvamLLMService.Settings(model="sarvam-105b"),
    )

    # === CONVERSATION CONTEXT ===
    messages = [
        {
            "role": "system",
            "content": """You are Priya, a real Indian girl working at misha Technologies. You're ON A PHONE CALL.

RULES:
- Talk like a REAL person on phone. Short, natural, casual.
- MAX 2 sentences per response. ALWAYS complete the sentence.
- Write Telugu words in TELUGU SCRIPT (తెలుగు). English words in English.
- Example: "హాయ్! fee అంటే 5000 per month ఉంటుంది."
- Use fillers: "hmm...", "so...", "actually..."
- If customer speaks Telugu → respond in Telugu script
- If customer speaks Hindi → respond in Hindi (Devanagari)
- If customer speaks English → respond in English
- Auto-detect and switch language immediately
- Never sound like AI. Never say "How can I assist you?"
- Be warm, friendly, casual. Like talking to a friend.

COMPANY INFO (use only when asked):
misha Technologies - AI voice solutions
Price: 5000/month
Location: Hyderabad, India
What: AI that makes and answers calls like a real employee

You are Priya. Be real. Be human.""",
        },
    ]

    context = LLMContext(messages)
    context_aggregator = LLMContextAggregatorPair(context)

    # === BUILD PIPELINE ===
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            context_aggregator.user(),
            llm,
            tts,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    # Exotel streams 8kHz mono audio
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("📞 Caller connected!")
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("📴 Caller disconnected")

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


if __name__ == "__main__":
    from pipecat.runner.run import main

    print("""
    ╔══════════════════════════════════════════════════╗
    ║   TZMICHA AI OS - Real Voice Agent               ║
    ║   Exotel + Sarvam AI (Telugu/Hindi/English)      ║
    ╠══════════════════════════════════════════════════╣
    ║   Voice: Suhani | Language: Auto-detect          ║
    ║   Company: misha Technologies                    ║
    ╠══════════════════════════════════════════════════╣
    ║   SETUP:                                         ║
    ║   1. Run: ngrok http 7860                        ║
    ║   2. Copy ngrok wss:// URL to Exotel Voicebot    ║
    ║   3. Call: 09513886363                            ║
    ╚══════════════════════════════════════════════════╝
    """)

    main()
